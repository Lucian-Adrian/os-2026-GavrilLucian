# Lab 11 – The Race and the Semaphore (Linux)

| File | Content |
|---|---|
| `report.md` | the Observe answers of Parts 1–4, as the brief asks |
| `report.pdf`, `report.tex` | UTM report with figures |
| `race.c`, `mutex.c`, `sem.c`, `order.c`, `parking.c` | the five required programs |
| `atomic.c` | the optional lock-free counter |
| `Makefile` | builds everything, plus the Observe variants `sem2`, `order1`, `parking1` |
| `evidence/` | the raw terminal output behind every figure |
| `brief.pdf`, `assets/` | the handout; figures, UTM class and logo |

The Observe experiments change one start value. Instead of editing the sources, the Makefile passes it with `-D`:

| Target | Built as | Question |
|---|---|---|
| `sem2` | `sem.c` with `-DSTART=2` | 2.2: semaphore starting at 2 |
| `order1` | `order.c` with `-DSTART=1` | 3.1: signal starting at 1 |
| `parking1` | `parking.c` with `-DPLACES=1` | 4.2: one parking place |

```bash
make                       # gcc -Wall -pthread, no -O2 (the brief forbids it today)
./race; ./race; ./race     # never 2000000
./mutex; ./sem             # always 2000000
./sem2                     # wrong again
time ./race; time ./mutex; time ./sem; time ./atomic
strace -f -c -e trace=futex ./mutex
./order; ./order1          # "hello", then ""
./parking; ./parking1      # max 3 inside, then one at a time
```

To rebuild the PDF, run `tectonic -X compile report.tex`.
