# Lab 12 – Producer, Consumer and the Other Tools

Lucian-Adrian Gavril, FAF-241. Debian 13, Linux 7.2, GCC 14.2, Intel Core i7-1355U (12 logical CPUs). Every program is compiled with `gcc -Wall -pthread`. The experiments of the Observe questions are reproduced without editing the handed-in files: `make` also builds `prodcons_swapped`, `condvar_if`, `deadlock_orig` and `deadlock_nosleep` from the same sources with `-D` flags. The raw output is in `evidence/`, and the full report with figures is `report.pdf`.

Each program sets `stdout` to line buffering (`setvbuf`), so the order of the lines is the real order, also when the output goes to a file or a pipe.

## Part 1 – Producer and consumer

The run matches the expected output line for line: `put 1`–`put 4` fill the buffer, then every `take` makes room for exactly one `put`, and `take 5`–`take 8` empty it. `in buffer` is never above 4 and never below 0.

**1. The producer is fast, yet "in buffer" never goes above 4. Which call stops it?**
`sem_wait(&empty)` in `producer()`. `empty` starts at `SIZE` = 4 and every `put` takes one unit. After `put 4` it is 0, so the producer sleeps there until the consumer frees a slot with `sem_post(&empty)`. That is why, after the buffer is full, each `put` comes only after a `take`.

**2. Who waits at the start: the consumer or the producer? Which call makes it wait?**
The **consumer**. It is created first, and its first call is `sem_wait(&full)`. `full` starts at 0 (nothing to take), so it sleeps until the producer's first `sem_post(&full)`.

**3. Lock the mutex BEFORE `sem_wait(&empty)` in `producer()`. What happens when the buffer is full, and why?**
It deadlocks. `prodcons_swapped` printed `put 1`–`put 4` and then nothing. `timeout 5` had to kill it (`exit code: 124`), and not even `take 1` appeared. With the buffer full, the producer locks the mutex and then sleeps in `sem_wait(&empty)` (empty = 0) **while still holding the mutex**. The consumer passes `sem_wait(&full)` (full = 4) but then blocks in `pthread_mutex_lock(&lock)`. The producer waits for the consumer's `sem_post(&empty)`, and the consumer waits for the producer's unlock. Neither can move. Rule: wait on the counting semaphore first, take the mutex only around the buffer itself.

## Part 2 – The condition variable

`./condvar` prints `B: not ready, I sleep`, then after one second `A: message written` and `B: I read "hello"`.

**1. In order.c the semaphore itself remembered that the message was ready. Here, which variable remembers it?**
The plain integer **`ready`**, protected by `lock`. The condition variable `changed` remembers nothing. It is only the place where B sleeps. A `pthread_cond_signal` with no thread waiting is simply lost, which is why B must look at `ready` before it decides to sleep.

**2. Replace `while (!ready)` with `if (!ready)`. Does it still work here?**
Yes. `condvar_if` printed the same three lines. Here there is one writer, one reader and one signal, and A sets `ready = 1` before signalling under the same mutex. So the only wake-up B gets is the right one, and `ready` really is 1 when it re-checks.

**3. Then why do we write while? Give one reason why a thread can wake up and still find ready == 0.**
`pthread_cond_wait` is allowed to return without anyone signalling (a *spurious wake-up*); POSIX says so explicitly. Even a real wake-up is not a promise. Between the signal and the moment the woken thread gets the mutex back, another thread can take the mutex first and use the condition up (for example a second reader that resets `ready = 0`, or a `pthread_cond_broadcast` that wakes several waiters for one item). With `if`, B would go on and read a message that is not there. With `while`, it checks again and sleeps again.

## Part 3 – Readers and writers

Three runs. In every run the three readers are inside together (`readers inside: 1, 2, 3`), and each writer is alone. The order changes between runs: once the writer 1 thread came first (`writer 1 writes 10`, then the readers read 10), and twice the readers came first and read 0, then both writers wrote.

**1. Three readers are inside at the same time, but a writer is always alone. Which two lines of reader() make that possible?**
```c
if (++readers == 1)  sem_wait(&room);   /* the first reader in locks out the writers */
if (--readers == 0)  sem_post(&room);   /* the last reader out lets the writers in */
```
Only the first reader takes `room`. The others see `readers > 1` and walk in without touching it. The whole group of readers holds `room` as one, and returns it only when the last one leaves. A writer needs `room` for itself, so it can never be inside with a reader or with another writer.

**2. Why does the counter readers need its own lock (rlock)? What could go wrong without it?**
`++readers` and `--readers` are load–add–store, exactly the race of Lab 11. The test `== 1` / `== 0` must also happen together with the change. Without `rlock`, two readers arriving at once could both read 0 and both write 1. Both would then call `sem_wait(&room)`, and the second one would block although readers are allowed to share. Two leaving readers could lose a decrement, so `readers` never returns to 0 and `room` is never given back: the writers wait forever. Or the count reaches 0 too early, `room` is released while a reader is still reading, and a writer changes `value` under it.

A small trace of the same problem is visible in run 3: `readers inside: 3` was printed before `readers inside: 2`. The `printf` reads `readers` *outside* `rlock`, so it prints whatever the value is at that moment. That is harmless because it is only display, but it shows that an unprotected read of a shared counter is a snapshot that can already be out of date.

**3. Imagine readers that keep arriving without a pause. What happens to writer 2?**
It **starves**. As long as at least one reader is inside, `readers` never drops to 0, so `sem_post(&room)` is never called, and writer 2 waits in `sem_wait(&room)` forever, although nothing is deadlocked and the system keeps working. This solution prefers readers. The usual fix is a "turnstile" semaphore that a waiting writer takes, so new readers queue behind it.

## Part 4 – Build a deadlock, then remove it

The original order (`deadlock_orig`) prints `one: I have A, I want B` and `two: I have B, I want A`, then nothing, and `timeout` ends it with **exit code 124**. The fixed `deadlock.c` (both threads lock A, then B) prints both `I have both` lines and `done`, **exit code 0**. Because `two()` now takes A first, its first message is `two: I have A, I want B`.

**1. In the stuck run, which thread holds which mutex, and which one is each thread waiting for? Draw the circle.**
```
        holds A                       holds B
  one ─────────► waits for B ───► owned by two
   ▲                                     │
   │                                     ▼
 owned by one ◄─── waits for A ◄──────  two
```
`one` holds **A** and waits for **B**. `two` holds **B** and waits for **A**. one → B → two → A → one is a closed circle, so neither can ever continue.

**2. Remove both sleep(1) lines from the ORIGINAL version and run it ten times. Does it still always hang? Why is that worse, not better?**
No, not always. On 12 CPUs, 4 of 10 runs hung (exit codes `0 0 124 124 0 0 0 124 124 0`). In three sessions of 100 runs, 53, 72 and 68 hung. Pinned to one CPU (`taskset -c 0`), **all 100 finished**. The `printf` between the two locks still leaves a window in which the other thread can take its first lock. On one CPU, a thread usually takes both locks before it is preempted. With `sleep(1)` the deadlock is certain and shows up at the first test. Without it, the result depends on timing, the number of cores and the load, and even the share of hangs changed from session to session. This is worse because the bug is now **intermittent**. The program can pass a test (or every test on a one-CPU machine) and hang later in production, and a hang that does not repeat is very hard to reproduce and debug. The code is just as wrong as before. Only the evidence became unreliable.

**3. In one sentence: why can taking the locks in the same order never deadlock?**
If every thread takes the locks in the same global order (A before B), a thread holding a lock only ever waits for a lock that comes later in that order, so the chain of "waits for" can only go forward and can never close into a circle.
