"""Reuse engine and cost accounting; every period is exploratory."""
import hashlib
import json
from datetime import datetime, timezone
import evaluate_research as engine


def main():
    engine.OUT = engine.ROOT / "data/research/discord_exploratory"
    engine.STRATEGIES = ["SweepConfirm", "SweepTrendConfirm"]
    engine.OUT.mkdir(parents=True, exist_ok=True)
    if (engine.OUT / "summary.json").exists():
        raise SystemExit("Completed screen exists; preserve results.")
    config = json.loads((engine.ROOT / "config.research.json").read_text())
    assert config["dry_run"] and not config["exchange"].get("key") and not config["exchange"].get("secret")
    hashes = {p: hashlib.sha256((engine.ROOT / p).read_bytes()).hexdigest() for p in
              ["DISCORD_EXPERIMENT.md", "user_data/strategies/discord_proxies.py", "config.research.json"]}
    (engine.OUT / "frozen_inputs.json").write_text(json.dumps(hashes, indent=2))
    results = {f"{period}_{cost}": engine.run(period, cost)
               for period in engine.PERIODS for cost in engine.COSTS}
    summary = {"completed_at": datetime.now(timezone.utc).isoformat(),
               "status": "exploratory_only_no_promotion", "hashes": hashes,
               "warning": "All historical periods previously inspected; no untouched holdout.",
               "results": results}
    (engine.OUT / "summary.json").write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
