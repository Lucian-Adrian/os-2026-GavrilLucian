#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 1 ]]; then
  printf 'Usage: bash lab6/prepare-overlay.sh /path/to/os\n' >&2
  exit 2
fi

repo_root="$(cd "$1" && pwd)"
lab2_root="$repo_root/lab2"
lab6_root="$repo_root/lab6"

for source in "$lab2_root/Makefile" "$lab6_root/user/mystat.c" "$lab6_root/user/find.c"; do
  if [[ ! -f "$source" ]]; then
    printf 'Missing required source: %s\n' "$source" >&2
    exit 1
  fi
done

overlay="$(mktemp -d /tmp/faf-os-lab6.XXXXXX)"
cp -a "$lab2_root/." "$overlay/"
install -D "$lab6_root/user/mystat.c" "$overlay/user/mystat.c"
install -D "$lab6_root/user/find.c" "$overlay/user/find.c"

python3 - "$overlay/Makefile" <<'PY'
from pathlib import Path
import sys

makefile = Path(sys.argv[1])
content = makefile.read_text()
marker = "\t$U/_logstress\\\n"

if content.count(marker) != 1:
    raise SystemExit("Expected one _logstress entry in the copied Makefile.")

for program in ("sleep", "args"):
    entry = f"\t$U/_{program}\\\n"
    if content.count(entry) != 1:
        raise SystemExit(f"Expected one existing _{program} entry.")

addition = marker + "\t$U/_mystat\\\n\t$U/_find\\\n"
content = content.replace(marker, addition, 1)

for program in ("mystat", "find"):
    entry = f"\t$U/_{program}\\\n"
    if content.count(entry) != 1:
        raise SystemExit(f"Failed to add exactly one _{program} entry.")

makefile.write_text(content)
PY

printf '%s\n' "$overlay"
