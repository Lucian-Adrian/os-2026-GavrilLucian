# Lab 12 – Producer, Consumer and the Other Tools (Linux)

| File | Content |
|---|---|
| `report.md` | the Observe answers of Parts 1–4, as the brief asks |
| `report.pdf`, `report.tex` | UTM report with figures and the deadlock diagram |
| `prodcons.c`, `condvar.c`, `readers.c`, `deadlock.c` | the four required programs (`deadlock.c` is the fixed version) |
| `Makefile` | builds everything, plus the Observe variants |
| `evidence/` | the raw terminal output behind every figure |
| `brief.pdf`, `assets/` | the handout; figures, UTM class and logo |

The handed-in sources behave exactly as in the brief when built by default (they only add `setvbuf` for unbuffered output and `#ifdef` hooks). The Observe experiments are built from them with `-D`:

| Target | Built as | Question |
|---|---|---|
| `prodcons_swapped` | `prodcons.c` with `-DSWAPPED` | 1.3: mutex locked before `sem_wait(&empty)` |
| `condvar_if` | `condvar.c` with `-DUSE_IF` | 2.2: `if` instead of `while` |
| `deadlock_orig` | `deadlock.c` with `-DORIGINAL` | Part 4: opposite lock order |
| `deadlock_nosleep` | `deadlock.c` with `-DORIGINAL -DNOSLEEP` | 4.2: no `sleep(1)` |

```bash
make
./prodcons
timeout 5 ./prodcons_swapped; echo "exit code: $?"    # 124
./condvar; ./condvar_if
./readers
timeout 5 ./deadlock_orig; echo "exit code: $?"       # 124
timeout 5 ./deadlock; echo "exit code: $?"            # done, 0
for i in $(seq 10); do timeout 1 ./deadlock_nosleep > /dev/null; echo -n "$? "; done; echo
```

To rebuild the PDF, run `tectonic -X compile report.tex`.
