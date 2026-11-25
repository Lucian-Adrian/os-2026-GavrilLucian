# Operating Systems Laboratory 4

The handout is [L4_SO.pdf](L4_SO.pdf), with setup instructions in [Prepare Your Laptop for the Labs.pdf](Prepare%20Your%20Laptop%20for%20the%20Labs.pdf). Deliverables: [Lab4_Lucian-Adrian_Gavril_FAF-241.docx](Lab4_Lucian-Adrian_Gavril_FAF-241.docx) and [report.pdf](report.pdf) (built from [report.tex](report.tex)).

For a source-based walkthrough of the `sleep` system call, `argv`, process descriptors, and the xv6 shell parser, see [teaching-note.md](teaching-note.md). The walkthrough uses the source tree in [../lab2](../lab2/) and keeps build output in a temporary copy.

## Environment

Tested on Debian GNU/Linux 13 with GNU Bash 5.2.37, the `riscv64-linux-gnu` toolchain, and QEMU 10 (`qemu-system-riscv64`). In QEMU, `sleep 20` returned after ~1.96–1.97 s, `sleep` without arguments printed the usage line, and `args` confirmed how Bash expands globs and removes quotes while xv6 passes raw tokens. Interactive tests and `user/sh.c` inspection confirmed that xv6 has no Up-arrow history, Tab completion, or Ctrl+R search.

## Build report PDF

With Tectonic installed, run `tectonic report.tex` from this folder. This writes `report.pdf` here. The report source uses the flat assets/ folder for its class, UTM logo, and figures.

## Run

Use a Linux environment with `make`, a RISC-V compiler and QEMU, following the setup guide. From this folder, create a temporary working copy of the pinned [Lab 2 tree](../lab2/) and copy this lab's sources and Makefile into it:

```bash
workdir=$(mktemp -d)
cp -a ../lab2/. "$workdir/"
cp sleep.c args.c "$workdir/user/"
cp Makefile "$workdir/Makefile"
make -C "$workdir" qemu
```

This `Makefile` is the pinned Lab 2 Makefile plus `_sleep` and `_args`. It also lists `_pingpong`, which comes from the Lab 2 tree (`../lab2/user/pingpong.c`), so use it only inside that copy and not in another xv6 tree. The pinned tree declares `sleep(int)` in `user/user.h`, matching this lab's `sleep.c`. At the xv6 prompt:

    $ sleep 20
    $ args one two three
    $ args *.c "x y"

For Linux, compile args_linux.c with gcc -o args args_linux.c and run it from a folder containing .c files. Bash expands *.c and removes quote marks before the program starts; the xv6 shell passes wildcard and quote characters to the program.

## Oral questions

- Which component expands *.c and removes quotes? The shell prepares argv before exec.
- Why is cd handled by the shell process? A child changing directory would not change its parent's working directory.
- What does a pipe connect? It sends one process's standard output to another process's standard input.
