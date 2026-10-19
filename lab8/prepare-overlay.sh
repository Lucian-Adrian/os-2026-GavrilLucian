#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 1 ]]; then
  printf 'Usage: bash lab8/prepare-overlay.sh /path/to/os\n' >&2
  exit 2
fi

repo_root="$(cd "$1" && pwd)"
lab2_root="$repo_root/lab2"
lab8_root="$repo_root/lab8"

for source in \
  "$lab2_root/Makefile" \
  "$lab8_root/user/run.c" \
  "$lab8_root/user/pingpong.c" \
  "$lab8_root/user/primes.c"; do
  if [[ ! -f "$source" ]]; then
    printf 'Missing required source: %s\n' "$source" >&2
    exit 1
  fi
done

overlay="$(mktemp -d /tmp/faf-os-lab8.XXXXXX)"
cp -a "$lab2_root/." "$overlay/"
install -D "$lab8_root/user/run.c" "$overlay/user/run.c"
install -D "$lab8_root/user/pingpong.c" "$overlay/user/pingpong.c"
install -D "$lab8_root/user/primes.c" "$overlay/user/primes.c"

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

addition = marker + "\t$U/_run\\\n\t$U/_pingpong\\\n\t$U/_primes\\\n"
content = content.replace(marker, addition, 1)

for program in ("run", "pingpong", "primes"):
    entry = f"\t$U/_{program}\\\n"
    if content.count(entry) != 1:
        raise SystemExit(f"Failed to add exactly one _{program} entry.")

makefile.write_text(content)
PY

printf '%s\n' "$overlay"
