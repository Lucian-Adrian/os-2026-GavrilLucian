# Lab 17: Threads Share Memory, and Race

Machine: Intel Core i5-12400F (12 logical CPUs), Debian 13, Linux 6.12, GCC 14.2.
Built with `gcc -Wall -Wextra -pthread` and no `-O2`, as in the brief. No warnings.
Raw output for every number below is in `evidence/`.

## Part 1: the race

Three runs of `./fire` (`evidence/1_fire.txt`):

| Run | counter | lost |
|---|---|---|
| 1 | 1 007 358 | 992 642 (49.6 %) |
| 2 | 1 470 750 | 529 250 (26.5 %) |
| 3 | 1 003 769 | 996 231 (49.8 %) |

Ten more runs gave between 1 019 581 and 1 528 489 (`evidence/2_scaling.txt`). The result never reached 2 000 000.

### Observe 1: thread 2 prints a non-zero counter. What does that prove?

It proves the two threads use **the same memory**, not two copies of it. Thread 2 reads `counter` and sees additions that only thread 1 made. Thread 2 never wrote anything yet, so the value can only come from thread 1. That means both threads read and write the same variable at the same address.

On this machine thread 2 usually starts too early to see this. In 200 runs it printed 0 in 179 runs and a non-zero value in 21 (272, 878, 2486, 11 641, 86 389, …) (`evidence/1_thread2_200runs.txt`). The reason: `pthread_create` for thread 2 returns within microseconds, and thread 1 has barely entered its loop by then. Whenever thread 1 got ahead before thread 2 printed, thread 2 saw its additions.

Two extra checks make the proof direct (`fire4.c`, `evidence/2_fire4.txt`):
- With 4 threads, threads 3 and 4 started later and saw 2552 and 5131.
- Every thread printed `&counter`, and all four printed the **same address**, `0x5646c6cfe030`. A child process after `fork()` would have its own copy, so its writes would never show up in the parent. Threads have one copy.

### Observe 2: why is the final counter less than 2 000 000, and different each run?

`counter++` is not one step. `gcc -S` shows it as three instructions (`evidence/1_asm.txt`, lines 39–41):

```asm
movq  counter(%rip), %rax    # 1. load  the value from memory into a register
addq  $1, %rax               # 2. add 1 inside the register (private to this thread)
movq  %rax, counter(%rip)    # 3. store the register back to memory
```

The two threads run on two cores at the same time. A lost update looks like this:

| time | thread 1 | thread 2 | counter in memory |
|---|---|---|---|
| t1 | load → 500 | | 500 |
| t2 | | load → 500 | 500 |
| t3 | add → 501 | add → 501 | 500 |
| t4 | store 501 | | 501 |
| t5 | | store 501 | **501** |

Two additions ran, but the counter grew by one. Thread 2's store overwrote thread 1's.

The result changes from run to run because the number of overlaps depends on timing. That timing includes when each thread starts, which cores the scheduler picks, interrupts, other programs, and how fast the cache line holding `counter` moves between the cores. None of these repeat exactly.

Two experiments confirm that overlap is the cause (`evidence/2_one_core.txt`):
- `taskset -c 0 ./fire` puts both threads on **one core**. All three runs printed exactly 2 000 000. One core runs only one thread at a time, so the three steps can only be split if the scheduler preempts a thread between its load and its store. That is rare.
- Rare does not mean safe. `taskset -c 0 ./fire4` printed 4 000 000, 4 000 000, then **2 000 000**. One thread was preempted right after its load. Two other threads then ran their whole million each, and the preempted thread stored its old value plus one, which wiped out 2 000 000 additions at once.

## Part 2: make it worse

`fire4.c` is the same program with `T` threads (`-DT=8` builds `fire8`). Ten runs each (`evidence/2_scaling.txt`):

| threads | expected | counter (range) | lost |
|---|---|---|---|
| 2 | 2 000 000 | 1 019 581 – 1 528 489 | 24 % – 49 % |
| 4 | 4 000 000 | 1 230 108 – 1 629 723 | 59 % – 69 % |
| 8 | 8 000 000 | 1 312 805 – 1 837 519 | 77 % – 84 % |

**Yes, the loss grows.** More threads means more loads that overlap. The final counter stays around 1.2–1.8 million no matter how many threads run. Most threads mainly overwrite each other's work.

### Observe 3: in one sentence, what single idea stops the lost updates?

**Mutual exclusion:** make the load–add–store of `counter++` a critical section that only one thread at a time may run, for example with a mutex locked before `counter++` and unlocked after it.

I checked the proposal with `fix.c`: four threads, with `pthread_mutex_lock` and `pthread_mutex_unlock` around `counter++` (`evidence/2_fix.txt`). It printed exactly 4 000 000 in all three runs. The lock has a cost: 0.222 s instead of 0.007 s, about 30 times slower, because every addition now waits for the lock. A hardware atomic add (`__atomic_fetch_add`, or `lock addq` in assembly) is the cheaper alternative for a single counter.

### A trap: `-O2` hides the race

Built with `-O2`, `fire` printed 2 000 000 in five runs out of five (`evidence/3_O2.txt`). The compiler replaced the whole loop with a single instruction, `addq $1000000, counter(%rip)` (`evidence/3_O2_asm.txt`). The race is still there: that instruction is still load, add, store inside the CPU, and nothing locks it. The window just became so small that it is rarely hit. Getting the right answer is not proof of correct code. That is why the brief forbids `-O2`.

## Files

`fire.c` (the brief's program), `fire4.c` (T threads plus the address), `fix.c` (mutex), `Makefile`, `evidence/`, and `report.pdf` (the same answers with the figures).
