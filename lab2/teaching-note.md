# Lab 2: how a request reaches the xv6 kernel

This lab lets you see both sides of an operating system. Linux lets you observe its resources from the shell. xv6 lets you read a small kernel and the user programs that ask it for services. QEMU imitates a RISC-V machine so xv6 can boot in an emulator. The prompt you see after boot belongs to xv6, not to the host machine.

A program is stored code; a process is a running instance with a PID, memory and open files. The kernel manages processes and protects its own memory and devices. Code in user/ runs with limited privilege. Code in kernel/ performs protected work. A user program crosses that boundary through a system call.

## Follow sleep 3 from the shell to the timer

Suppose you type sleep 3 at the xv6 prompt. The shell turns the command line into a program name and an argument vector: argv[0] is sleep, argv[1] is 3, and argc is 2. The shell creates a child with fork; in the child, user/sh.c:runcmd handles an EXEC command and calls exec(argv[0], argv). fork creates a process, while exec replaces the program in that process. exec does not create another process.

In user/sleep.c:main, the program checks that it received exactly one argument. atoi(argv[1]) converts the string 3 into the integer 3. The call sleep(3) looks like an ordinary C function call, but its user-side declaration in user/user.h corresponds to a generated system-call stub. user/usys.pl lists entry("sleep"), and the Makefile runs Perl to generate user/usys.S. That stub puts the system-call number in the RISC-V a7 register and executes ecall.

The ecall trap moves execution from user mode into the kernel. kernel/trap.c:usertrap recognizes the system-call trap and calls kernel/syscall.c:syscall. The dispatcher reads the number from the process trap frame's a7, looks it up in the table that maps SYS_sleep to sys_sleep, and stores the result in register a0. kernel/syscall.h defines SYS_sleep. This route is why user code can request a protected operation without directly calling a kernel function.

kernel/sysproc.c:sys_sleep reads the integer argument and remembers the current timer count in ticks0. It waits until ticks - ticks0 reaches the requested number. While it waits, it calls kernel/proc.c:sleep(&ticks, &tickslock). This second function named sleep is an internal scheduler helper, not the user system call. It marks the current process SLEEPING and yields the CPU. Holding and handing off the locks around the state change prevents the process from missing a wakeup between checking the condition and going to sleep.

A timer interrupt calls kernel/trap.c:clockintr, which increments ticks and calls wakeup(&ticks). kernel/proc.c:wakeup marks processes waiting on that channel RUNNABLE, meaning the scheduler may run them. It does not mean the process runs immediately. When the process resumes, sys_sleep checks the tick difference again. The loop matters because a wakeup only makes the process eligible to continue; the requested number of ticks still has to pass. After sys_sleep returns, user/sleep.c exits.

This trace also explains the limits of sleep 3. The number is timer ticks, not a promise of three wall-clock seconds. The duration depends on the timer and emulator. The program checks the number of arguments but not whether the text is a valid positive number. In user/ulib.c:atoi, conversion stops at the first nondigit, so text beginning with a nondigit such as -3 becomes zero. sys_sleep independently clamps a negative integer to zero if another caller passes one. These inputs therefore do not produce the intended wait.

## File descriptors connect programs to files

A file descriptor is a small integer in a process's open-file table. xv6 conventionally uses 0 for standard input, 1 for standard output and 2 for standard error. The descriptor names an open stream, not the file's path. open("README", O_RDONLY) asks the kernel to open a path and returns a descriptor. In a plain shell process with the three standard descriptors open, the returned number will commonly be 3, but programs should use the value returned by open rather than assume a number.

In user/cat.c:main, cat opens each named file and passes the returned descriptor to cat(fd). That function asks read for at most 512 bytes into its buf, then sends the bytes to descriptor 1 with write. It repeats while read returns a positive count. A read can return fewer bytes than requested; zero means end-of-file, and a negative result indicates an error. This is why the loop, rather than one read, is needed to print a whole file. close(fd) releases the descriptor when the file is finished.

kernel/sysfile.c:sys_read extracts the descriptor, buffer address and byte count from the system-call arguments. It uses the descriptor to find the open file and calls kernel/file.c:fileread. That function routes the request according to the file type: an inode-backed file, a device or a pipe. The buffer is in the process's virtual memory. The kernel transfers bytes to that user address through its checked copy paths; the user program cannot pass an arbitrary kernel pointer.

fprintf in cat.c is a user-space library routine that formats text. It is not itself a system call. The formatted message is ultimately written through an output descriptor. This distinction separates convenience code in the program from the kernel service that actually writes bytes.

## A pipe carries bytes between processes

For ls | grep c, the shell needs two processes and a communication channel. user/sh.c:runcmd handles the PIPE command by calling pipe(p) and forking two children. The pipe returns a read descriptor p[0] and a write descriptor p[1].

The left child closes descriptor 1, then calls dup(p[1]). Since dup chooses the lowest unused descriptor, the duplicate becomes descriptor 1. When ls writes its normal output, those bytes enter the pipe. The right child similarly closes descriptor 0 and duplicates p[0], so grep reads the listing through its normal standard input. Both children close the extra pipe descriptors after duplication. The shell closes its copies and waits for the children.

The kernel stores pipe bytes in a bounded buffer. If the buffer is empty while a writer is still open, piperead sleeps until data arrives. If all write ends are closed and the buffer is empty, a read returns end-of-file. An inherited descriptor that remains open can therefore keep a reader waiting even after the intended writer has exited. Closing unused ends is part of the pipeline's meaning, not just tidying up.

## Build and run from a disposable copy

A Linux build needs make, a host C compiler, Perl, a RISC-V cross compiler and qemu-system-riscv64. A capability check on 19 October recorded all five in Ubuntu 24.04 WSL: GNU Make 4.3, host GCC 13.3, Perl 5.38, RISC-V GCC 13.2 and QEMU 8.2.2. This confirms availability at that check, not a new build. Do not build directly in the preserved source tree: make qemu creates or updates build outputs and the xv6 filesystem image.

Build in a disposable copy. From this workspace in WSL:

    work=$(mktemp -d "$HOME/os-lab2.XXXXXX")
    cp -a /mnt/d/edu/faf/sem5/os/lab2/. "$work/"
    cd "$work"
    make qemu

At xv6's $ prompt, run:

    sleep 10
    sleep
    ls | grep c
    cat README

make qemu compiles the kernel and user programs, builds the filesystem image and starts QEMU. sleep 10 should wait for ten ticks, then return to the prompt. sleep without an argument should print usage: sleep <ticks> and exit with an error. To exit QEMU, press Ctrl-A, release it, then press X. The course VM may keep its source at ~/xv6-riscv; copy from that path into a disposable directory before running the same build.

## A short route for explaining the lab

Start with the user/kernel boundary, then trace one request: the shell forks a child, exec loads sleep, the generated stub issues ecall, and the dispatcher invokes sys_sleep. Explain why the kernel blocks the process instead of making it spin, and follow the timer tick to wakeup and the scheduler. Then use cat README to show that file descriptors name streams and read and write cross into kernel code. Finish with ls | grep c: two child processes use duplicated descriptors to exchange bytes through a bounded pipe. State the limit that timer ticks are not seconds, and a wakeup makes a process runnable rather than immediately running it.

## Practice prompts

1. In sleep 3, what are argc, argv[0] and argv[1]? Explain how the string 3 reaches sys_sleep.
2. Why does xv6 use both usertrap and syscall in the system-call path? What does sys_sleep do that a user-space busy loop would not?
3. For cat README, which descriptor names the opened file and which descriptor receives its output? Why does cat loop around read?
4. In ls | grep c, why does the left child close descriptor 1 before duplicating p[1]? What could happen if a process keeps an unused write end open?
5. What can you conclude from one sleep 10 duration? What cannot you conclude?

## Check your answers

1. argc is 2, argv[0] is sleep, and argv[1] is the text 3. The user program converts that text with atoi, calls the system-call stub, and the kernel dispatcher passes the integer to sys_sleep.
2. usertrap handles the transition into kernel mode; syscall selects the handler from the system-call number. sys_sleep waits on timer ticks and lets the scheduler run other processes, while a busy loop would keep consuming processor time.
3. open returns the descriptor used by read; descriptor 1 is standard output. read may return a short block and eventually returns 0 at end-of-file, so cat repeats until the file is exhausted.
4. Closing descriptor 1 makes it the lowest available descriptor, so dup(p[1]) assigns the pipe's write end to standard output. An open write end prevents an empty pipe from reporting end-of-file, so the reader may remain asleep.
5. It shows what happened in that one run on that timer and emulator. It does not establish that a tick always has an exact wall-clock duration or predict every run.

## Source and status

The walkthrough follows [the Lab 2 brief](lab-02-brief.docx) and the xv6 revision pinned in [the lab README](README.md). notes.md retains the earlier measured build, boot and command-check results; this revision does not claim a new QEMU run. The [course overview](../README.md#completion-record) records the owner's 15 October confirmation that all six labs were completed with 10/10 each; the portal gradebook was not independently checked.
