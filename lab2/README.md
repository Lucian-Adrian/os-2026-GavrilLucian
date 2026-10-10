# Lab 2: Meet the OS You Will Build

The handout is [lab-02-brief.docx](lab-02-brief.docx). The required answers are in [notes.md](notes.md). The source tree is pinned to MIT xv6-riscv commit 9374395cd3dc31c0e6993b3d257e2379a8dec89f. The file user/sleep.c is registered as $U/_sleep in the Makefile.

The measured local check built and booted the tree, ran seven shell checks, and verified sleep 10 and the usage error. The notes also answer the source-reading questions. These local records do not establish a course-system or assistant-side receipt.

## Build and run

From this folder, run make qemu. At the xv6 prompt, try:

    $ sleep 10
    $ sleep

The first command passes the tick count from user/sleep.c through the user system-call stub to the kernel sleep implementation. The kernel blocks the process until timer ticks wake it.

For ls | grep c, user/sh.c starts the producer and consumer processes and connects them through a kernel pipe. This shows why a pipeline needs both processes and interprocess communication.

## Oral questions

- Why does sleep.c call a system call instead of waiting in a user-space loop? The kernel can block and schedule the process while timer ticks advance.
- What is the difference between user/ and kernel/ code? User programs request protected services through system calls.
- Why must a pipeline run its two commands in separate processes? Each side needs its own program and file descriptors while sharing data through a pipe.

[pingpong.c](pingpong.c) is the optional two-pipe exercise. It is not registered in the pinned tree; use a working copy if you want to build it.
