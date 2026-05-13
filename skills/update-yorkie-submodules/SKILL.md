---
name: update-yorkie-submodules
description: Update and verify the Yorkie community repository's projects/* Git submodules. Use when Codex needs to refresh Yorkie-related submodules under projects, sync .gitmodules URLs, initialize missing submodules, update them to their tracked main branches, or report resulting gitlink changes.
---

# Update Yorkie Submodules

## Overview

Use this skill in the Yorkie community repository to keep the project submodules under `projects/` initialized and updated to their tracked `main` branches.

Managed submodules:

- `projects/yorkie`
- `projects/yorkie-js-sdk`
- `projects/yorkie-team.github.io`
- `projects/dashboard`
- `projects/codepair`
- `projects/syncup`
- `projects/wafflebase`
- `projects/yorkie-rust-sdk`

## Workflow

1. Start from the community repository root and inspect `git status --short`.
2. Run the bundled script:

```bash
bash skills/update-yorkie-submodules/scripts/update_yorkie_submodules.sh
```

3. If SSH access to GitHub is unavailable but the public repositories are readable over HTTPS, rerun with:

```bash
bash skills/update-yorkie-submodules/scripts/update_yorkie_submodules.sh --https-fallback
```

4. Review `git submodule status` and `git status --short -- .gitmodules projects`.
5. Report any changed gitlinks in the parent repository. Do not commit or stage unless the user asks.

## Safety

- The script refuses to update a submodule that has local uncommitted changes. Use `--allow-dirty` only after the user explicitly accepts that risk.
- Keep `.gitmodules` URLs in SSH form (`git@github.com:...`) with `branch = main` and `ignore = dirty`.
- Prefer `git submodule update --remote --merge --recursive` over manually checking out detached commits inside each submodule.
