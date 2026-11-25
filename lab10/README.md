# Lab 10 – Add Your Own System Call: trace (xv6)

| File | Content |
|---|---|
| `report.pdf`, `report.tex` | UTM report with figures and the Observe answers |
| `notes.txt` | Part 3 answers, as the brief asks |
| `lab10.patch` | every Lab 10 change (`trace` and the optional `sysinfo`) against upstream xv6 commit `fa2ddcb` (13 files, +140 lines) |
| `xv6-commits/` | the three xv6 commits as `git format-patch` files (`git am` applies them) |
| `kernel/`, `user/`, `Makefile` | the modified xv6 files: `trace` (SYS 23) and the optional `sysinfo` (SYS 24) |
| `assets/` | figures, UTM class and logo |

Apply and run:

```bash
git clone https://github.com/mit-pdos/xv6-riscv.git && cd xv6-riscv
git checkout fa2ddcb
git apply /path/to/lab10/lab10.patch && make qemu
```

Then, inside xv6:

```
trace 32 grep hello README        # read -> 1023, 965, 453, 0
trace 2129920 grep hello README   # open and close only
sysinfo
```

To rebuild the PDF, run `tectonic report.tex`.

The complete tree with Lab 10 already applied (and Lab 13 on top) is in [`../lab13/xv6-riscv`](../lab13/xv6-riscv/).
