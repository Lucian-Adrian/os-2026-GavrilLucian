# Operating Systems Laboratory 5: The File System with Your Own Hands

Coursework for Operating Systems (FCIM / FAF, UTM, 2026-2027).

Start with [teaching-note.md](teaching-note.md) for a walkthrough of names, inodes, open descriptors, allocation, and permissions, with oral defense questions. The assignment handout is on Moodle ([Lab 5 handout](https://else.fcim.utm.md/mod/resource/view.php?id=72232)).

**Track:** A (Warm-up on Linux)
**Environment:** Ubuntu 24.04 LTS (WSL2) / Debian GNU/Linux 13
**Reports:** [report.pdf](report.pdf) | [LaTeX source](report.tex) | [Markdown report](report.md) | [execution log](execution-2026-10-23.txt)

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

- [report.md](report.md): Markdown report with command transcripts, measurements, tables, and answers.
- [report.tex](report.tex): LaTeX laboratory report using `utmreport.cls`.
- [report.pdf](report.pdf): PDF report built from `report.tex`, with terminal screenshots.

The terminal screenshots, filesystem diagram, report class, and logo are in [assets](assets/).

---

## Build the Report PDF

To build `report.pdf` using Tectonic:

```bash
tectonic report.tex
```

## Additional execution log

[execution-2026-10-23.txt](execution-2026-10-23.txt) records a standalone WSL2 (Ubuntu 24.04.4, ext4) run checking hard links, symlinks, reading from an unlinked open file descriptor, and sparse file allocation.
