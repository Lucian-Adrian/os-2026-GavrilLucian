# Operating Systems Laboratory 6: Inside the xv6 File System

Coursework for Operating Systems (FCIM / FAF, UTM, 2026-2027).

**Track:** B (Build Your Own Small OS, xv6)  
**Environment:** xv6 RISC-V on QEMU 8.2.2 (emulated 3-hart virt machine)  
**Toolchain:** `riscv64-linux-gnu-gcc` 13.3.0, GNU `make` 4.3  
**Full Notes:** [notes.md](notes.md) | **Report:** [report.md](report.md) | [report.pdf](report.pdf)  

---

## Lab Deliverables in This Folder

- [user/mystat.c](user/mystat.c) (and [mystat.c](mystat.c)): Inode inspection utility decoding file type, inode number, link count, and byte size.
- [user/find.c](user/find.c) (and [find.c](find.c)): Recursive directory search utility matching basenames, complete with the `-n` inode inspection stretch feature.
- [Makefile](Makefile): xv6 build file registered with `$U/_mystat\` and `$U/_find\` under `UPROGS`.
- [notes.md](notes.md): Structured technical notes answering all questions from the lab brief.
- [report.md](report.md): Formal markdown lab report.
- [report.tex](report.tex): Formal LaTeX report using `utmreport.cls`.
- [report.pdf](report.pdf): Compiled PDF report generated via Tectonic.

---

## Build and Run

To run xv6 with `mystat` and `find`:

```bash
make clean
make qemu
```

Inside the xv6 shell:

```text
$ mystat README . console
$ ln README r2
$ mystat README r2
$ rm README
$ mystat r2
$ cat r2 | wc

$ mkdir a
$ mkdir a/b
$ echo x > a/b/r2
$ echo y > a/r2
$ ln cat r2
$ find . r2
$ find a b
$ find . r2 -n
$ mystat cat
```

To exit QEMU: press `Ctrl-A` then `X`.

---

## Build the Report PDF

To build `report.pdf` using Tectonic:

```powershell
tectonic report.tex
```
