# Operating Systems Laboratory 4

The handout is [L4_SO.pdf](L4_SO.pdf), with the setup guide in [Prepare Your Laptop for the Labs.pdf](Prepare%20Your%20Laptop%20for%20the%20Labs.pdf). The required repository files are [Lab4_Lucian-Adrian_Gavril_FAF-241.docx](Lab4_Lucian-Adrian_Gavril_FAF-241.docx), [sleep.c](sleep.c), [args.c](args.c), [args_linux.c](args_linux.c), and [Makefile](Makefile). The Word report source and PDF review copy are [report.tex](report.tex) and [report.pdf](report.pdf).

## Status

A focused QEMU run built and booted the temporary tree on Debian GNU/Linux 13 on 9 October 2026. It checked sleep with and without an argument; sleep 20 returned after 1.96 seconds. A 10 October run checked all four args patterns in xv6 and Bash. All twelve required figures for Parts 1 through 4 use genuine terminal captures. The xv6 comparison capture covers rows 1 through 9. A focused interaction found no Up-arrow recall or Ctrl+R search, and Tab at an empty prompt produced no completion list; path-prefix completion was not tested. Source inspection shows no history, completion, or reverse-search handler in the xv6 console. Dev1 is a remote Debian host, and these records do not establish that the course-assigned laptop or VM was used. No teacher receipt is available in this workspace.

## Build report PDF

With Tectonic installed, run `tectonic report.tex` from this folder. This writes `report.pdf` here. The report class and UTM logo are included beside the source, so the build does not depend on a separate `report-template` folder.

## Run

Use a Linux environment with `make`, a RISC-V compiler and QEMU, following the setup guide. From this folder, create a temporary working copy of the pinned [Lab 2 tree](../lab2/) and copy this lab's sources and Makefile into it:

```bash
workdir=$(mktemp -d)
cp -a ../lab2/. "$workdir/"
cp sleep.c args.c "$workdir/user/"
cp Makefile "$workdir/Makefile"
make -C "$workdir" qemu
```

The pinned tree declares `sleep(int)` in `user/user.h`, matching this lab's `sleep.c`. At the xv6 prompt:

    $ sleep 20
    $ args one two three
    $ args *.c "x y"

For Linux, compile args_linux.c with gcc -o args args_linux.c and run it from a folder containing .c files. Bash expands *.c and removes quote marks before the program starts; the xv6 shell passes wildcard and quote characters to the program.

## Oral questions

- Which component expands *.c and removes quotes? The shell prepares argv before exec.
- Why is cd handled by the shell process? A child changing directory would not change its parent's working directory.
- What does a pipe connect? It sends one process's standard output to another process's standard input.
