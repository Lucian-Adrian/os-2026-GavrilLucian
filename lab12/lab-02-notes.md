# Operating Systems Lab 2 report

## Goal and source

The lab builds xv6, boots it under QEMU, explores its shell and source, then adds a user program named `sleep`.

- Source: [MIT xv6-riscv](https://github.com/mit-pdos/xv6-riscv)
- Assignment-compatible commit: `9374395cd3dc31c0e6993b3d257e2379a8dec89f`
- The upstream tip checked on 2026-09-28 had renamed the user `sleep(ticks)` call to `pause(ticks)`. This lab uses the official revision from before that rename because the handout requires `sleep(ticks)`.

## Work completed

Added `user/sleep.c` and registered `$U/_sleep` in the xv6 `Makefile`. The program checks for exactly one argument. With a missing or extra argument it prints `usage: sleep <ticks>` and exits with status 1. Otherwise it converts the argument with `atoi`, calls the existing kernel `sleep()` system call, and exits with status 0.

## Results

The kernel and file system image built in **2.158 seconds**. QEMU booted xv6 and reached the shell prompt in **2.459 seconds**.

All seven scripted shell checks passed:

- `ls`
- `cat README`
- `echo hello xv6`
- `ls | grep c`
- `wc README`
- `sleep 10`, which returned to the prompt in **0.958 seconds**
- `sleep`, which printed `usage: sleep <ticks>`

QEMU exited with return code 0 after the checks. The optional `usertests -q` suite was not run.

## Part 2: xv6 shell

1. Three programs included in the xv6 image are `ls`, `cat`, and `echo` (`Makefile`, `UPROGS`).
2. A pipe needs separate processes for the producer and consumer, plus interprocess communication. The xv6 shell creates child processes and connects their output and input through a kernel pipe (`user/sh.c`).
3. The xv6 shell runs basic programs and pipelines in a small environment; the Linux shell from Lab 1 runs in a full Linux environment with a broader set of tools and facilities.

## Part 3: reading the source

1. `user/cat.c` uses `read` to request bytes from a file descriptor, `write` to send them to standard output, `open` to open named files, `close` to release file descriptors, and `exit` to end the process with a status. `fprintf` formats error text in user space; it is a library function, not a system call.
2. `sys_read` is implemented at `kernel/sysfile.c:69` in the pinned source commit.
3. Code in `kernel/` runs with kernel privileges and implements OS services. Code in `user/` contains ordinary programs that request those services through system calls.

## Explain it to me

xv6 is a small operating system running on a simulated RISC-V machine. QEMU supplies the simulated hardware. The `user/` programs ask the `kernel/` to do protected work through system calls such as `read`, `write`, and `sleep`.

For `ls | grep c`, the shell starts one process for `ls` and another for `grep`, then connects them with a pipe. `ls` writes its listing into the pipe, and `grep` reads that listing and keeps lines containing `c`.

The new `sleep` program passes the requested tick count to the existing kernel service. The kernel blocks that process on a wait channel and wakes it on timer interrupts until the requested ticks have elapsed. In this run, `sleep 10` took 0.958 seconds; this is a single observed duration, not an exact conversion from ticks to seconds.

The supplied program validates the number of arguments, but xv6's `atoi` does not report numeric conversion errors. Non-numeric or negative strings can become zero. The kernel separately clamps negative integer arguments to zero, and a killed process can make its system call return -1. The minimal user program does not propagate that return value and still calls `exit(0)`.

## Evidence

- `D:/ops/uni/os/lab2/lab2-run.log`: package, build, boot, command checks, and summary.
- `D:/ops/uni/os/lab2/lab2-serial.raw`: raw QEMU serial output, including the boot messages and xv6 command output.
- `D:/ops/uni/os/lab2/lab2-timing.jsonl`: shell-ready time and duration for each command.

![Lab 2 xv6 output rendered from the saved QEMU log](D:/ops/uni/os/lab2/proof-xv6-output.png)

The image renders selected lines from the actual QEMU run. `lab2-run.log` and `lab2-serial.raw` are the complete primary records.
