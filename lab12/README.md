# Laboratories 1 and 2: Linux Resource Management and xv6 System Calls

This directory contains all code, observations, and academic reports for Operating Systems Laboratories 1 and 2.

## Overview

- **Laboratory 1**: Linux as a Resource Manager. Examines process hierarchy, memory management (distinguishing free vs available RAM), file descriptors, device nodes, and system logs on an Ubuntu 24.04 environment.
- **Laboratory 2**: xv6 System Calls and Shell Architecture. Builds and boots the xv6 operating system on emulated RISC-V hardware, inspects kernel/user boundary mechanisms, and implements the user-space `sleep` utility invoking the kernel scheduler tick mechanism.

## Deliverables & Files

- [Compiled report](file:///d:/edu/faf/sem5/os/lab12/labs-01-02.pdf) (`labs-01-02.pdf`): Academic report following UTM FCIM guidelines in English.
- [LaTeX source](file:///d:/edu/faf/sem5/os/lab12/labs-01-02.tex) (`labs-01-02.tex`): Formatted with `utmreport.cls`.
- [Visual summary](file:///d:/edu/faf/sem5/os/lab12/labs-01-02-summary.png) (`labs-01-02-summary.png`): High-resolution visual review summary.
- [Lab 1 observations](file:///d:/edu/faf/sem5/os/lab12/lab-01-observations.md) (`lab-01-observations.md`): Terminal execution logs and analysis for Linux system inspection.
- [Lab 2 notes](file:///d:/edu/faf/sem5/os/lab12/lab-02-notes.md) (`lab-02-notes.md`): xv6 build, boot, system call analysis, and timing measurements.
- [xv6-riscv source](file:///d:/edu/faf/sem5/os/lab12/xv6-riscv) (`xv6-riscv/`): Pinned source tree (commit `9374395cd3dc`) containing [`sleep.c`](file:///d:/edu/faf/sem5/os/lab12/xv6-riscv/user/sleep.c) registered in the Makefile.

## Compilation

Recompile the LaTeX report with Tectonic:

```powershell
& "$env:LOCALAPPDATA\Programs\Tectonic\tectonic.exe" labs-01-02.tex
```
