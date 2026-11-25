# Operating Systems laboratories

Gavril Lucian-Adrian, FAF-241. Technical University of Moldova, FCIM, 2026–2027.

Course repository: [Lucian-Adrian/os-2026-GavrilLucian](https://github.com/Lucian-Adrian/os-2026-GavrilLucian). Each laboratory keeps its assignment material, source, answers, report and supporting images together. Open a lab's README for its prerequisites and exact execution commands.

| Lab | Topic | Required answers | Report and execution |
| --- | --- | --- | --- |
| 1 | Linux resources and processes | [report.md](lab1/report.md) | [Files and commands](lab1/README.md) |
| 2 | xv6, system calls and sleep | [notes.md](lab2/notes.md) | [Source and build](lab2/README.md) |
| 3 | Bash, quoting and text streams | [notes.md](lab3/notes.md) | [PDF](lab3/report.pdf) · [Source and commands](lab3/README.md) |
| 4 | xv6 shell and arguments | [notes.md](lab4/notes.md) | [PDF](lab4/report.pdf) · [Source and build](lab4/README.md) |
| 5 | Linux filesystem and links | [report.md](lab5/report.md) | [PDF](lab5/report.pdf) · [Files and commands](lab5/README.md) |
| 6 | xv6 filesystem and traversal | [notes.md](lab6/notes.md) · [report.md](lab6/report.md) | [PDF](lab6/report.pdf) · [Source and build](lab6/README.md) |
| 7 | Linux fork, exec, zombies and pipes | [report.md](lab7/report.md) | [PDF](lab7/report.pdf) · [Source and commands](lab7/README.md) |
| 8 | xv6 processes and pingpong | [notes.md](lab8/notes.md) | [PDF](lab8/report.pdf) · [Source and build](lab8/README.md) |
| 9 | Watching system calls with strace | [report.md](lab9/report.md) | [PDF](lab9/report.pdf) · [Source and commands](lab9/README.md) |
| 10 | xv6 system call `trace` (and `sysinfo`) | [notes.txt](lab10/notes.txt) | [PDF](lab10/report.pdf) · [Patch and build](lab10/README.md) |
| 11 | Race, mutex and semaphore (Linux) | [report.md](lab11/report.md) | [PDF](lab11/report.pdf) · [Source and commands](lab11/README.md) |
| 12 | Producer–consumer, condition variable, readers–writers, deadlock | [report.md](lab12/report.md) | [PDF](lab12/report.pdf) · [Source and commands](lab12/README.md) |
| 13 | Semaphores in the xv6 kernel (`sem_init`, `sem_down`, `sem_up`) | [notes.txt](lab13/notes.txt) | [PDF](lab13/report.pdf) · [Patch and build](lab13/README.md) |
| 17 | Threads share memory, and race (Linux) | [report.md](lab17/report.md) | [PDF](lab17/report.pdf) · [Source and commands](lab17/README.md) |
| 18 | User-level thread switch (xv6 `uthread`) | [notes.txt](lab18/notes.txt) | [PDF](lab18/report.pdf) · [Tree and build](lab18/README.md) |

The [combined Labs 1–2 report](lab1-2/README.md) and [combined Labs 5–6 report](lab5-6/README.md) are supplementary. Individual folders retain the required submission files. Original handouts are included where recovered; the original Labs 5, 6 and 8 handouts are linked from their lab READMEs rather than presented as locally recovered files.

## Build and inspect

Clone the repository, then follow the selected lab's instructions:

```sh
git clone https://github.com/Lucian-Adrian/os-2026-GavrilLucian.git
cd os-2026-GavrilLucian
```

Linux labs use Bash, GCC and the normal GNU command-line tools. xv6 labs require GNU make, Perl, a RISC-V toolchain and QEMU. The complete base xv6 source is in `lab2/`; later xv6 labs include their changed source. Lab 8 provides a disposable overlay helper so its experiments do not alter the base tree.

The formal PDFs include their editable TeX sources, UTM class, logo and figure assets. To rebuild one with Tectonic, run `tectonic -X compile report.tex` inside its lab directory. Combined reports use their own `.tex` filenames. The report layout uses the [UTM report template](https://github.com/Lucian-Adrian/utm-report-templates) included locally in each applicable lab's `assets/` folder.

## Evidence and explanations

Every terminal figure in the reports is the real output of the commands shown in it, captured on the lab machine (Debian 13, GCC 14, QEMU 10.0). Labs 9, 11, 12 and 13 keep the raw output behind their figures in `evidence/`. Lab 10 keeps its kernel change as `lab10/lab10.patch`, and Lab 13 keeps the cumulative xv6 change as `lab13/lab10-13.patch`.

For study, start with a lab's `teaching-note.md`. The [Labs 7–8 presentation and speaking route](lab7-8/README.md) connect the reports to a demonstration. The [course study guide](lab7-8/course-study.md) also explains commands from the earlier labs, with oral questions and changed conditions.

Course handouts and lectures are published in the [ELSE Operating Systems course](https://else.fcim.utm.md/course/view.php?id=5439), which requires university access.
