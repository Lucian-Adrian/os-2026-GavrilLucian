# Lab 17 – Threads Share Memory, and Race (Linux)

| File | Content |
|---|---|
| `fire.c` | the brief's program: 2 threads, 1 counter, no lock |
| `report.md` | the three Observe answers, as the brief asks |
| `report.pdf`, `report.tex` | UTM report with figures |
| `fire4.c` | Part 2: `T` threads (4 by default, `-DT=8` gives 8). Each thread prints `&counter` |
| `fix.c` | the proposed fix, tested: a mutex around `counter++` |
| `Makefile` | builds everything |
| `evidence/` | the raw terminal output behind every figure |
| `brief.pdf`, `assets/` | the handout; figures, UTM class and logo |

```bash
make                          # gcc -Wall -Wextra -pthread, no -O2
./fire; ./fire; ./fire        # never 2000000
./fire4; ./fire8              # one shared address, bigger loss
taskset -c 0 ./fire4          # one core: usually right, sometimes 2M lost at once
./fix                         # always 4000000, ~30x slower
make fire-O2 && ./fire-O2     # -O2 hides the race (loop becomes one addq)
```

To rebuild the PDF, run `tectonic -X compile report.tex`.
