#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: update_yorkie_submodules.sh [--repo <path>] [--https-fallback] [--allow-dirty]

Updates the Yorkie community repository's managed submodules under projects/.

Options:
  --repo <path>       Repository root. Defaults to the current Git repository root.
  --https-fallback   Rewrite git@github.com: reads to https://github.com/ for this run.
  --allow-dirty      Continue even if a submodule has local uncommitted changes.
  -h, --help         Show this help.
USAGE
}

repo_root=""
https_fallback=0
allow_dirty=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      if [[ $# -lt 2 ]]; then
        echo "error: --repo requires a path" >&2
        exit 2
      fi
      repo_root="$2"
      shift 2
      ;;
    --https-fallback)
      https_fallback=1
      shift
      ;;
    --allow-dirty)
      allow_dirty=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$repo_root" ]]; then
  repo_root="$(git rev-parse --show-toplevel)"
fi

submodules=(
  "projects/yorkie"
  "projects/yorkie-js-sdk"
  "projects/yorkie-team.github.io"
  "projects/dashboard"
  "projects/codepair"
  "projects/syncup"
  "projects/wafflebase"
  "projects/yorkie-rust-sdk"
)

git_cmd=(git)
if [[ "$https_fallback" -eq 1 ]]; then
  git_cmd=(git -c url.https://github.com/.insteadOf=git@github.com:)
fi

cd "$repo_root"

if [[ ! -f ".gitmodules" ]]; then
  echo "error: .gitmodules not found in $repo_root" >&2
  exit 1
fi

missing=()
for path in "${submodules[@]}"; do
  if ! git config --file .gitmodules --get "submodule.${path}.path" >/dev/null; then
    missing+=("$path")
  fi
done

if [[ "${#missing[@]}" -gt 0 ]]; then
  echo "error: missing submodule entries in .gitmodules:" >&2
  printf '  - %s\n' "${missing[@]}" >&2
  exit 1
fi

if [[ "$allow_dirty" -eq 0 ]]; then
  dirty=()
  for path in "${submodules[@]}"; do
    if [[ -e "$path/.git" ]] || [[ -f "$path/.git" ]]; then
      if [[ -n "$(git -C "$path" status --porcelain)" ]]; then
        dirty+=("$path")
      fi
    fi
  done

  if [[ "${#dirty[@]}" -gt 0 ]]; then
    echo "error: refusing to update dirty submodules:" >&2
    printf '  - %s\n' "${dirty[@]}" >&2
    echo "Pass --allow-dirty only after preserving or accepting those local changes." >&2
    exit 2
  fi
fi

echo "Syncing configured submodule URLs..."
"${git_cmd[@]}" submodule sync --recursive -- "${submodules[@]}"

echo "Initializing submodules..."
"${git_cmd[@]}" submodule update --init --recursive -- "${submodules[@]}"

echo "Updating submodules from their tracked branches..."
"${git_cmd[@]}" submodule update --remote --merge --recursive -- "${submodules[@]}"

echo
echo "Submodule status:"
"${git_cmd[@]}" submodule status -- "${submodules[@]}"

echo
echo "Parent repository changes:"
"${git_cmd[@]}" status --short -- .gitmodules "${submodules[@]}"
