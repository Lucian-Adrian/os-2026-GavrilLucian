# Operating Systems Laboratory 3

The handout is [L3_SO.pdf](L3_SO.pdf). Deliverables: [Lab3_Lucian-Adrian_Gavril_FAF-241.docx](Lab3_Lucian-Adrian_Gavril_FAF-241.docx), [report.pdf](report.pdf) (built from [report.tex](report.tex)), [report.sh](report.sh), and [oneliners.sh](oneliners.sh).

For a first-principles walkthrough of Bash parsing, descriptors, pipes, and the report script, see [teaching-note.md](teaching-note.md).

## Environment

Tested on Debian GNU/Linux 13 with GNU Bash 5.2.37. The report includes terminal screenshots for all 24 figures, plus the temporary cron entry and its four-run output. For Q6, the last three failed requests in `access.log` are `10:10 user0`, `10:15 user5`, and `10:20 user3`.

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
