#!/usr/bin/env bash
# Install the ProbeMatrix Learnings Coach skills for OpenAI Codex (user level).
set -euo pipefail
if ! command -v python3 >/dev/null 2>&1 || ! python3 -c 'import sys; sys.exit(sys.version_info < (3, 9))'; then
  echo "Error: Python 3.9 or later is required (python3 was not found or is older than 3.9)." >&2
  exit 1
fi
here="$(cd "$(dirname "$0")/.." && pwd)"
dest="${CODEX_SKILLS_DIR:-$HOME/.agents/skills}"
mkdir -p "$dest"
for d in "$here"/skills/*/; do
  name="$(basename "$d")"
  rm -rf "${dest:?}/$name"
  cp -R "$d" "$dest/$name"
  echo "installed $name"
done
if [ ! -f "$dest/learnings-coach/scripts/pmlc.py" ]; then
  echo "Error: learnings-coach was not copied to $dest; the other skills need it." >&2
  exit 1
fi
python3 -c "import openpyxl" 2>/dev/null || echo "Note: run 'pip install openpyxl' so the skills' engine can read .xlsx exports."
echo "Done. Skills are in $dest. Restart Codex if they do not appear."
