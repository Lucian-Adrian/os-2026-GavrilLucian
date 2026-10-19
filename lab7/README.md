# Lab 7: processes, redirection and pipes

This lab follows one command through process creation, program replacement and waiting, then uses file descriptors to reproduce shell redirection and a two-command pipeline.

The measured observations and answers to each required question are in [report.md](report.md). The [recorded execution session](../lab78/execution-session-2026-10-19.txt) preserves the build and run output alongside the screenshots.

## Files

- `brief.pdf`: original English assignment handout.
- `run.c`, `zombie.c`, `redirect.c`, `pipeline.c`: the four programs supplied by the teacher.
- `pipeline3.c`: optional three-stage extension.
- `report.md`: answers to every required Observe question, with measured results separated from explanations.
- [report.pdf](report.pdf): printable report with diagrams of the process and descriptor changes.
- [report.tex](report.tex): editable report using the canonical UTM `assets/utmreport.cls` and logo. Build from this folder with `tectonic -X compile report.tex`.
- `assets/proof-*.png`: seven original live execution screenshots, embedded beside the relevant results in the report.
- `teaching-note.md`: first-principles explanation, source traces, speaking route and practice answers.
- [teaching-note.pdf](teaching-note.pdf): visual study brief with a ten-minute route and priority defense questions.

## Requirements

Use Linux with `gcc`, the usual `ls`, `wc`, `date`, and `ps` commands, and a POSIX shell. `timeout` is used only for the intentionally broken pipeline experiment. Check `gcc --version` first. No service or elevated permission is needed.

## Build and run safely

Keep generated programs and `out.txt` in a disposable directory so the lab folder contains only source and documents:

```sh
tmpdir=$(mktemp -d)
cp run.c zombie.c redirect.c pipeline.c pipeline3.c "$tmpdir/"
cd "$tmpdir"
gcc -Wall -Wextra -o run run.c
./run
gcc -Wall -Wextra -o zombie zombie.c
gcc -Wall -Wextra -o redirect redirect.c
gcc -Wall -Wextra -o pipeline pipeline.c
gcc -Wall -Wextra -o pipeline3 pipeline3.c
```

The teacher's `run.c` is the `ls -l` version. For the `date` and missing-program exercises, make a temporary copy and replace only its `execlp` line with the exact line below. Leave the submitted `run.c` unchanged.

```c
execlp("date", "date", (char *)NULL);
execlp("nosuchprog", "nosuchprog", (char *)NULL);
```

For the zombie observation, run the program in the background, inspect its direct child while the parent is in its 20-second sleep, then wait for the parent:

```sh
./zombie >/dev/null &
zombie_parent=$!
sleep 2
ps -o pid,ppid,stat,cmd -p "$zombie_parent" --ppid "$zombie_parent"
wait "$zombie_parent"
ps -o pid,ppid,stat,cmd -p "$zombie_parent"
```

For redirection, run `./redirect` from the disposable directory and inspect `head -3 out.txt` there.

For the pipeline comparison, run `./pipeline` and then `ls /etc | wc -l` from the same environment. The two numbers should match for an unchanged `/etc` listing.

The final Observe question deliberately makes the pipeline hang by leaving the parent's pipe write end open. Create the changed file only in the disposable directory, compile it, and bound the run with GNU `timeout`:

```sh
python3 - <<'PY'
from pathlib import Path

source = Path("pipeline.c").read_text()
old = "    close(p[1]);\n    wait(NULL);"
assert source.count(old) == 1
Path("pipeline-broken.c").write_text(
    source.replace(old, "    /* close(p[1]); */\n    wait(NULL);", 1)
)
PY
gcc -Wall -Wextra -o pipeline-broken pipeline-broken.c
timeout --signal=TERM --kill-after=2s 4s ./pipeline-broken
```

The timeout is the expected result for this broken variant. Do not run it without a bound or modify the canonical `pipeline.c`. The measured run and process-group cleanup are recorded in [report.md](report.md).
