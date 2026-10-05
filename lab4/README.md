# Laboratory 4: The xv6 Shell from the Outside

This directory contains all coursework files, source code implementations, patches, and documentation for Operating Systems Laboratory 4 (Track B: xv6 RISC-V).

## Overview

- **Focus**: Comparing the xv6 minimalist shell (`user/sh.c`) against GNU Bash on Linux. Investigating system call evolutions (`sleep` vs `pause`), command line parsing, wildcard expansion, quote stripping, environment variables, subshell execution, and shell built-in mechanics.
- **Handout**: [Official Lab 4 Specification](file:///d:/edu/faf/sem5/os/lab4/L4_SO.pdf) (`L4_SO.pdf`).
- **Prerequisites Guide**: [Prepare Your Laptop for the Labs](file:///d:/edu/faf/sem5/os/lab4/Prepare%20Your%20Laptop%20for%20the%20Labs.pdf) (`Prepare Your Laptop for the Labs.pdf`).

## Deliverables & Files

- [`sleep.c`](file:///d:/edu/faf/sem5/os/lab4/sleep.c): Working xv6 user program with argument validation and tick-based system call invocation.
- [`args.c`](file:///d:/edu/faf/sem5/os/lab4/args.c): xv6 user program printing argument count `argc` and individual `argv` entries.
- [`args_linux.c`](file:///d:/edu/faf/sem5/os/lab4/args_linux.c): Linux C utility demonstrating POSIX argument reception.
- [`Makefile`](file:///d:/edu/faf/sem5/os/lab4/Makefile): xv6 build Makefile with `$U/_sleep` and `$U/_args` registered in `UPROGS`.
- [`Makefile.patch`](file:///d:/edu/faf/sem5/os/lab4/Makefile.patch): Clean unified diff registering `$U/_args` in `UPROGS`.
- [`notes.md`](file:///d:/edu/faf/sem5/os/lab4/notes.md): Comprehensive report notes containing the Bash vs xv6 command comparison matrix, argument analysis, and xv6 `sh.c` source code answers.
- [`test-args.sh`](file:///d:/edu/faf/sem5/os/lab4/test-args.sh): Test script to compile and exercise `args_linux.c`.

## Verification Instructions

### xv6 Verification (QEMU)
Inside the xv6 source tree (`lab12/xv6-riscv/` or course repository):
```bash
make qemu
$ sleep 20
$ args one   two   three
$ args *.c "x y"
```

### Linux Verification
Inside a Linux / WSL terminal:
```bash
cd lab4
bash test-args.sh
```
