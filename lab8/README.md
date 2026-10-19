# Lab 8: the same calls inside xv6

This lab uses the process and file-descriptor calls inside xv6. The required program follows `fork`, `exec` and `wait`; the pipe exercise sends a one-byte ping and pong between a parent and child. The optional primes exercise connects small filter processes with pipes.

The current assignment is the Moodle resource [The Same Calls Inside Your Own OS (xv6)](https://else.fcim.utm.md/mod/resource/view.php?id=72240), resource 72240. Use the English handout as the authority for the required questions and submission format.

## Files

The printable [report.pdf](report.pdf) is built from [report.tex](report.tex) using the canonical UTM `assets/utmreport.cls` and logo. Build it from this folder with `tectonic -X compile report.tex`.

Seven original live execution screenshots are in `assets/proof-*.png` and embedded in the report: build/boot, echo, the beginning and end of the ls variant, failed exec, pingpong and primes. The reported PIDs match this capture session.

- `user/run.c` is the fixed `echo hello from the child` example.
- `user/pingpong.c` uses one pipe for each direction.
- `user/primes.c` is the optional process-and-pipe filter chain for 2 through 35.
- `Makefile` records these three UPROGS entries while retaining the Lab 2 `sleep` and `args` entries.
- `prepare-overlay.sh` makes a disposable xv6 copy from `lab2/` and registers the Lab 8 programs there.
- `notes.md` contains answers to the required Observe questions and the recorded QEMU observations.
- `teaching-note.md` traces the calls through the actual user and kernel sources.
- [teaching-note.pdf](teaching-note.pdf) provides the visual study route and priority defense questions.
- [report.pdf](report.pdf) is the formal lab report.

The canonical xv6 tree is in [Lab 2](../lab2/README.md). The overlay helper never edits it.

The [recorded execution session](../lab78/execution-session-2026-10-19.txt) preserves the actual build, boot and command output from 19 October 2026.

## Build and run

The overlay requires GNU make, a host C compiler, Perl, a RISC-V GCC toolchain and QEMU. From the OS repository root in WSL:

```sh
cd /path/to/sem5-operating-systems
overlay=$(bash ./lab8/prepare-overlay.sh "$PWD")
cd "$overlay"
make clean
make qemu
```

At the xv6 prompt, run:

```text
$ run
$ pingpong
$ primes
```

`run` starts with the handout's `echo` arguments. To observe the two requested `exec` variants without changing the submitted source, edit only the disposable copy at `$overlay/user/run.c`, replacing the argument array and `exec` target with one of these pairs. Exit QEMU first, then run `make qemu` again from the same overlay directory; Make rebuilds the program and filesystem image from the changed source.

```c
char *args[] = {"ls", 0};
exec("ls", args);
```

```c
char *args[] = {"nosuchprog", 0};
exec("nosuchprog", args);
```

In each variant, retain the `printf("exec failed\n")` and `exit(1)` statements after `exec`. A successful `exec` does not return to them. Quit QEMU with Ctrl-A, then X. The helper prints the overlay path; each call creates a fresh copy, so do not rerun it when you want to rebuild the same variant.
