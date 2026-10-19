# Operating Systems Laboratory 5: The File System with Your Own Hands

Coursework for Operating Systems (FCIM / FAF, UTM, 2026-2027).

Start with [teaching-note.md](teaching-note.md): names, inodes, open descriptors, allocation and permissions, with source-linked experiments and oral questions. The original local Lab 5 brief is not recovered; use the current official [Lab 5 handout](https://else.fcim.utm.md/mod/resource/view.php?id=72232) for the assignment requirements.

The [course overview](../README.md) records the owner's 15 October confirmation that all six OS labs were completed and received 10/10. The environment and numbers below describe the saved report's historical run, not a new check. The terminal-style JPEGs are reconstructed illustrations, not original captures.

**Track:** A (Warm-up on Linux)
**Environment:** Ubuntu 24.04 LTS VM on WSL2, Linux kernel 6.6.87.2-microsoft-standard-WSL2, x86_64
**Historical report user:** `ubuntu` (non-root, UID 1000)
**Current PDF review/export:** [report.pdf](report.pdf) | [LaTeX source](report.tex) | [Markdown report](report.md) | [fresh execution record](execution-2026-10-23.txt)

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

- [report.md](report.md): Markdown report with historical command transcripts, reported measurements, data tables, and answers; its terminal-style images are reconstructed illustrations, not original captures.
- [report.tex](report.tex): Formal LaTeX laboratory report using `utmreport.cls`.
- [report.pdf](report.pdf): Current PDF review/export generated from report.tex, with the conceptual filesystem diagram, reconstructed historical panels, and a fresh-results appendix.

The report's images, class and logo are together in [assets](assets/). The lesson, reports and this overview stay directly in the lab folder.

---

## Build the Report PDF

To build `report.pdf` using Tectonic:

```powershell
tectonic report.tex
```

## Fresh focused run

The 23 October transcript is a genuine WSL execution record for hard-link identity, symbolic-link metadata, an open descriptor after unlink, and sparse allocation. It records Ubuntu 24.04.4 on WSL2 and an ext4 temporary directory. The rest of the report remains historical material.
