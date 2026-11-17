# Lab 13 – Semaphores in Your Own Kernel (xv6)

| File | Content |
|---|---|
| `notes.txt` | the four Observe answers, Check 1 and Check 2, as the brief asks |
| `report.pdf`, `report.tex` | UTM report with figures |
| `lab13.patch` | the Lab 13 change on top of Lab 10 (9 files, +212 lines) |
| `lab10-13.patch` | the whole change against clean upstream xv6 (Lab 10 and Lab 13) |
| `xv6-commits/` | the four Lab 13 commits as `git format-patch` files |
| `xv6-riscv/` | the complete modified xv6 tree (upstream `fa2ddcb` + Lab 10 + Lab 13): `cd xv6-riscv && make qemu` |
| `experiments/` | `wakeall.c` and the two temporary kernel changes used for Observe 3 and 4 (not in the tree) |
| `evidence/` | the QEMU console output behind every figure |
| `brief.pdf`, `assets/` | the handout; figures, UTM class and logo |

System calls: `sem_init` 24, `sem_down` 25, `sem_up` 26, the optional `sem_trydown` 27.
`trace` (Lab 10) stays 23. The optional `sysinfo` of Lab 10 moved from 24 to 28.

Run the committed tree directly:

```bash
cd lab13/xv6-riscv && make qemu
```

Or apply the change to a clean upstream tree:

```bash
git clone https://github.com/mit-pdos/xv6-riscv.git && cd xv6-riscv
git checkout fa2ddcb
git apply /path/to/lab13/lab10-13.patch
make qemu
```

Then, inside xv6:

```
semtest                     # child after parent, ping/pong, semtest: OK
mix                         # letters mixed
mix lock                    # every line whole
trydown                     # optional: 0, 0, -1
trace 117440512 semtest     # only sem_init, sem_down, sem_up
```

To rebuild the PDF, run `tectonic -X compile report.tex`.
