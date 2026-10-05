# Operating Systems Coursework

Coursework, laboratory implementations, and academic reports for the Operating Systems course (FCIM / FAF, Technical University of Moldova, Semester 5, 2026–2027).

## Coursework Organization

All laboratory assignments are structured in dedicated folders to maintain separation of concerns, build integrity, and clean deliverables.

```
os/
├── lab12/                 # Combined Labs 1 & 2: Linux OS Management and xv6 System Calls
│   ├── README.md          # Lab overview, execution and build guide
│   ├── labs-01-02.pdf     # Academic laboratory report (English, UTM format)
│   ├── labs-01-02.tex     # LaTeX report source
│   ├── labs-01-02-summary.png # High-resolution visual review summary
│   ├── lab-01-observations.md # Handout submission notes for Lab 1
│   ├── lab-02-notes.md    # Handout submission notes for Lab 2
│   └── xv6-riscv/         # xv6 RISC-V source checkout with sleep/args utilities
│
├── lab3/                  # Lab 3: The Command Line: Shell, Pipes and Text Filters
│   ├── README.md          # Lab overview, test instructions, and deliverables
│   ├── L3_SO.pdf          # Official Lab 3 handout
│   ├── oneliners.sh       # Verified pipeline solutions for Q1–Q8 + Bonus
│   ├── report.sh          # Shell script with completed user0–user6 failure breakdown
│   ├── access.log         # 500-line standard artificial web access dataset
│   ├── notes.md           # Predictions table, Observe questions, cron bonus
│   └── run-lab3.sh        # Verification test runner
│
├── lab4/                  # Lab 4: The xv6 Shell from the Outside
│   ├── README.md          # Lab overview, comparison matrix, and test instructions
│   ├── L4_SO.pdf          # Official Lab 4 handout
│   ├── Prepare Your Laptop for the Labs.pdf # Official environment setup guide
│   ├── sleep.c            # xv6 sleep utility with argument validation
│   ├── args.c             # xv6 user program printing argc and argv
│   ├── args_linux.c       # Linux C utility printing argc and argv
│   ├── Makefile           # xv6 Makefile with sleep and args registered in UPROGS
│   ├── Makefile.patch     # Unified patch registering _args in xv6 UPROGS
│   ├── notes.md           # Shell comparison table, argument analysis, sh.c answers
│   └── test-args.sh       # Compilation and test runner for Linux args
│
└── .agents/rules/         # Universal agent guidelines prohibiting folder flattening
```

## Laboratories Overview

### [Laboratories 1 and 2](file:///d:/edu/faf/sem5/os/lab12/README.md) (`lab12/`)
- **Focus**: Inspecting Linux system resources (process hierarchy, memory allocation, `/proc`, file descriptors) and boot tracing xv6 RISC-V in QEMU.
- **Deliverables**: Formatted UTM report ([`labs-01-02.pdf`](file:///d:/edu/faf/sem5/os/lab12/labs-01-02.pdf)), editable LaTeX source ([`labs-01-02.tex`](file:///d:/edu/faf/sem5/os/lab12/labs-01-02.tex)), and xv6 source tree ([`xv6-riscv`](file:///d:/edu/faf/sem5/os/lab12/xv6-riscv/)).

### [Laboratory 3](file:///d:/edu/faf/sem5/os/lab3/README.md) (`lab3/`)
- **Focus**: Bash command execution, expansions (globbing, variables, subshells, arithmetic), word splitting, I/O redirection, standard pipelines, text filters (`grep`, `cut`, `sort`, `uniq`, `wc`), and shell automation.
- **Deliverables**: Handout ([`L3_SO.pdf`](file:///d:/edu/faf/sem5/os/lab3/L3_SO.pdf)), one-liner answers ([`oneliners.sh`](file:///d:/edu/faf/sem5/os/lab3/oneliners.sh)), report script ([`report.sh`](file:///d:/edu/faf/sem5/os/lab3/report.sh)), 500-line dataset ([`access.log`](file:///d:/edu/faf/sem5/os/lab3/access.log)), and detailed notes ([`notes.md`](file:///d:/edu/faf/sem5/os/lab3/notes.md)).

### [Laboratory 4](file:///d:/edu/faf/sem5/os/lab4/README.md) (`lab4/`)
- **Focus**: Comparing the xv6 minimalist shell (`user/sh.c`) against GNU Bash on Linux. Inspecting command tokenization, argument passing (`argc`/`argv`), shell built-in mechanics (`cd`), and kernel boundary behavior.
- **Deliverables**: Handout ([`L4_SO.pdf`](file:///d:/edu/faf/sem5/os/lab4/L4_SO.pdf)), setup guide ([`Prepare Your Laptop for the Labs.pdf`](file:///d:/edu/faf/sem5/os/lab4/Prepare%20Your%20Laptop%20for%20the%20Labs.pdf)), implementations ([`sleep.c`](file:///d:/edu/faf/sem5/os/lab4/sleep.c), [`args.c`](file:///d:/edu/faf/sem5/os/lab4/args.c), [`args_linux.c`](file:///d:/edu/faf/sem5/os/lab4/args_linux.c)), build configuration ([`Makefile`](file:///d:/edu/faf/sem5/os/lab4/Makefile)), and analysis notes ([`notes.md`](file:///d:/edu/faf/sem5/os/lab4/notes.md)).

## Universal Hierarchy Mandate

A universal rule is enforced across all agent interactions in this repository and system-wide configurations:
- All coursework materials must maintain per-lab directory boundaries (`lab12/`, `lab3/`, `lab4/`, etc.).
- Never dump implementation files, notes, reports, or test scripts into subject root folders.
- All relative file paths across LaTeX classes, build files, and documentation must be preserved and updated when files are moved.
