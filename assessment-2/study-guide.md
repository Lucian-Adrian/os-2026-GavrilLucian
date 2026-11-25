# OS assessment 2: study guide

FAF-241, Mon 30 Nov 2026, 15:15. Scope: everything since assessment 1 (Labs 7–18; Labs 14–16 do not exist in this repository). The format is unknown, so each topic gives (a) the idea in plain words, (b) where xv6 implements it, (c) what your own labs measured. Practise with [practice.md](practice.md); print [cheatsheet.pdf](cheatsheet.pdf).

**Which xv6.** Our tree is a *newer* mit-pdos xv6-riscv than the xv6 book. Kernel functions are renamed and sleeping is two-step. When the exam shows book code, recognise both spellings:

| Book / MIT 6.1810 | Our tree (`lab18/xv6-riscv/kernel`) |
|---|---|
| `fork`, `exit`, `wait`, `kill`, `exec` | `kfork`, `kexit`, `kwait`, `kkill`, `kexec` (in `proc.c`, `exec.c`); `sys_fork` just calls `kfork` |
| `sleep(chan, lock)` | `sleep_prepare(chan)` while holding the lock → `release(lock)` → `sleep()` → `acquire(lock)` |
| `printf` in the kernel | `printk` |
| `sleep` system call (13) | `pause` (13); `SYS_sync` = 22 |

All paths below are relative to `lab18/xv6-riscv/` unless they start with `labN/`.

---

## 1. Processes: fork, exec, wait, exit, zombies

**Idea.** A shell runs a command in three steps: `fork` copies the process, the child calls `exec` to replace its program, the parent calls `wait` to collect the child's exit status.

- `fork()` returns **twice**: the child's PID in the parent, **0** in the child, −1 on failure. The child gets a *copy* of memory (changes are not seen by the other process), a copy of the descriptor table (same open files, shared offsets) and the same current directory.
- `exec` keeps the PID, the open descriptors and (in our xv6) the trace mask; it replaces code, data, stack. On success it **never returns**. Any line after `exec` runs only if exec failed.
- `exit(status)` closes files, becomes a **ZOMBIE** and waits for the parent. A zombie runs no code; it only keeps the PID and exit status until the parent's `wait` frees it.
- If the parent exits first, the children are **orphans** and are handed to `init` (`reparent()`), which reaps them.

**xv6 code.**
- `kfork()` (`kernel/proc.c`): `allocproc()` → `uvmcopy()` copies memory page by page (no copy-on-write in this tree) → `*(np->trapframe) = *(p->trapframe)` → `np->trapframe->a0 = 0` (this is why the child sees 0) → `filedup()` each open file → `idup(p->cwd)` → `np->trace_mask = p->trace_mask` → state `RUNNABLE`.
- `kexit()`: closes `ofile[]`, `iput(p->cwd)`, `reparent(p)`, `wakeup(p->parent)`, sets `xstate`, `state = ZOMBIE`, `sched()` and never returns (`panic("zombie exit")`).
- `kwait()`: scans `proc[]` for children; a `ZOMBIE` child → `copyout` of `xstate`, `freeproc()`, return its pid. No children → −1. Otherwise `sleep_prepare(p)`; `sleep()`.
- Process states: `enum procstate { UNUSED, USED, SLEEPING, RUNNABLE, RUNNING, ZOMBIE }` (`kernel/proc.h`). `NPROC = 64` (`kernel/param.h`).

**Linux vs xv6.** Linux `execlp` searches `PATH`; xv6 `exec(path, argv)` does not. Linux `wait` status is encoded (`exit(3)` arrives as raw 768 = 3<<8; use `WEXITSTATUS`); xv6 copies the plain integer.

**Your measurements.**
- Lab 7 (`lab7/run.c`, `lab7/report.md`): `ls` child status 0; `nosuchprog` → `exec: No such file or directory`, status **127** (chosen by the child's `exit(127)`, not by exec). Parent PID 1795, child 1796 with PPID 1795.
- Lab 7 (`lab7/zombie.c`): child 1894 shown as `Z+`, `[ls] <defunct>` while the parent slept 20 s; gone after `waitpid`.
- Lab 8 (`lab8/notes.md`): xv6 `run` printed `parent pid: 3`, `child pid: 4`, `hello from the child`, `child 4 ended with status 0`; missing program → status **1** (the child's `exit(1)`).
- Lab 10 (`lab10/notes.txt`): `forkforkfork` under `trace` reached `fork -> 67` then `-1`: process table full (NPROC = 64).
- Verified on Linux (this machine): `printf("hello "); fork(); printf("world\n");` prints `hello world` **twice**, even on a terminal, because the unflushed "hello " is copied with the stdio buffer. `printf("A\n"); fork(); printf("B\n");` prints `A B B` on a terminal but `A B A B` into a pipe (full buffering). Three `fork()`s in a row → 2³ = 8 processes.

---

## 2. Descriptors, redirection, pipes

**Idea.** A descriptor is an index into the process's table of open files. 0 = stdin, 1 = stdout, 2 = stderr, inherited from the shell. **Every call that creates a descriptor takes the lowest free number.** Redirection = close a number, then open/dup so the new file lands on that number, then exec. The program never knows.

- `ls > out.txt` = `close(1); open("out.txt", O_WRONLY|O_CREAT|O_TRUNC)` → returns 1 → `exec ls`.
- `2> err.txt`: the same with `close(2)`.
- `a | b`: `pipe(p)`; child 1: `close(1); dup(p[1])`; child 2: `close(0); dup(p[0])`; **everyone closes both original ends**; parent waits twice.
- A pipe read blocks while the pipe is empty **and a writer exists**. It returns 0 (EOF) only when the buffer is empty **and every write end is closed** in every process. One forgotten write end → the reader hangs forever.
- Writing to a full pipe blocks until the reader takes bytes.

**xv6 code.**
- `fdalloc()` (`kernel/sysfile.c`): `for (fd = 0; fd < NOFILE; fd++) if (p->ofile[fd] == 0) ...` – the "lowest free" rule. `NOFILE = 16` per process, `NFILE = 100` system-wide.
- `sys_dup()` → `fdalloc(f)` + `filedup(f)` (ref count++). `struct file` (`kernel/file.h`): `type` (`FD_PIPE`, `FD_INODE`, `FD_DEVICE`), `ref`, `readable`, `writable`, `pipe`, `ip`, `off`.
- `kernel/pipe.c`: `PIPESIZE 512`, circular `data[]`, counters `nread`, `nwrite`, flags `readopen`, `writeopen`. `pipewrite` sleeps on `&pi->nwrite` when `nwrite == nread + PIPESIZE` (full); `piperead` sleeps on `&pi->nread` while `nread == nwrite && writeopen`; returns 0 when empty and `writeopen == 0`. `pipeclose` clears a flag and wakes the other side.
- Shell: `user/sh.c`, `case PIPE:` is exactly the pattern above (`fork1`, `close(1); dup(p[1]); close(p[0]); close(p[1]); runcmd(left)` …, then the parent closes both and `wait(0); wait(0)`).

**Your measurements.**
- Lab 7 (`lab7/redirect.c`): `open` returned **1** after `close(1)`; the listing went to `out.txt`, the diagnostic on fd 2 stayed on the terminal.
- Lab 7 (`lab7/pipeline.c`): hand-made `ls /etc | wc -l` = **172** = shell result. Leaked-writer variant: `wc` (PID 2007) stayed blocked after `ls` ended. `pipeline3.c` (`ls /usr/bin | grep x | wc -l`) = **108**.
- Lab 8 (`lab8/user/pingpong.c`): two pipes, one per direction; `10: received ping`, `9: received pong`. Lab 8 `primes.c`: 11 primes from 2..35, one process and one pipe per prime.
- Lab 9 (`lab9/report.md`): first `openat` returns **3**; with stdin closed (`./syscalls 0<&-`) it returns **0**.
- Verified on Linux: pipe capacity **65536** bytes (non-blocking fill). xv6's is 512.

---

## 3. System calls: the path into the kernel, strace, trace, sysinfo

**Idea.** A user program cannot touch kernel memory. It puts the call number in `a7`, arguments in `a0..a5`, and executes `ecall`. The CPU traps into supervisor mode; the kernel looks up the number in a table, runs the handler, and puts the return value in `a0`.

**Path in xv6.** `user/usys.pl` generates `user/usys.S` stubs: `li a7, SYS_x; ecall; ret` → `uservec` (`kernel/trampoline.S`, saves registers in the trapframe) → `usertrap()` (`kernel/trap.c`, `r_scause() == 8` means ecall from user) → `syscall()` (`kernel/syscall.c`): `num = p->trapframe->a7; p->trapframe->a0 = syscalls[num]();` → handler reads arguments with `argint`/`argaddr`/`argstr` (via `argraw`, which reads `trapframe->a0..a5`) → `prepare_return()` → `userret`. Unknown number → `printk("%d %s: unknown sys call %d\n" …)`, `a0 = -1`.

**Adding a call (Lab 10 recipe, 5 places):** `kernel/syscall.h` (number), `user/user.h` (prototype), `user/usys.pl` (`entry("trace")`), `kernel/syscall.c` (`extern` + table entry), the handler (`sys_trace` in `kernel/sysproc.c`), plus `Makefile` UPROGS for the user program.

**Numbers in our tree** (`kernel/syscall.h`): fork 1, exit 2, wait 3, pipe 4, **read 5**, kill 6, exec 7, fstat 8, chdir 9, dup 10, getpid 11, sbrk 12, pause 13, uptime 14, **open 15**, **write 16**, mknod 17, unlink 18, link 19, mkdir 20, **close 21**, sync 22, **trace 23**, sem_init 24, sem_down 25, sem_up 26, sem_trydown 27, sysinfo 28 (moved from 24 in Lab 13).

**trace.** `struct proc` gets `int trace_mask`. `sys_trace` stores `argint(0)` there. After the call returns, `syscall()` prints if `(p->trace_mask >> num) & 1`. `kfork` copies the mask; `kexec` does not touch it, so `trace 32 grep ...` traces grep.

**Your measurements.**
- Lab 9 (`lab9/report.md`, strace on Linux): `ls -l` = 87 calls with filter (39 openat, 33 close, 14 read, **1 write** on fd 1), 214 without; `./syscalls` 41 calls, 6 from `main`; `seq 1 100000` = 72 writes (588 895 bytes); the same printf program = **1 write into a pipe, 3 on a terminal** (stdio buffering).
- Lab 10 (`lab10/notes.txt`): before the kernel side: `3 trace: unknown sys call 23`. `trace 32 grep hello README` → reads **1023, 965, 453, 0** (sum 2441 = README size). Mask for open + close only = 2¹⁵ + 2²¹ = **2129920**. `trace 65536 echo hi` prints the trace line between `hi` and the newline because echo does two writes and the kernel prints after each.
- Lab 10 sysinfo: start 32532 free pages, 3 procs; after fork 32522, 4 procs (**child costs 10 pages**); after `sbrk(40960)` 32512 (10 pages); after wait back to 32522; bad pointer → −1 (`copyout` rejects). Note: `sbrk()` in user/ulib.c is eager (`SBRK_EAGER`); `sbrklazy()` exists and defers allocation to `vmfault()`.

---

## 4. File system and the xv6 disk layout

**Idea.** A file is an **inode** (type, link count, size, block addresses). A directory is a file whose content is a list of (inode number, name) entries. A name is only a link; the data is freed when the link count is 0 **and** no process has it open.

**Layout** (`kernel/fs.h`, `mkfs/mkfs.c`, `BSIZE 1024`, `FSSIZE 2000`):

| block | 0 | 1 | 2–32 | 33–45 | 46 | 47–1999 |
|---|---|---|---|---|---|---|
| content | boot | super block | log (31 = header + `LOGBLOCKS` 30) | inodes (13 blocks, 200 inodes, 16 per block) | free bitmap (1) | data (1953) |

mkfs prints: `nmeta 47 (boot, super, log blocks 31, inode blocks 13, bitmap blocks 1) blocks 1953 total 2000` (Lab 6, `lab6/notes.md`).

- `struct dinode`: `type, major, minor, nlink` (shorts), `size`, `addrs[NDIRECT+1]` = 64 bytes → `IPB = 16`. `NDIRECT = 12`, `NINDIRECT = 1024/4 = 256`, `MAXFILE = 268` blocks = **274 432 bytes**.
- `struct dirent`: `ushort inum; char name[DIRSIZ=14]` = 16 bytes. Empty directory = 32 bytes (`.` and `..`). Root inode `ROOTINO = 1`. Types (`kernel/stat.h`): 1 dir, 2 file, 3 device.
- Layers (bottom up): `virtio_disk.c` → buffer cache `bio.c` (`bread`, `bwrite`, `brelse`, `NBUF = 30`) → log `log.c` (`begin_op`, `log_write`, `end_op`/`commit`, crash recovery `recover_from_log`) → inodes `fs.c` (`ialloc`, `iget`, `ilock`, `iput`, `bmap`, `readi`, `writei`, `itrunc`) → directories (`dirlookup`, `dirlink`) → paths (`namei`, `nameiparent`, `namex`) → descriptors (`file.c`, `sysfile.c`).
- `bmap(ip, bn)`: `bn < 12` → `addrs[bn]`; otherwise read the indirect block `addrs[12]`; allocates with `balloc` on demand.
- `sys_unlink` does `ip->nlink--; iupdate(ip)`; blocks are freed later in `iput()` when `ref == 1 && nlink == 0` (`itrunc`).
- Locks here: `bcache` spinlock + per-buffer **sleeplock**; per-inode sleeplock in `ilock`. Sleeplocks are used because disk I/O is slow and a spinlock may not be held across `sleep`.

**Your measurements (Lab 6, before assessment 1, still asked).** `ln README r2` → both show inode 2, links 2; `rm README` → r2 links 1, content intact (`cat r2 | wc` = `48 334 2425`). `mkdir averyveryverylongname` → stored as `averyveryveryl` (14 chars).

---

## 5. Races

**Idea.** `counter++` is three instructions: **load, add, store**. Two threads can both load the same old value; both store old+1; one increment is lost. The result depends on timing, so it changes every run. Threads share globals (one copy); after `fork` each process has its own copy.

**Your measurements.**
- `gcc -S` (Lab 11, Lab 17 `evidence/1_asm.txt`): `movq counter(%rip),%rax` / `addq $1,%rax` / `movq %rax,counter(%rip)`.
- Lab 11 `race`: 1214868, 1085564, 1031688, 1019785, 1014123 (expected 2 000 000).
- Lab 17 `fire`: 1 007 358 / 1 470 750 / 1 003 769. Loss grows with threads: 2 thr 24–49 %, 4 thr 59–69 %, 8 thr 77–84 %; the final value stays ~1.2–1.8 M.
- Lab 17 proof of shared memory: all 4 threads printed the same `&counter` (0x5646c6cfe030); thread 2 saw a non-zero counter in 21 of 200 runs.
- Lab 17 `taskset -c 0` (one core): 2 000 000 three times, but `fire4` once gave **2 000 000 instead of 4 000 000**: a thread preempted between load and store wiped out a whole million of another thread.
- Lab 17 `-O2`: always correct, because the loop became one `addq $1000000, counter(%rip)`. The race is still there; correct output is not proof of correct code.

---

## 6. Mutex, semaphore, atomic

**Idea.** A **critical section** is code that only one thread may run at a time. Tools:

- **Mutex**: lock/unlock; the owner unlocks.
- **Semaphore**: an integer ≥ 0. `wait`/`down`/P: if 0, sleep; then decrement. `post`/`up`/V: increment, wake a sleeper. The start value decides the role: **1 = lock**, **0 = signal/order** ("not happened yet"), **N = counter of N resources**.
- **Atomic**: one hardware read-modify-write (`lock addq` on x86, `amoswap`/`amoadd` on RISC-V). Fastest for one counter; no sleeping.

**Your measurements (Lab 11, `lab11/report.md`).** mutex and sem: always 2 000 000. `sem_init(&s,0,2)`: wrong again (1993053, 1838146, 1672013). Times: race 0.009 s (wrong), atomic 0.076 s, mutex 0.232 s, sem 0.267 s. Why slower: atomic RMW per lock, cache line moves between cores, and contention → `futex` system calls (**10 759 futex calls** for mutex vs 2 for race; sys time 0.000 → 0.140 s). `order.c` with start 1: B reads `""` (semaphore said "ready" too early). Parking with 3 places: max inside **3**, runtime 2.003 s; with 1 place: becomes a mutex, 6.004 s.

Lab 17 `fix.c`: mutex around `counter++`, 4 threads → exactly 4 000 000, 0.222 s vs 0.007 s (~30× slower).

---

## 7. Producer–consumer, condition variables, readers–writers, deadlock

**Producer–consumer (bounded buffer, `lab12/prodcons.c`).** `empty = SIZE` (free slots), `full = 0` (filled slots), `lock` (mutex) protects `buf`, `in`, `out`. Producer: `sem_wait(&empty); lock; put; unlock; sem_post(&full)`. Consumer mirrors it. **Order rule: semaphore wait first, mutex second.** Swapped (`prodcons_swapped`): `put 1..4`, then deadlock; `timeout` exit code **124**. The producer sleeps in `sem_wait(&empty)` holding the mutex the consumer needs.

**Condition variable (`lab12/condvar.c`).** The state lives in an ordinary variable (`ready`) protected by the mutex; the condvar remembers nothing (a signal with no waiter is lost). Pattern: `lock; while (!ready) pthread_cond_wait(&c, &lock); ... unlock`. `pthread_cond_wait` atomically unlocks + sleeps, and relocks before returning. Use **while**: spurious wake-ups are allowed, and another thread may take the condition between the signal and the relock. (`if` happened to work in the lab: one writer, one reader.)

**Readers–writers (`lab12/readers.c`).** `rlock` protects the counter `readers`; `room` is held by the first reader in (`if (++readers == 1) sem_wait(&room)`) and released by the last one out (`if (--readers == 0) sem_post(&room)`). Writers take `room` alone. Readers-preferring: a constant stream of readers **starves** the writer. Fix: a turnstile semaphore.

**Deadlock (`lab12/deadlock.c`).** Four conditions (Coffman): mutual exclusion, hold and wait, no preemption, **circular wait**. Lab: `one` holds A wants B, `two` holds B wants A → exit 124. Fix: **lock ordering** (everyone takes A then B), breaks the circle. Without `sleep(1)`: hung in 4/10 runs (and 53, 72, 68 of 100 in three sessions), **0 of 100 on one CPU** (`taskset -c 0`). Intermittent is worse: tests pass, production hangs.

Deadlock vs starvation: deadlock = nobody can move, ever; starvation = the system moves but one thread never gets its turn.

---

## 8. Kernel locks, sleep/wakeup, kernel semaphores, UART (Lab 13)

**Spinlocks** (`kernel/spinlock.c`). `acquire`: `push_off()` (disable interrupts), panic if already `holding`, spin on `__atomic_exchange_n(&lk->locked, 1, __ATOMIC_ACQUIRE)` (RISC-V `amoswap.w.aq`), record `lk->cpu`. `release`: `__atomic_store_n(&lk->locked, 0, __ATOMIC_RELEASE)` (a `fence` then store), `pop_off()`. Why interrupts off: an interrupt handler on the same CPU that wants the same lock would spin forever. `push_off`/`pop_off` nest via `mycpu()->noff`, restoring `intena` at the outermost.

**Sleep and wakeup** (`kernel/proc.c`, our two-step version).
- `sleep_prepare(chan)`: under `p->lock`, `p->chan = chan`.
- `sleep()`: under `p->lock`, if `p->chan != 0` → `state = SLEEPING; sched()`. If a wakeup already cleared `chan`, it returns immediately: **no lost wakeup**.
- `wakeup(chan)`: for every proc with `p->chan == chan` → `chan = 0`, and if `SLEEPING` → `RUNNABLE`. It wakes **all** sleepers on that channel.
- Pattern: `acquire(lk); while (!cond) { sleep_prepare(x); release(lk); sleep(); acquire(lk); }`. Used in `pipe.c`, `kwait`, `sys_pause`, `uartwrite`, `acquiresleep`, `sem.c`.

**Sleeplock** (`kernel/sleeplock.c`): `acquiresleep` = spinlock-protected `locked` flag + sleep while held. For long holds (disk); may only be used in process context.

**Kernel semaphores** (`kernel/sem.c`, Lab 13): `NSEM 8` global `struct sem { struct spinlock lock; int value; }`. `sys_sem_down`: `acquire; while (value == 0) { sleep_prepare(s); release; sleep(); acquire; if (killed) return -1; } value--; release`. `sys_sem_up`: `acquire; value++; wakeup(s); release`. `sem_trydown` returns −1 instead of sleeping.

**UART / console.** `write(1, …)` → `consolewrite()` (`kernel/console.c`, copies up to 32 bytes at a time, takes no lock) → `uartwrite()` (`kernel/uart.c`): holds `tx_lock`, writes one byte to `THR`, sets `tx_busy = 1`, then sleeps on `tx_chan` until the UART's transmit interrupt runs `uartintr()` → `tx_busy = 0; wakeup(&tx_chan)`. Kernel `printk` uses `uartputc_sync` (spins, no interrupts). User `printf` in xv6 (`user/printf.c`) does **one `write` per character**, so output of two processes interleaves character by character.

**Your measurements (`lab13/notes.txt`, `lab13/evidence/`).**
- Before the kernel side: `unknown sys call 24/25`, and the child line came **before** the parent line.
- `semtest`: parent, child, ping/pong ×3, `semtest: OK` on every run; Ctrl-P during `pause(10)` shows both processes `sleep` (no CPU used).
- `mix`: one line = 31 bytes = **31 system calls**; no lock → `AAAAAAAbAAAAbAAAbbAbbbb…`; with `sem_down(3)`/`sem_up(3)` around the line (sem 3 starts at 1) every line is whole, but the order of lines still varies.
- `if` instead of `while` (`experiments/wakeall.c`): three children sleep, one `sem_up` → **all three pass**, value goes to −2.
- Sleeping while holding the spinlock (`experiments/sleep-holding-lock.diff`): **`panic: sched locks`** (`sched()` requires `mycpu()->noff == 1`, i.e. only `p->lock`).
- `sem_trydown(4)` after `sem_init(4,2)`: 0, 0, −1.

---

## 9. Scheduling and the kernel context switch

**Idea.** Each CPU runs a loop that picks a RUNNABLE process and switches to it. The process gives the CPU back either voluntarily (sleep, exit, wait) or because the **timer interrupt** forces `yield()`. That forced give-back is **preemption**; xv6 scheduling is **round-robin** over `proc[]`.

**xv6 code.**
- `scheduler()` (`kernel/proc.c`): per CPU, forever: `intr_on(); intr_off();` scan `proc[0..63]`, `acquire(&p->lock)`; if `RUNNABLE` → `state = RUNNING; c->proc = p; swtch(&c->context, &p->context)`; back here when the process switches out; `release`. Nothing runnable → `wfi`.
- `sched()`: checks `holding(&p->lock)`, `noff == 1` ("sched locks"), `state != RUNNING`, interrupts off; then `swtch(&p->context, &mycpu()->context)`.
- `yield()`: `acquire(&p->lock); state = RUNNABLE; sched(); release`.
- Timer: `start.c` and `clockintr()` program `stimecmp = time + 1000000` (about 0.1 s in QEMU); `ticks++`; in `usertrap()`/`kerneltrap()`, `if (which_dev == 2) yield();`.
- `swtch` (`kernel/swtch.S`): `sd` 14 registers (`ra, sp, s0..s11`, offsets 0..104) into `*a0`, `ld` 14 from `*a1`, `ret`. `struct context` in `kernel/proc.h`. Only callee-saved registers: `swtch` is called like a C function, so the caller already assumes `a0–a7`, `t0–t6` are destroyed. User registers are in the trapframe, not in the context.
- A new process starts in `forkret()` because `allocproc` sets `p->context.ra = forkret` (it releases `p->lock`, which the scheduler held, then returns to user space).
- `p->lock` is held across `swtch` *in both directions*: acquired by the side that switches away, released by the side that switches in.

---

## 10. Threads and user-level context switching

**Idea.** A thread = a stack + registers + PC, sharing the address space with the other threads of the process. A context switch only has to save the registers the caller does not save, and load the other thread's set; changing `sp` moves to the other stack, changing `ra` makes `ret` land in the other thread.

**Kernel vs user-level threads.** Kernel (pthreads on Linux): the OS schedules them, they run in parallel on several cores, a blocking call blocks only that thread. User-level (Lab 18 `uthread`): one kernel process, switching done in a library with no system call; **cooperative** (a thread runs until it calls `thread_yield`), no parallelism, and a thread blocked in a system call blocks all of them.

**Lab 18 (`user/uthread.c`, `user/uthread_switch.S`, `lab18/notes.txt`).**
- `struct context` = 14 `uint64`: `ra, sp, s0..s11`.
- `thread_create`: `t->ctx.ra = (uint64)func; t->ctx.sp = (uint64)(t->stack + STACK_SIZE);` (top of stack, because stacks grow down; `STACK_SIZE 8192`, `MAX_THREAD 4`).
- `thread_schedule`: round robin from `current_thread + 1`; `next->state = RUNNING; old = current; current = next; thread_switch(&old->ctx, &next->ctx)`.
- `thread_switch` = 14 `sd`, 14 `ld`, `ret`; the same as `swtch`.
- Output: `thread_a/b/c started`, then **c 0, a 0, b 0, c 1, …**, 300 numbered lines, `thread_c: exit after 100`, …, `thread_schedule: no runnable threads`. c prints first because a and b yield until all three have started; c is the first to find both others started.
- First switch into a thread: `ra` = the function address (0x190 thread_a, 0x244 b, 0x2F8 c in the trace build). Every later switch: `ra = 0x10E`, the instruction after `jal thread_switch` in `thread_schedule`.
- Experiments: `sp = 0` → `usertrap(): unexpected scause 0xf` (store page fault), `stval=0xfffffffffffffff8` (0 − 48 + 40 = −8). `ra = 0` → jumps to address 0 (`thread_init`), silent infinite loop, Ctrl-P shows `run uthread`.

---

## Ten facts to say without looking

1. `fork` returns 0 in the child because `kfork` sets `np->trapframe->a0 = 0`.
2. A successful `exec` never returns; status 127 / 1 came from the child's own `exit`.
3. Lowest free descriptor: `fdalloc` loop from 0.
4. EOF on a pipe needs every write end closed.
5. Syscall number in `a7`, args in `a0..a5`, result in `a0`; `syscalls[num]()` in `syscall()`.
6. `counter++` = load, add, store; lost update when two loads overlap.
7. Semaphore start value: 1 lock, 0 signal, N resources.
8. Wait on a condition with `while`, not `if`.
9. Deadlock needs a cycle; same lock order everywhere prevents it.
10. A context switch saves `ra, sp, s0..s11`; `ret` jumps to the new `ra`.
