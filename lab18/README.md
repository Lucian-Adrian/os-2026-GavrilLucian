# Lab 18 – Build a User-Level Thread Switch (xv6)

| File | Content |
|---|---|
| `notes.txt` | the Observe answer, the result, the experiments, as the brief asks |
| `report.pdf`, `report.tex` | UTM report with figures |
| `xv6-riscv/` | the complete xv6 tree (Lab 13 tree + Lab 18): `cd xv6-riscv && make qemu` |
| `xv6-commits/` | the three Lab 18 commits as `git format-patch` files |
| `lab18.patch` | the Lab 18 change on top of Lab 13 (3 files, +234 lines, no kernel change) |
| `experiments/` | `trace.diff`, `nosp.diff`, `nora.diff`: temporary changes used for Chapters 2–3 (not in the tree) |
| `evidence/` | the QEMU console output behind every figure |
| `brief.pdf`, `assets/` | the handout; figures, UTM class and logo |

The Lab 18 files: `user/uthread.c`, `user/uthread_switch.S`, and `Makefile` (`$U/_uthread` in UPROGS, plus the rule from the brief).

```bash
cd lab18/xv6-riscv && make qemu
$ uthread          # a, b, c started; then c, a, b take turns 0..99; "no runnable threads"
```

To rerun headless and capture the console: `python3 tools/xv6run.py lab18/xv6-riscv uthread`.
To rebuild the PDF, run `tectonic -X compile report.tex`.
