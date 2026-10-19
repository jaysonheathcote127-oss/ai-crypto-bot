"""Execute the frozen research plan and keep validation selection before holdout."""
import hashlib
import io
import json
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data/research/evaluation_exclusive_boundaries"
STRATEGIES = ["TrendBaseline", "MomentumBaseline", "ReversionBaseline"]
PERIODS = {"development": "20241001-20251001", "validation": "20251001-20260401", "holdout": "20260401-20261019"}
COSTS = {"base": .0015, "stress": .0045}


def engine_timerange(timerange):
    # Freqtrade includes its stop candle. Keep the protocol's segment end exclusive.
    start, end = timerange.split("-")
    last_candle = pd.Timestamp(end, tz="UTC") - pd.Timedelta(hours=4)
    return start + "-" + last_candle.strftime("%Y%m%dT%H%M")


def drawdown(values):
    series = pd.concat([pd.Series([1000.]), values.reset_index(drop=True)], ignore_index=True)
    return float((1 - series / series.cummax()).max())


def run(period, cost):
    folder = OUT / f"{period}_{cost}"
    folder.mkdir(parents=True, exist_ok=True)
    command = [str(ROOT / ".venv/bin/freqtrade"), "backtesting", "-c", "config.research.json",
               "--userdir", "user_data", "--strategy-list", *STRATEGIES,
               "--timerange", engine_timerange(PERIODS[period]), "--fee", str(COSTS[cost]), "--cache", "none",
               "--backtest-directory", str(folder), "--no-color"]
    print("Running", period, cost, flush=True)
    with (folder / "run.log").open("w") as log:
        subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    archive = sorted(folder.glob("*.zip"))[-1]
    results = {}
    with zipfile.ZipFile(archive) as z:
        data = next(json.loads(z.read(n)) for n in z.namelist()
                    if n.endswith(".json") and "_config" not in n)
        for name in STRATEGIES:
            stats = data["strategy"][name]
            wallet_name = next(n for n in z.namelist() if n.endswith(f"_{name}_wallet.feather"))
            wallet = pd.read_feather(io.BytesIO(z.read(wallet_name)))
            equity = wallet.groupby("date").total_quote.sum()
            results[name] = {
                "return_pct": stats["profit_total"] * 100,
                "profit": stats["profit_total_abs"], "final_balance": stats["final_balance"],
                "trades": stats["total_trades"],
                "closed_trade_drawdown_pct": stats["max_drawdown_account"] * 100,
                "marked_wallet_drawdown_pct": drawdown(equity) * 100,
                "start": stats["backtest_start"], "end": stats["backtest_end"],
                "force_exits": sum(t.get("exit_reason") == "force_exit" for t in stats["trades"]),
                "source_archive": str(archive.relative_to(ROOT)),
            }
            print(name, results[name], flush=True)
    return results


def benchmarks(config):
    pairs = config["exchange"]["pair_whitelist"]
    result = {}
    for period, timerange in PERIODS.items():
        start, end = [pd.Timestamp(x, tz="UTC") for x in (timerange[:8], timerange[9:])]
        frames = {p: pd.read_feather(ROOT / "user_data/data/okx" / (p.replace("/", "_") + "-4h.feather"))
                  for p in pairs}
        frames = {p: f[(f.date >= start) & (f.date < end)].set_index("date") for p, f in frames.items()}
        for cost, fee in COSTS.items():
            items = {"cash": {"return_pct": 0., "marked_wallet_drawdown_pct": 0.}}
            for name, chosen in [("BTC_hold", ["BTC/USDT"]), ("equal_weight_hold", pairs)]:
                for fraction in (.5, 1.):
                    allocated = 1000 * fraction / len(chosen)
                    values = []
                    for pair in chosen:
                        frame = frames[pair]
                        value = allocated / (frame.open.iloc[0] * (1 + fee)) * frame.close
                        value = value.copy()
                        value.iloc[-1] *= 1 - fee
                        values.append(value)
                    equity = pd.concat(values, axis=1).sum(axis=1) + 1000 * (1 - fraction)
                    items[f"{name}_{int(fraction*100)}pct"] = {
                        "return_pct": (float(equity.iloc[-1]) / 1000 - 1) * 100,
                        "marked_wallet_drawdown_pct": drawdown(equity) * 100,
                    }
            result[f"{period}_{cost}"] = items
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT / "summary.json").exists():
        raise SystemExit("Completed research exists. Preserve it; use a new protocol for further experiments.")
    config = json.loads((ROOT / "config.research.json").read_text())
    if config["dry_run"] is not True or config["exchange"].get("key") or config["exchange"].get("secret"):
        raise ValueError("Only credential-free paper research is allowed")
    hashes = {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in
              ["RESEARCH_PLAN.md", "config.research.json", "user_data/strategies/research_baselines.py"]}
    (OUT / "frozen_inputs.json").write_text(json.dumps(hashes, indent=2))
    results = {}
    for period in ("development", "validation"):
        for cost in COSTS:
            results[f"{period}_{cost}"] = run(period, cost)
    passing = []
    for strategy in STRATEGIES:
        base, stress = results["validation_base"][strategy], results["validation_stress"][strategy]
        if (base["return_pct"] > 0 and base["trades"] >= 30
                and max(base["marked_wallet_drawdown_pct"], stress["marked_wallet_drawdown_pct"]) <= 15
                and stress["return_pct"] > 0):
            passing.append(strategy)
    selected = max(passing, key=lambda s: results["validation_base"][s]["return_pct"]) if passing else None
    decision = {"chosen_before_holdout": selected, "validation_candidates": passing,
                "recorded_at": datetime.now(timezone.utc).isoformat(),
                "criteria": "Positive validation after both costs, >=30 trades at base cost, marked-wallet drawdown <=15% at both costs"}
    (OUT / "selection_before_holdout.json").write_text(json.dumps(decision, indent=2))
    print("Locked selection before holdout:", selected, flush=True)
    for cost in COSTS:
        results[f"holdout_{cost}"] = run("holdout", cost)
    holdout_pass = selected is not None and all(
        results[f"holdout_{cost}"][selected]["return_pct"] > 0
        and results[f"holdout_{cost}"][selected]["marked_wallet_drawdown_pct"] <= 15
        for cost in COSTS)
    summary = {"completed_at": datetime.now(timezone.utc).isoformat(), "hashes": hashes,
               "selection": decision, "holdout_performance_gate_passed": holdout_pass,
               "results": results, "benchmarks": benchmarks(config),
               "limitations": ["Today's membership and liquidity cause historical selection bias.",
                               "Cost proxy is not an actual slippage model; no intrabar fill validation.",
                               "USDT dollar peg assumed. Current exchange minimums/precision used historically.",
                               "No automatic promotion. Causality/lookahead/startup checks also required."]}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    print("Performance gate passed:", holdout_pass, flush=True)


if __name__ == "__main__":
    main()
