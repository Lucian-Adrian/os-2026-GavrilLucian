# Lab 9 – Watching System Calls with strace

Lucian-Adrian Gavril, FAF-241. The full report with figures is `report.pdf`. The raw traces are in `evidence/`.

## Part 1
**Which system call does ls use to print to the screen? To which descriptor does it write?**
It uses `write` on descriptor 1 (standard output): `write(1, "total 16\n...", 250) = 250`. The whole listing goes out in one call because stdio buffers the lines and flushes them at exit. With the filter, `ls -l` makes 87 calls (39 openat, 33 close, 14 read, 1 write); with no filter it makes 214.

## Part 2
**The descriptor returned by the first openat is 3, not 0, 1 or 2. Why are those three already taken?**
Every process inherits 0 (stdin), 1 (stdout) and 2 (stderr) already open from the shell, through fork and exec. The kernel returns the lowest free descriptor, which is 3. When the program is started with stdin closed (`./syscalls 0<&-`), the same `open` returns 0.

## Part 3
- `./syscalls` makes 41 system calls; 6 of them come from `main`, and the rest is program startup.
- `write` counts: `ls -l /` makes 1, `seq 1 100000` makes 72 (588895 bytes), and a sh loop of 5 echos makes 5.
- The same printf program makes 1 write into a pipe (80 bytes, full buffering) and 3 writes on a terminal (line buffering).
