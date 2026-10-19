# Lab 2: Meet the OS You Will Build

Start with the [teaching note](teaching-note.md) for a source walkthrough of processes, system calls, file descriptors, pipes and the lab's `sleep` program. The handout is [lab-02-brief.docx](lab-02-brief.docx). The required answers are in [notes.md](notes.md). The source tree is pinned to MIT xv6-riscv commit 9374395cd3dc31c0e6993b3d257e2379a8dec89f. The file `user/sleep.c` is registered as `$U/_sleep` in the Makefile.

An Ubuntu 24.04 WSL capability check on 19 October recorded host GCC 13.3, GNU Make 4.3, Perl 5.38, RISC-V GCC 13.2 and QEMU 8.2.2. This confirms the build prerequisites were present during that check; it does not record a new build. The build, boot, timing and seven shell-check results in [notes.md](notes.md) are from an earlier run and remain historical. The notes also answer the source-reading questions.

## Build and run

Build from a disposable copy so generated files and the xv6 image do not alter the preserved source tree. In WSL, run:

    work=$(mktemp -d "$HOME/os-lab2.XXXXXX")
    cp -a ./lab2/. "$work/"
    cd "$work"
    make qemu

At the xv6 prompt, try:

    $ sleep 10
    $ sleep

The first command passes the tick count from user/sleep.c through the user system-call stub to the kernel sleep implementation. The kernel blocks the process until timer ticks wake it.

For ls | grep c, user/sh.c starts the producer and consumer processes and connects them through a kernel pipe. This shows why a pipeline needs both processes and interprocess communication.

## Oral questions

- Why does sleep.c call a system call instead of waiting in a user-space loop? The kernel can block and schedule the process while timer ticks advance.
- What is the difference between user/ and kernel/ code? User programs request protected services through system calls.
- Why must a pipeline run its two commands in separate processes? Each side needs its own program and file descriptors while sharing data through a pipe.

[pingpong.c](pingpong.c) is the optional two-pipe exercise. It is not registered in the pinned tree; use a working copy if you want to build it.

For the preceding Linux resource-management lab, see [Lab 1](../lab1/README.md) and its [teaching note](../lab1/teaching-note.md).
