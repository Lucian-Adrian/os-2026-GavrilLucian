# OS assessment 2: practice questions

49 questions. Answer on paper first, then open the answer. ★ marks the 10 most likely (they come straight from the Observe questions of Labs 7–18 or from the core mechanisms the course repeats). Types: **T** theory, **P** predict the output, **B** find the bug, **D** draw the diagram.

Every Linux "predict" answer below was run on Debian 13 / GCC 14 on 25 November 2026. xv6 facts refer to `lab18/xv6-riscv`.

The ten ★: 1, 4, 10, 12, 18, 29, 31, 36, 40, 45.

---

## A. Processes: fork, exec, wait

### 1 ★ (T) Write the three steps a shell performs to run `ls -l`, naming the system call of each step and what it returns.

<details><summary>Answer</summary>

1. `fork()` copies the shell. Returns the child's PID in the parent, 0 in the child (−1 on error).
2. In the child, `exec("ls", argv)` replaces the program image with `ls`. Same PID, same open descriptors. On success it does not return; on failure it returns −1.
3. In the parent, `wait(&status)` (Linux `waitpid`) sleeps until the child exits, returns the child's PID and stores the exit status, freeing the zombie.

In xv6, the 0 in the child comes from `kfork()` setting `np->trapframe->a0 = 0`.
</details>

### 2 (P) How many lines does this print?

```c
for (int i = 0; i < 3; i++) fork();
printf("x\n");
```

<details><summary>Answer</summary>

**8.** Each `fork` doubles the number of processes: 2³ = 8, and each prints once. (Verified: `./t2 | wc -l` → 8.)
</details>

### 3 (P) How many times is `X` printed? How many processes exist in total?

```c
if (fork() && fork()) printf("X\n");
```

<details><summary>Answer</summary>

**Once**, 3 processes. The parent gets a PID (true) from the first fork, so it evaluates the second fork. The first child gets 0, `&&` short-circuits, no print. The second fork gives the parent true (prints X) and the second child 0 (no print). Verified.
</details>

### 4 ★ (P) What is printed (a) on a terminal, (b) with `./a.out | cat`?

```c
printf("hello ");
fork();
printf("world\n");
```

<details><summary>Answer</summary>

Both cases: `hello world` **twice**. `"hello "` has no newline, so it is still in the stdio buffer in user memory when `fork` copies that memory. Each process then adds `world\n` and flushes its own copy.

Contrast: `printf("A\n"); fork(); printf("B\n");` prints `A B B` on a terminal (line-buffered: A was flushed before fork), but `A B A B` into a pipe (fully buffered: A still in the buffer at fork). Both verified with `script` (pty) and a pipe. Same cause as Lab 9: 1 write into a pipe vs 3 on a terminal.
</details>

### 5 (P) What does the parent print?

```c
int x = 5;
int main(void) {
  if (fork() == 0) { x++; printf("child x=%d\n", x); return 3; }
  int st; wait(&st);
  printf("parent x=%d status=%d\n", x, WEXITSTATUS(st));
}
```

<details><summary>Answer</summary>

`child x=6`, then `parent x=5 status=3`. The child changes its own copy of memory. The raw `st` is 768 (= 3 << 8), which is why you need `WEXITSTATUS`. Verified. In xv6 `wait(&st)` would give plain 3.
</details>

### 6 (P) Output on a terminal and into a pipe?

```c
printf("start\n");
execlp("echo", "echo", "from", "echo", NULL);
printf("end\n");
```

<details><summary>Answer</summary>

Terminal: `start`, `from echo`. Pipe: only **`from echo`**. `end` never prints (successful exec does not return). Into a pipe, `start\n` is still in the stdio buffer, and exec throws the old memory away, buffer included. Fix: `fflush(stdout)` before `exec` (Lab 7 `run.c` does exactly this). Verified.
</details>

### 7 (T) What is a zombie? What is an orphan? How did Lab 7 show a zombie, and which line removed it?

<details><summary>Answer</summary>

A **zombie** has exited (runs no code, memory freed) but its process-table entry with PID and exit status stays until the parent calls `wait`. In xv6 `kexit` sets `state = ZOMBIE`; `kwait` finds it, copies `xstate`, calls `freeproc`. An **orphan** is a child whose parent exited first; `reparent()` gives it to `init`, which waits for it.

Lab 7 `zombie.c`: during the parent's `sleep(20)`, `ps` showed child 1894, PPID 1893, `STAT Z+`, `[ls] <defunct>`. `waitpid(pid, &status, 0)` at `zombie.c:25` reaped it. (Re-verified: a child that exits while the parent sleeps shows `Z`.)
</details>

### 8 (B) The author expects "child failed" to be impossible. Find the bug.

```c
if (fork() == 0) {
  execlp("nosuchprog", "nosuchprog", NULL);
}
printf("parent continues\n");
wait(NULL);
```

<details><summary>Answer</summary>

If `exec` fails it returns, and the child falls through into the parent's code: it prints "parent continues" too and calls `wait` (no children, returns −1). Always put `perror("exec"); exit(127);` right after `exec`. Lab 7 used 127; Lab 8 (xv6) used `exit(1)`. The status is chosen by the child's error branch, not by exec.
</details>

---

## B. Descriptors, redirection, pipes

### 9 (P) Which number does `open` return, and where does `ls` write?

```c
close(1);
int fd = open("out.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
execlp("ls", "ls", NULL);
```

<details><summary>Answer</summary>

**1**, the lowest free descriptor (xv6 `fdalloc()` scans from 0). `ls` writes to fd 1, which is now `out.txt`. Lab 7 measured `open gave descriptor 1`. For `2> err.txt`, `close(2)` before `open`.
</details>

### 10 ★ (T) Lab 7 leaked-writer experiment: `ls /etc | wc -l` built by hand, but the parent forgot `close(p[1])`. What happens and why?

<details><summary>Answer</summary>

`wc` never prints and never exits; the parent hangs in `wait`. `wc` reads until EOF. A pipe read returns 0 only when the pipe is empty **and every write end is closed**. `ls` exited, but the parent's copy of `p[1]` is still open, so the kernel must assume more data may come (xv6 `piperead` keeps sleeping while `writeopen` is 1). Measured: `wc` PID 2007 still running with PPID 2005 after `ls` finished.
</details>

### 11 (D) Draw the descriptor tables of the parent and both children for `ls | wc` just before the two `exec`s (after all `close`s), as in `user/sh.c` `case PIPE`.

<details><summary>Answer</summary>

```
parent:  0 tty  1 tty  2 tty        (p[0], p[1] closed)
child L: 0 tty  1 →pipe(write)  2 tty
child R: 0 →pipe(read)  1 tty  2 tty

          ls ──fd1──► [ pipe buffer ] ──fd0──► wc
```
Steps: `pipe(p)` gives fds 3 (read) and 4 (write). Left: `close(1); dup(p[1])` → 1; `close(p[0]); close(p[1])`. Right: `close(0); dup(p[0])` → 0; close both. Parent closes both and waits twice.
</details>

### 12 ★ (P) Output?

```c
int p[2]; pipe(p);
write(p[1], "hello", 5);
close(p[1]);
char b[10];
int n = read(p[0], b, 3);
int m = read(p[0], b, 10);
int k = read(p[0], b, 10);
printf("%d %d %d\n", n, m, k);
```

<details><summary>Answer</summary>

`3 2 0`. A pipe is a byte stream: read takes at most what is asked (3), then what is left (2). The third read finds it empty with no writer → 0 = EOF. Without `close(p[1])` the third read would block forever. Verified.
</details>

### 13 (P) After `close(0)`, the program calls `pipe(q)`. Fds 3 and 4 are already in use. What are `q[0]` and `q[1]`?

<details><summary>Answer</summary>

`q[0] = 0`, `q[1] = 5`. Each end takes the lowest free number at that moment: 0, then 5. Verified on Linux; xv6 `sys_pipe` calls `fdalloc` twice the same way.
</details>

### 14 (T) Why does `pingpong` (Lab 8) use two pipes instead of one?

<details><summary>Answer</summary>

A pipe is one-way and has no notion of "whose" byte it is. With one pipe the parent could write ping and then read its own byte back before the child does. With `parent_to_child` and `child_to_parent`, each direction has one writer and one reader. Measured: `10: received ping`, `9: received pong`. The parent blocks in `read(child_to_parent[0])` until the pong; `wait(0)` only reaps afterwards.
</details>

### 15 (T) Compare pipe capacity in xv6 and Linux, and say what happens when a writer fills it.

<details><summary>Answer</summary>

xv6: `PIPESIZE 512` bytes (`kernel/pipe.c`). Linux: 65 536 bytes (measured here by filling a non-blocking pipe). When full, `pipewrite` wakes readers (`wakeup(&pi->nread)`) and sleeps on `&pi->nwrite` until a reader removes bytes. If no reader exists at all, xv6 returns −1; Linux sends SIGPIPE.
</details>

### 16 (B) Lab 8 primes: a student's filter process never exits. Their child code is below. Find the bug.

```c
if (fork() == 0) {
  filter(next_pipe[0]);   /* recursive: reads primes from next_pipe */
}
close(next_pipe[0]);
```

<details><summary>Answer</summary>

The child inherited `next_pipe[1]` (and `input_fd`) and never closed them. The child itself holds a write end of the pipe it reads, so it never sees EOF. Fix as in `lab8/user/primes.c`: in the child, `close(input_fd); close(next_pipe[1]);` before `filter(next_pipe[0])`.
</details>

---

## C. System calls, strace, trace, sysinfo

### 17 (T) Trace `write(1, "hi", 2)` in xv6 from the user program to the console. Name each step.

<details><summary>Answer</summary>

`user/usys.S` stub (generated by `usys.pl`): `li a7, SYS_write (16); ecall` → `uservec` in `trampoline.S` saves registers into the trapframe → `usertrap()` sees `r_scause() == 8` → `syscall()`: `num = trapframe->a7`, `trapframe->a0 = syscalls[num]()` → `sys_write` reads args with `argfd`/`argaddr`/`argint` → `filewrite` → device → `consolewrite` → `uartwrite` → `prepare_return()`/`userret` → back in user space, return value in `a0`.
</details>

### 18 ★ (T) `trace 32 grep hello README` printed only `read` lines. Why not `open` and `close`? Which mask traces exactly open and close?

<details><summary>Answer</summary>

32 = 2⁵, only bit 5 is set, and `SYS_read = 5`. `syscall()` prints only when `(p->trace_mask >> num) & 1`. `open` is 15, `close` is 21: their bits are 0. Open + close: 2¹⁵ + 2²¹ = 32768 + 2097152 = **2129920**. Measured: reads 1023, 965, 453, 0 (= 2441 bytes of README, then EOF).
</details>

### 19 (T) In `forkforkfork` under `trace`, several PIDs print lines. Which single line makes that possible? And why does `trace` keep tracing after `exec`?

<details><summary>Answer</summary>

`np->trace_mask = p->trace_mask;` in `kfork()` (`kernel/proc.c`). Children inherit the mask. `kexec` replaces memory but keeps the `struct proc`, so the mask stays. Lab 10 saw PIDs 6–11 and `fork -> 67`, then −1 when the 64-entry process table was full.
</details>

### 20 (P) `trace 65536 echo hi` (bit 16 = write). Write the console output in order.

<details><summary>Answer</summary>

```
hi68: syscall write -> 2

68: syscall write -> 1
```
i.e. `hi`, then the trace line, then the newline, then the second trace line. `echo` writes the argument and the `\n` in two calls; the kernel prints after each call returns. (PID may differ.)
</details>

### 21 (T) Lab 10 `sysinfo`: after `fork` free memory fell by 10 pages, after `sbrk(40960)` by 10 more, after `wait` it rose by 10. Explain each number.

<details><summary>Answer</summary>

`kfork` → `uvmcopy` copies every page of the parent (no copy-on-write in this tree) plus page-table pages, trapframe and kernel stack: 10 pages total for that small process. `sbrk(40960)` = 40960/4096 = 10 pages, eager (`sbrk` in `user/ulib.c` uses `SBRK_EAGER`). The `sbrk` was in the child, so when the parent's `wait` reaped it, `freeproc` returned the child's pages: back to 32522 pages. A bad pointer makes `copyout` fail → −1.
</details>

### 22 (T) Lab 9: why does the first `openat` return 3? How did you make it return 0?

<details><summary>Answer</summary>

0, 1, 2 are inherited open from the shell through fork and exec, and the kernel returns the lowest free number, so 3. Run with stdin closed: `./syscalls 0<&-` → `open` returns 0.
</details>

---

## D. File system

### 23 (D) Draw the xv6 disk layout with block numbers.

<details><summary>Answer</summary>

```
| 0    | 1     | 2 ... 32        | 33 ... 45        | 46     | 47 ... 1999 |
| boot | super | log (31 blocks) | inodes (13 blks) | bitmap | data (1953) |
```
`BSIZE 1024`, `FSSIZE 2000`, `LOGBLOCKS 30` + 1 header, 200 inodes / 16 per block (+1) = 13, bitmap 2000/8192 + 1 = 1. mkfs: `nmeta 47 … blocks 1953 total 2000`.
</details>

### 24 (T) What is the largest xv6 file? Show the computation.

<details><summary>Answer</summary>

`NDIRECT = 12` direct blocks + `NINDIRECT = BSIZE/sizeof(uint) = 1024/4 = 256` via the indirect block = `MAXFILE` 268 blocks × 1024 = **274 432 bytes**. `bmap()` maps logical block `bn`: `< 12` → `addrs[bn]`; else index `bn − 12` in block `addrs[12]`.
</details>

### 25 (T) After `ln README r2; rm README`, can you still `cat r2`? When are README's data blocks freed?

<details><summary>Answer</summary>

Yes. Both names pointed to inode 2 (links 2). `rm` → `sys_unlink` removes the directory entry and does `ip->nlink--; iupdate(ip)`, links 1. Blocks are freed only in `iput()` when `ref == 1 && nlink == 0` (calls `itrunc`). Lab 6 measured `cat r2 | wc` = `48 334 2425` after the rm.
</details>

### 26 (T) Why is an empty xv6 directory 32 bytes? Why does `mkdir averyveryverylongname` show as `averyveryveryl`?

<details><summary>Answer</summary>

`struct dirent { ushort inum; char name[14]; }` = 16 bytes; a new directory holds `.` and `..` = 32. `DIRSIZ = 14`, so longer names are cut at 14 bytes.
</details>

### 27 (T) What does the log (blocks 2–32) protect against, and which functions bracket a file-system operation?

<details><summary>Answer</summary>

A crash in the middle of a multi-block update (e.g. bitmap written, inode not). Each system call wraps its changes in `begin_op()` … `end_op()`; `log_write()` records blocks; `commit()` writes them to the log, then the header, then installs them in place. At boot `recover_from_log()` replays a committed log or ignores an uncommitted one: all or nothing.
</details>

---

## E. Races and user-space synchronisation

### 28 (T) Write the three instructions of `counter++` and show with a table how one increment is lost.

<details><summary>Answer</summary>

```
movq counter(%rip),%rax   # load
addq $1,%rax              # add
movq %rax,counter(%rip)   # store
```
| t | T1 | T2 | memory |
|---|---|---|---|
| 1 | load 500 | | 500 |
| 2 | | load 500 | 500 |
| 3 | add → 501 | add → 501 | 500 |
| 4 | store 501 | | 501 |
| 5 | | store 501 | **501** |
Two increments, +1. Lab 17 measured 1 007 358 / 1 470 750 / 1 003 769 of 2 000 000.
</details>

### 29 ★ (T) Why is the race result different on every run, and why does it get worse with more threads?

<details><summary>Answer</summary>

Loss happens only when two load–store windows overlap. That depends on thread start times, core assignment, interrupts, other load and cache-line transfers, none of which repeat exactly. More threads → more overlapping windows: Lab 17 lost 24–49 % with 2 threads, 59–69 % with 4, 77–84 % with 8.
</details>

### 30 (T) Lab 17 thread 2 printed a non-zero counter at start. What does that prove? How did you prove it more directly?

<details><summary>Answer</summary>

Threads share one copy of global memory: thread 2 saw increments only thread 1 made. Directly: all 4 threads in `fire4` printed the same `&counter` (0x5646c6cfe030). After `fork`, a child would have its own copy (question 5).
</details>

### 31 ★ (T) Give the meaning of a semaphore that starts at 0, at 1 and at N, with the Lab 11 program for each.

<details><summary>Answer</summary>

- **0 = signal / order:** "the event has not happened yet"; the waiter sleeps until someone posts (`order.c`).
- **1 = lock (binary semaphore, mutex):** one thread in the critical section (`sem.c`, always 2 000 000).
- **N = counter of resources:** at most N inside (`parking.c`, PLACES 3, max `inside: 3`; with 1 place it degenerates into a mutex, 6.004 s instead of 2.003 s).
</details>

### 32 (P) `sem.c` with `sem_init(&s, 0, 2)` and two threads each doing 1 000 000 `sem_wait; counter++; sem_post`. Is the result 2 000 000?

<details><summary>Answer</summary>

No. Both threads pass `sem_wait` (2→1→0), so nothing excludes anyone; the race is back. Measured 1993053, 1838146, 1672013. It loses less than `race` only because the semaphore calls space the increments out.
</details>

### 33 (P) `order.c` with the semaphore started at 1 instead of 0. Output?

<details><summary>Answer</summary>

```
B: waiting for the message...
B: I read ""
A: message written
```
B's `sem_wait` takes the unit at once, a second before A writes. `message` is a zeroed global → empty string.
</details>

### 34 (T) Why is the mutex version slower than the race, and why is the atomic one faster than the mutex? Use your numbers.

<details><summary>Answer</summary>

Lab 11: race 0.009 s (wrong), atomic 0.076 s, mutex 0.232 s, sem 0.267 s. Each lock/unlock is an atomic read-modify-write that bounces the cache line between cores; when the lock is taken the thread sleeps via `futex` and is woken by another `futex` (10 759 futex calls vs 2; sys time 0 → 0.140 s); and the critical section serialises the threads. `atomic_fetch_add` is one `lock addq` instruction: no sleep, no kernel entry, ~3× faster than the mutex.
</details>

### 35 (B) Producer code. What happens when the buffer is full?

```c
pthread_mutex_lock(&lock);
sem_wait(&empty);
buf[in] = item; in = (in + 1) % SIZE;
pthread_mutex_unlock(&lock);
sem_post(&full);
```

<details><summary>Answer</summary>

Deadlock. Buffer full → `empty == 0` → the producer sleeps in `sem_wait(&empty)` **holding the mutex**. The consumer passes `sem_wait(&full)` and blocks on `pthread_mutex_lock`, so it can never `sem_post(&empty)`. Lab 12: `put 1`–`put 4`, then nothing, `timeout` exit **124**. Fix: `sem_wait(&empty)` first, then lock.
</details>

### 36 ★ (T) In `pthread_cond_wait` code, why `while (!ready)` and not `if (!ready)`? What does the condition variable itself remember?

<details><summary>Answer</summary>

The condvar remembers nothing (a signal with no waiter is lost); the state is `ready`, protected by the mutex. A thread can return from `pthread_cond_wait` with `ready == 0`: spurious wake-ups are allowed by POSIX, and between the signal and re-acquiring the mutex another thread may consume the condition (or a broadcast woke several for one item). `while` re-checks. In Lab 12 `if` happened to work (one writer, one reader). Same reason as `while (s->value == 0)` in the kernel `sem_down` (question 40).
</details>

### 37 (T) Readers–writers (`readers.c`). Which two lines let many readers in but keep writers alone? What happens if readers never stop arriving?

<details><summary>Answer</summary>

`if (++readers == 1) sem_wait(&room);` and `if (--readers == 0) sem_post(&room);`, both inside `rlock`. The first reader takes the room for the whole group; the last one returns it. A writer needs `room` alone. Continuous readers keep `readers > 0`, so `room` is never posted: the writer **starves** (not a deadlock; the system keeps working). Fix: a turnstile semaphore taken by waiting writers.
</details>

### 38 (D) Draw the wait-for cycle of Lab 12's deadlock and state the four conditions. Which one does lock ordering break?

<details><summary>Answer</summary>

```
 one ──holds──► A        one ──waits for──► B
 two ──holds──► B        two ──waits for──► A
     one → B → two → A → one   (closed cycle)
```
Conditions: mutual exclusion, hold and wait, no preemption, circular wait. Lock ordering (everyone takes A before B) breaks **circular wait**: a holder only waits for a later lock, so the chain cannot close. Lab 12 fixed version: both `I have both`, `done`, exit 0.
</details>

### 39 (T) Without the `sleep(1)` lines the deadlock appeared in only some runs, and never on one CPU. Why is that worse?

<details><summary>Answer</summary>

Lab 12: 4/10 hung on 12 CPUs (53, 72, 68 of 100 in three sessions); 0/100 with `taskset -c 0`. On one CPU a thread usually takes both locks before being preempted. The code is equally wrong, but the bug is now intermittent: tests pass, it hangs later, and a hang that does not repeat is very hard to debug.
</details>

---

## F. Kernel: spinlocks, sleep/wakeup, semaphores, UART

### 40 ★ (T) Lab 13 `sem_down` uses `while (s->value == 0)`. Why can a process wake up and still find 0? What did the `if` experiment show?

<details><summary>Answer</summary>

`wakeup(s)` wakes **every** process with `p->chan == s`, but `sem_up` adds only 1. The first one to re-acquire `s->lock` takes it to 0; the others must see 0 and sleep again. Also, a process that was not sleeping can grab the unit first, and `sleep()` can return because of a kill. Experiment `wakeall.c`: 3 children asleep, one `sem_up` → with `if`, all three passed and the value went to **−2**; with `while`, exactly one passed.
</details>

### 41 (T) Why does `sem_down` release the spinlock before `sleep()`? What happened when you removed that release? Why is a wakeup not lost in the gap?

<details><summary>Answer</summary>

(a) `sem_up` needs `s->lock` to increment and wake; a sleeper holding it would make `sem_up` spin forever. (b) `sched()` panics unless the only lock held is `p->lock` (`mycpu()->noff != 1` → `panic("sched locks")`); that is exactly what Lab 13 got. No lost wakeup: `sleep_prepare(s)` sets `p->chan = s` *while still holding the lock*; if `sem_up` runs between `release` and `sleep()`, `wakeup` sets `p->chan = 0`, and `sleep()` sees 0 and returns at once.
</details>

### 42 (T) Why does `acquire` disable interrupts? What instruction does the spin use?

<details><summary>Answer</summary>

If code holding a lock is interrupted on the same CPU and the handler tries the same lock (e.g. `tickslock` in `clockintr`, `tx_lock` in `uartintr`), the handler spins forever because the holder cannot run: deadlock on one CPU. `push_off()` disables them (nested count `noff`). The spin is `__atomic_exchange_n(&lk->locked, 1, __ATOMIC_ACQUIRE)` = RISC-V `amoswap.w.aq`; `release` is `__atomic_store_n(..., 0, __ATOMIC_RELEASE)` = `fence rw,w; sw zero`.
</details>

### 43 (P) Lab 13 `mix` without the lock: what kind of output, and how many system calls per line? With `mix lock`?

<details><summary>Answer</summary>

Each line is 30 letters + `\n` = 31 bytes written one byte per `write` = **31 system calls** (155 per process). `uartwrite` holds `tx_lock` only for one call's bytes, nothing holds a line together, and the two processes run on different harts (CPUS=3) or are switched by the timer. Output like `AAAAAAAbAAAAbAAAbbAbbbb…`, different each run. With `sem_down(3)`/`sem_up(3)` around the 31 writes (sem 3 starts at 1) every line is whole; only the order of whole lines varies (e.g. `AA bbb A bb AA`).
</details>

### 44 (T) Describe how a byte gets out of the xv6 UART when a user process writes, and where the process sleeps.

<details><summary>Answer</summary>

`consolewrite` copies up to 32 bytes from user space and calls `uartwrite(buf, n)`. `uartwrite` holds `tx_lock`; for each byte, while `tx_busy` it does `sleep_prepare(&tx_chan); release; sleep(); acquire`; then writes the byte to `THR` and sets `tx_busy = 1`. When the UART finishes, it raises an interrupt; `uartintr()` sees `LSR_TX_IDLE`, sets `tx_busy = 0` and `wakeup(&tx_chan)`. Kernel `printk` instead uses `uartputc_sync`, which spins on `LSR` with interrupts off.
</details>

---

## G. Scheduling, context switch, threads

### 45 ★ (T) What exactly does `thread_switch` (Lab 18) / `swtch` save and load? Why is `ra` the register that makes execution continue in the other thread? Why not save `a0–a7` or the PC?

<details><summary>Answer</summary>

It stores `ra, sp, s0..s11` (14 registers, offsets 0–104) into `*old` (`a0`), loads the same 14 from `*new` (`a1`), and `ret`. `ret` = jump to `ra`; after the loads `ra` is the *new* thread's saved return address, so a call made by one thread returns in another. First switch: `ra` = the thread function (set in `thread_create`); later: the instruction after `jal thread_switch` in `thread_schedule` (0x10E in the trace build). `sp` is loaded with it so that code finds its own stack. `a0–a7`, `t0–t6` are caller-saved: the C caller already assumes a call destroys them. The PC need not be saved: it is the same instruction inside `thread_switch` for everyone, and `ra` plays its role.
</details>

### 46 (B) `thread_create` below. What happens on the first switch into this thread? And if only `ra` was set?

```c
t->state = RUNNABLE;
t->ctx.ra = (uint64)func;
t->ctx.sp = (uint64)t->stack;
```

<details><summary>Answer</summary>

`sp` points to the **bottom** of the stack array. Stacks grow downward, so the function's first `addi sp,sp,-N; sd ra,…(sp)` writes *below* the array, into the previous thread's struct (`all_thread[i-1]`, or other globals for thread 0), corrupting it silently. Correct: `t->stack + STACK_SIZE`. Lab 18 experiments: `sp` left 0 → `usertrap(): unexpected scause 0xf` (store page fault), `stval=0xfffffffffffffff8`; `ra` left 0 → jumps to address 0 (`thread_init`), silent infinite loop.
</details>

### 47 (P) Lab 18 output: why does `thread_c 0` print before `thread_a 0`?

<details><summary>Answer</summary>

`main` switches to a; a prints `started` but b and c have not started, so it yields to b; b prints `started` and yields to c; c prints `started`, finds both flags set and enters its loop first. From then on round robin: c 0, a 0, b 0, c 1, … , 300 numbered lines, `thread_c: exit after 100`, then a, b, `thread_schedule: no runnable threads`.
</details>

### 48 (T) Explain how xv6 takes the CPU away from a process that loops forever without system calls. Name the functions.

<details><summary>Answer</summary>

The timer interrupt. `clockintr()` reprograms `stimecmp = time + 1000000` (~0.1 s in QEMU) and increments `ticks`; `devintr()` returns 2; `usertrap()` (or `kerneltrap()`) does `if (which_dev == 2) yield();`. `yield()`: `acquire(&p->lock); p->state = RUNNABLE; sched();`. `sched()` checks the locks and `swtch(&p->context, &mycpu()->context)` back into `scheduler()`, which continues its round-robin scan of `proc[]` and `swtch`es to the next `RUNNABLE` process. That forced switch is preemption.
</details>

### 49 (T) User-level threads (Lab 18) vs kernel threads (pthreads, Lab 17): give three differences.

<details><summary>Answer</summary>

1. Switching: user-level is a function call in user space (no `ecall`); kernel threads switch inside the kernel on a timer or block.
2. Scheduling: Lab 18 is cooperative (runs until `thread_yield`); pthreads are preemptive.
3. Parallelism and blocking: xv6 sees one process, so a, b, c never run on two harts at once, and one thread blocking in a system call blocks all; pthreads run on several cores (which is why Lab 17 raced) and block independently.
</details>
