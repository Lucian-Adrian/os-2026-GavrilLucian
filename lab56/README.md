# Supplementary combined report for Labs 5 and 6

Operating Systems (FCIM / FAF, UTM, 2026-2027).

Recovered from the owner's repository at commit `183ff1340c42620ccb86b2f0d3493e0d667d5a78`. Use the separate [Lab 5](../lab5/teaching-note.md) and [Lab 6](../lab6/teaching-note.md) lessons for study. The original handouts are unavailable; the saved reports and source supply the task descriptions.

**Track A:** The File System with Your Own Hands (Linux)  
**Track B:** Inside the xv6 File System (xv6 RISC-V)  
**Author:** Lucian-Adrian Gavril (FAF-241)  
**Combined Document:** [labs-05-06.pdf](labs-05-06.pdf) | [labs-05-06.tex](labs-05-06.tex)  

---

## Overview

This folder contains the formal combined academic report covering both Lab 5 and Lab 6, structured with distinct parts for each laboratory:
- **Part I: Laboratory 5 (Track A)**: Exploration of Linux VFS, inode/name decoupling, link lifecycles, permissions, sparse file allocations, `/proc` pseudo-files, and four stretch problems (magic numbers, setuid hunt, unlinking open file descriptors, and loopback ext4 inode allocation).
- **Part II: Laboratory 6 (Track B)**: Investigation of xv6 filesystem internals, implementation of `user/mystat.c` and `user/find.c` with the `-n` inode stretch flag, derivation of theoretical capacity limits, and deallocation code tracing in `kernel/sysfile.c` and `kernel/fs.c`.

---

## Individual Lab Folders

Individual standalone lab folders, complete with their source code, working makefiles, and separate reports, remain available at:
- [Lab 5](../lab5/README.md)
- [Lab 6](../lab6/README.md)

---

## Build the Combined Report PDF

The class, logo and images are together in [assets](assets/). Build from this folder so the relative paths resolve.

To recompile `labs-05-06.pdf` using Tectonic:

```powershell
tectonic labs-05-06.tex
```

## Illustration provenance

The older terminal panels in this supplementary report were reconstructed from text by a drawing script. They explain the saved observations and are not original terminal screenshots. Use the separate reports for the current source and evidence distinctions.
