# Operating Systems Laboratory 5: The File System with Your Own Hands

Coursework for Operating Systems (FCIM / FAF, UTM, 2026-2027).

**Track:** A (Warm-up on Linux)  
**Environment:** Ubuntu 24.04 LTS VM on WSL2, Linux kernel 6.6.87.2-microsoft-standard-WSL2, x86_64  
**User:** `ubuntu` (non-root, UID 1000)  
**Full Report:** [report.md](report.md) | [report.pdf](report.pdf)  

---

## Lab Overview

This laboratory examines the Linux filesystem from the shell up:
1. **The Tree and File Types**: System root inspection, device nodes (`/dev`), UsrMerge symlink architecture, directory sizes.
2. **Inodes and Links**: Inode metadata vs directory entries, hard links, dangling symlinks, directory link counts, sparse files (`truncate` vs physical block allocation).
3. **Permissions & Access Control**: Octal permissions (`600`, `644`, `755`, `700`), `umask` arithmetic, directory read (`r`) vs search/traversal (`x`), setuid (`/usr/bin/passwd`), and the sticky bit (`/tmp`).
4. **Disks and Kernel Filesystem**: Block device hierarchy (`lsblk`, `df`), root mount options, hardware introspection via `/proc/cpuinfo` and `/proc/meminfo`, and `/proc/self` process resolution.
5. **Stretch Experiments**: Magic number byte analysis via `xxd`, setuid binary discovery, unlinking active file descriptors in `/proc/$$/fd`, and loopback ext4 inode allocation.

---

## Deliverables in This Folder

- [report.md](report.md): Markdown report containing all verified terminal transcripts, data tables, and answers to Observe questions.
- [report.tex](report.tex): Formal LaTeX laboratory report using `utmreport.cls`.
- [report.pdf](report.pdf): Compiled PDF report generated via Tectonic.

---

## Build the Report PDF

To build `report.pdf` using Tectonic:

```powershell
tectonic report.tex
```
