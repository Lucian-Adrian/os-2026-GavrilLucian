# Lab 9 – Watching System Calls with strace (Linux)

| File | Content |
|---|---|
| `report.pdf`, `report.tex` | UTM report with figures and the Observe answers |
| `report.md` | short Observe answers, as the brief asks |
| `syscalls.c` | open/write/read/close using only system calls |
| `evidence/` | raw strace output used in the figures |
| `assets/` | figures, UTM class and logo |

```bash
gcc -Wall -Wextra -o syscalls syscalls.c && ./syscalls
strace -e trace=openat,write,read,close ./syscalls
strace -f -e trace=openat,read,write,close ls -l
strace -c ./syscalls
```

To rebuild the PDF, run `tectonic report.tex`.
