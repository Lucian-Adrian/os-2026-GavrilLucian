# Operating Systems Laboratory 6: Inside the xv6 File System

Coursework for Operating Systems (FCIM / FAF, UTM, 2026-2027).

**Track:** B, Build Your Own Small OS (xv6)
**Author:** Lucian-Adrian Gavril (FAF-241)
**Historical report environment:** xv6 RISC-V on QEMU 8.2.2

## Source and handout

The original local Lab 6 brief is not recovered. Use the current official [Lab 6 handout](https://else.fcim.utm.md/mod/resource/view.php?id=72234) for the assignment requirements; this README summarizes the recovered source and report.

## Lab goal and files

The 23 October [execution record](execution-2026-10-23.txt) captures one fresh disposable-image run of mystat, hard-link removal, and recursive find. It does not update the older 12 October transcript or cover every report exercise.

The recovered task explores xv6 inode metadata, directory entries, hard links, file removal, and file-system limits. It adds two user programs:

- [user/mystat.c](user/mystat.c) prints a path's type, inode number, link count, and size.
- [user/find.c](user/find.c) recursively searches directory entries by basename and can print inode numbers.
- [Makefile](Makefile) records the UPROGS registrations.
- [notes.md](notes.md) preserves the 12 October answers and links to the fresh run record.
- [report.md](report.md) retains historical transcripts and analysis plus fresh results; [report.tex](report.tex) is the LaTeX source; [report.pdf](report.pdf) is the current review/export with a conceptual diagram and a fresh-results appendix.
- [assets/](assets/) holds the report class, logo, terminal captures, and the conceptual filesystem diagram.
- [teaching-note.md](teaching-note.md) traces the programs through xv6 and separates historical output from fresh execution.

The complete xv6 source used for the overlay is in sibling [Lab 2](../lab2/README.md). Lab 6 alone does not contain a kernel tree, so its Makefile cannot build by itself.

## Build and run xv6

Use the WSL toolchain described in the [Lab 2 README](../lab2/README.md). Lab 6 needs GNU make, a host C compiler, Perl, a RISC-V GCC cross-compiler, and QEMU.

From the OS project root, run:

    overlay=$(bash ./lab6/prepare-overlay.sh "$PWD")
    cd "$overlay"
    make clean
    make qemu

The helper creates a fresh working copy of Lab 2 in /tmp, copies the two Lab 6 programs into its user directory, and adds their UPROGS entries. It keeps the existing sleep and args entries. The original Lab 2 source and Makefile are not changed.

At the xv6 prompt, try these commands in the disposable image:

    $ mystat README . console
    $ ln README r2
    $ mystat README r2
    $ rm README
    $ mystat r2
    $ rm r2
    $ mkdir a
    $ mkdir a/b
    $ echo x > a/b/r2
    $ echo y > a/r2
    $ ln cat r2
    $ find . r2
    $ find a b
    $ find . r2 -n
    $ mystat cat

The second rm removes the last README link before r2 is reused as a link to cat. To leave QEMU, press Ctrl-A, then X.

## Rebuild the report

From this folder in WSL, with Tectonic installed:

    out=$(mktemp -d /tmp/os-lab6-report.XXXXXX)
    tectonic report.tex --outdir "$out"

The output directory keeps generated build files out of the lab folder. The current report.pdf is built from report.tex and includes the fresh execution appendix.
