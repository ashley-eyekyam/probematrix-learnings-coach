#!/usr/bin/env bash
# Install the ProbeMatrix Learnings Coach skills for OpenAI Codex (user level).
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
dest="${CODEX_SKILLS_DIR:-$HOME/.agents/skills}"
mkdir -p "$dest"
for d in "$here"/skills/*/; do
  name="$(basename "$d")"
  rm -rf "${dest:?}/$name"
  cp -R "$d" "$dest/$name"
  echo "installed $name"
done
python3 -c "import openpyxl" 2>/dev/null || echo "Note: run 'pip install openpyxl' so the skills' engine can read .xlsx exports."
echo "Done. Skills are in $dest. Restart Codex if they do not appear."
