# Continue from another computer using GitHub

Updated 19 October 2026. User prefers keeping the project online via GitHub,
without a remote connection between computers.

## Current setup

- Git repository initialized locally, branch main.
- Prepared code, protocols, memory, reports, datasets and research result archives
  for a PRIVATE repository. Nothing uploaded or remotely synchronized yet.
- GitHub integration offered but installation/account connection not confirmed.
- GitHub CLI is not installed. No account owner or repository URL selected.
- Existing source resources came from public third-party repositories; they are
  not a GitHub account owned by the assistant or the user.
- No file exceeds 10 MB in the checked workspace (~135 MB total). Research data
  is deliberately included; venvs, caches, SQLite journals and credential-file
  patterns are excluded. SQLite history is represented by retained JSON snapshots.
- A credential-pattern/config scan found no potential matches. This is a limited
  local check, not a guarantee that every private source note is publishable.
  Keep the repository PRIVATE.

## Normal handoff workflow

1. Save work, update memory, commit and push before switching computers.
2. Clone the private repository once on the other PC; thereafter pull before work.
3. Open that folder as the project. Ask Codex to read AGENTS.md and
   memory/PROJECT_MEMORY.md, then inspect the latest log/status before continuing.
4. Commit and push the other computer's updates before returning here.

GitHub shares committed files and project notes; local chat history, credentials,
Python environments and running processes are separate. GitHub does not
continuously upload unsaved/uncommitted work. Use one active editing copy at a
time, or separate branches for intentional parallel changes.

The original .venv is an absolute symlink outside this project and is ignored.
Create a separate supported Python environment on each machine; the direct
package versions are recorded in requirements-research.txt. This manifest is
preparation, not proof of a working Windows installation. The original BTC
service/runtime outside this research folder is not included.

## Optional browser-based execution

For working without a local runtime, Codex Cloud can use a prepared GitHub-backed
environment. Local files do not transfer automatically; dependencies/data must
be made available and the environment tested. Each cloud task has its own working
files, so commit changes to carry them into later tasks.

Official guidance:
https://learn.chatgpt.com/docs/cloud
https://learn.chatgpt.com/docs/environments/modes

No private remote repository has been created and no upload/automatic push has
been configured by this preparation. Complete GitHub installation/sign-in first.
