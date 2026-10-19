# Operating Systems laboratories

Gavril Lucian-Adrian, FAF-241. Technical University of Moldova, FCIM, 2026–2027.

Course repository: [Lucian-Adrian/sem5-operating-systems](https://github.com/Lucian-Adrian/sem5-operating-systems). Each laboratory keeps its assignment material, source, answers, report and supporting images together. Open a lab's README for its prerequisites and exact execution commands.

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

The [combined Labs 1–2 report](lab12/README.md) and [combined Labs 5–6 report](lab56/README.md) are supplementary. Individual folders retain the required submission files. Original handouts are included where recovered; the original Labs 5, 6 and 8 handouts are linked from their lab READMEs rather than presented as locally recovered files.

## Build and inspect

Clone the repository, then follow the selected lab's instructions:

```sh
git clone https://github.com/Lucian-Adrian/sem5-operating-systems.git
cd sem5-operating-systems
```

Linux labs use Bash, GCC and the normal GNU command-line tools. xv6 labs require GNU make, Perl, a RISC-V toolchain and QEMU. The complete base xv6 source is in `lab2/`; later xv6 labs include their changed source. Lab 8 provides a disposable overlay helper so its experiments do not alter the base tree.

The formal PDFs include their editable TeX sources, UTM class, logo and figure assets. To rebuild one with Tectonic, run `tectonic -X compile report.tex` inside its lab directory. Combined reports use their own `.tex` filenames. The report layout uses the [UTM report template](https://github.com/Lucian-Adrian/utm-report-templates) included locally in each applicable lab's `assets/` folder.

## Evidence and explanations

Reports distinguish recorded output from illustrative examples. Labs 7 and 8 include fourteen original terminal screenshots captured on 19 October 2026, embedded beside their answers. Process IDs, directory counts and tool versions describe that recorded environment. The older Labs 5–6 terminal panels are reconstructed illustrations, not original screenshots. Their captions identify this limitation. Fresh bounded runs on 23 October provide genuine [Linux filesystem output](lab5/execution-2026-10-23.txt) and [xv6 filesystem output](lab6/execution-2026-10-23.txt); their report appendices explain exactly what was tested. Concept illustrations explain mechanisms and are labelled separately from execution evidence.

For study, start with a lab's `teaching-note.md`. The [Labs 7–8 presentation and speaking route](lab78/README.md) connect the reports to a demonstration. The [course study guide](lab78/course-study.md) also explains commands from the earlier labs, with oral questions and changed conditions.

Course handouts and lectures are published in the [ELSE Operating Systems course](https://else.fcim.utm.md/course/view.php?id=5439), which requires university access.
