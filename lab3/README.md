# Operating Systems Laboratory 3

The handout is [L3_SO.pdf](L3_SO.pdf). Required Word-deliverable filename: [Lab3_Lucian-Adrian_Gavril_FAF-241.docx](Lab3_Lucian-Adrian_Gavril_FAF-241.docx), retained unchanged. Current PDF review/export: [report.pdf](report.pdf), generated from the [LaTeX source](report.tex) and including the conceptual shell-argument illustration. The required repository scripts are [report.sh](report.sh) and [oneliners.sh](oneliners.sh).

For a first-principles walkthrough of Bash parsing, descriptors, pipes, and the report script, see [teaching-note.md](teaching-note.md).

## Status

The data and script checks passed on Debian GNU/Linux 13 on 9 October 2026. The measured Q6 output is 10:10 user0, 10:15 user5, and 10:20 user3.

The report includes genuine terminal captures for all 24 required figures and the exact temporary cron entry with its four-run output. The captures were recorded on the remote Dev1 Debian GNU/Linux 13 host on 10 October 2026; they do not establish that the assigned course laptop or VM was used.

## Build report PDF

With Tectonic installed, run `tectonic report.tex` from this folder. This writes `report.pdf` here. The report source uses the flat assets/ folder for its class, UTM logo, and figures.

## Run

From a Linux or WSL shell:

    cd lab3
    bash run-lab3.sh

A failed row contains a timestamp, username, status, and page. grep FAIL access.log | cut -d' ' -f3 | sort | uniq -c keeps usernames from failed requests, sorts them, and counts each one.

## Oral questions

- Why must values be sorted before uniq -c? uniq combines adjacent equal lines.
- Why does ls -l /etc | wc -l usually add one line? Long output includes its total summary.
- Why do the last failed rows depend on the data file? tail reads the current file order, so rerun the pipeline after changing the dataset.
