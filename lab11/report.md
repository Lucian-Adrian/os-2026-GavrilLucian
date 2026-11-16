# Lab 11 – The Race and the Semaphore

Lucian-Adrian Gavril, FAF-241. Debian 13, Linux 7.2, GCC 14.2, Intel Core i7-1355U (12 logical CPUs). Every program is compiled with `gcc -Wall -pthread` and no `-O2`. All the numbers below are real runs. The raw terminal output is in `evidence/`, and the full report with figures is `report.pdf`.

## Part 1 – See the race

Five runs of `./race`: 1214868, 1085564, 1031688, 1019785, 1014123. None of them reaches 2000000, and in most runs almost half of the additions are lost.

**1. `counter++` looks like one step. Write the three steps the CPU really does.**
`gcc -S race.c` shows them:
```
movq  counter(%rip), %rax    # 1. load: read counter from memory into a register
addq  $1, %rax               # 2. add: add 1 inside the register
movq  %rax, counter(%rip)    # 3. store: write the register back to memory
```

**2. Describe, with those steps, how two threads can lose one addition.**
`counter` is 100. Thread A loads 100 into its register. Before A stores, thread B, on another core, also loads 100. A adds 1 and stores 101. B adds 1 to its own copy and also stores 101. Two additions ran, but `counter` went from 100 to 101. B's store overwrote A's, so one addition is lost. Each thread has its own register, and the memory is the only shared copy.

**3. Why is the result different at every run?**
The loss depends on how often the two load–add–store sequences overlap. That depends on when the scheduler starts each thread, on which cores they run, on interrupts and other load, and on when the cache line holding `counter` moves between cores. None of this repeats exactly, so the number of collisions, and the result, is different every time.

## Part 2 – Fix it: mutex, then semaphore

**1. Run mutex and sem three times each. Is the answer always 2 000 000?**
Yes. All six runs print `counter = 2000000 (expected 2000000)`. With the lock, the load–add–store of one thread is finished before the other thread may start its own, so no addition can be overwritten.

**2. What would happen in sem.c with `sem_init(&s, 0, 2)`? Try it and explain.**
It is wrong again. `make sem2` builds `sem.c` with `-DSTART=2`, and three runs gave 1993053, 1838146 and 1672013. A semaphore that starts at 2 lets two threads past `sem_wait` at the same time: the first takes 2→1 and the second takes 1→0. There are only two threads, so the "lock" never stops anyone, and the race of Part 1 is back. It loses fewer additions than `race` only because the `sem_wait`/`sem_post` calls add work between the increments, so the two threads collide less often.

**3. Why is the locked version slower?**
Measured with `time`: race 0.009 s (wrong), atomic 0.076 s, mutex 0.232 s, sem 0.267 s. The order is the same as on the reference machine.
- Every `lock`/`unlock` (or `sem_wait`/`sem_post`) is an atomic read-modify-write instruction. It forces the cache line to move between the two cores. That happens 2 000 000 times, against a plain `addq` in `race`.
- When one thread finds the lock taken, it cannot spin forever. It asks the kernel to put it to sleep with the `futex` system call, and the other thread must wake it with another `futex`. `strace -f -c -e trace=futex ./mutex` counted **10 759 futex calls** (`race` makes 2). That is why `sys` time goes from 0.000 s to 0.140 s (mutex) and 0.217 s (sem).
- The critical section runs one thread at a time, so the two cores no longer work in parallel on the counter.

The optional `atomic.c` (`atomic_fetch_add` compiles to one `lock addq $1, counter(%rip)` instruction) is also always correct. It is about 3× faster than the mutex because it never sleeps and never enters the kernel.

## Part 3 – A semaphore as a signal

`./order` prints `B: waiting for the message...` at once, then nothing for one second (`real 1.003 s`), then `A: message written` and `B: I read "hello"`.

**1. Change the start value to 1. What does B read now, and why?**
`make order1` (`-DSTART=1`) prints:
```
B: waiting for the message...
B: I read ""
A: message written
```
B reads an **empty string**. The semaphore already holds one unit, so B's `sem_wait` takes it (1→0) and returns at once, one second before A writes anything. `message` is a global, so it is still all zeros, and the read is `""`. The semaphore said "ready" when nothing was ready.

**2. Put it back to 0. In one sentence: what does a semaphore that starts at 0 mean?**
A semaphore that starts at 0 means "the event has not happened yet": whoever calls `sem_wait` sleeps until another thread announces the event with `sem_post`.

## Part 4 – A semaphore as a counter: the parking lot

**1. What is the largest value of "inside" you see? Which line of code guarantees it?**
The largest value is **3**. In ten runs (120 lines) I counted 23 lines with `inside: 3` and none with 4 or more. The guarantee is `sem_wait(&places);` in `car()`, together with `sem_init(&places, 0, PLACES)`. The semaphore starts at 3 and every car that enters takes one unit, so the fourth car sleeps in `sem_wait` until a car leaving calls `sem_post(&places)`. The run takes `2.003 s`: two "waves" of one second each.

**2. Set PLACES to 1. What does the semaphore become?**
It becomes a **mutex** (a binary semaphore), exactly like `sem.c` in Part 2. With `make parking1` (`-DPLACES=1`) only one car is ever inside: each `enters (inside: 1)` is followed by its own `leaves (inside: 0)`. The six cars park strictly one after the other, so the run takes `6.004 s` instead of 2 s.

## Summary

| Use | Start value | Program | Result |
|---|---|---|---|
| lock (mutual exclusion) | 1 | `sem.c` | always 2000000 |
| signal (order) | 0 | `order.c` | B reads only after A writes |
| counter (resources) | N = 3 | `parking.c` | never more than 3 inside |
