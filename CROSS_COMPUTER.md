# Continue on another computer

Repository: https://github.com/jaysonheathcote127-oss/ai-crypto-bot

The user chose the existing repository, which is currently public, and intends to change visibility later. Existing GitHub history is preserved alongside this folder's local checkpoint. Initial upload completed on 19 October 2026; GitHub main was updated to 10d8cad. Subsequent documentation commits may follow.

## First setup on each computer

Install Git, authenticate to the same GitHub account (GitHub CLI: `gh auth login`, then `gh auth setup-git`), and clone:

```sh
git clone https://github.com/jaysonheathcote127-oss/ai-crypto-bot.git
cd ai-crypto-bot
```

Open the cloned folder as the Codex project. Tell the new chat: “Read AGENTS.md, memory/PROJECT_MEMORY.md and the latest memory/CONVERSATION_LOG.md, inspect GitHub status, and continue the recorded work. Keep GitHub updated.”

## Every time you switch computers

Before working, check `git status`, then `git pull --ff-only` with a clean working tree. Before switching away, save files, update memory, inspect `git diff` and `git status`, commit the intended changes and run `git push`. Confirm the latest commit appears on GitHub. If pull fails because both computers changed files, preserve both sets of edits and resolve the divergence; do not force-push or reset. Prefer one active editing computer at a time.

AGENTS.md instructs future agents to commit and push completed work without asking again. This is a workflow instruction, not a background synchronization service. It depends on working credentials/network and agents following the instructions. Failed pushes must be reported.

## What is included

Research code, reports, protocols, memory and work logs, handoff notes, frozen datasets, JSON observation snapshots, result archives and original GitHub source under crypto-bot-public-source/. The working research is under ai-crypto-bot/freqtrade-trial/. Existing repository commits and the new local research checkpoint are preserved. There was no older Git history for this research folder before setup; recorded logs and archived experiment files provide earlier context. Full chat transcripts are not available as files and are not claimed to be included.

Excluded: credentials, ignored SQLite files/journals, environments, caches and machine logs except retained research run.log files. Inspect `git status --ignored` if an expected artifact is missing. The original .venv is an external absolute link; it cannot run on another computer. Create a supported environment and install requirements-research.txt (Windows setup untested). External BTC services, account sessions and running processes do not transfer.

Do not put new credentials into this public repository. The user intends to make it private through GitHub settings later.

## Authentication on the original Mac

The initial upload used an official GitHub CLI device login from a temporary installation. No authentication files were copied into the project or committed. For durable setup, install GitHub CLI normally and run `gh auth login` and `gh auth setup-git` on each computer. The temporary login used during initial setup is not a portable or guaranteed persistent configuration.
