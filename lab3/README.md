# Laboratory 3: The Command Line: Shell, Pipes and Text Filters

This directory contains all coursework files, solutions, and documentation for Operating Systems Laboratory 3 (Track A: Linux).

## Overview

- **Focus**: Bash command expansion, process environment, shell built-ins vs external utilities, I/O redirection, standard pipelines, text filters (`grep`, `cut`, `sort`, `uniq`, `wc`), and automation scripts.
- **Handout**: [Official Lab 3 Specification](file:///d:/edu/faf/sem5/os/lab3/L3_SO.pdf) (`L3_SO.pdf`).

## Deliverables & Files

- [`oneliners.sh`](file:///d:/edu/faf/sem5/os/lab3/oneliners.sh): Single-pipeline solutions answering questions Q1 through Q8, plus the regex bonus.
- [`report.sh`](file:///d:/edu/faf/sem5/os/lab3/report.sh): Shell script parsing `access.log` with complete user failure breakdowns (`user0` to `user6`) and input validation.
- [`access.log`](file:///d:/edu/faf/sem5/os/lab3/access.log): Generated 500-line standard artificial web access dataset.
- [`notes.md`](file:///d:/edu/faf/sem5/os/lab3/notes.md): Complete lab observations, command expansion prediction table, answers to all Observe questions (Parts 1–5), and cron bonus documentation.
- [`run-lab3.sh`](file:///d:/edu/faf/sem5/os/lab3/run-lab3.sh): Automated test harness verifying the dataset, one-liners, and report generator.

## Running the Verification

Run the verification harness inside a Linux terminal or WSL environment:

```bash
cd lab3
bash run-lab3.sh
```
