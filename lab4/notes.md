# Laboratory 4 Notes & Observations: The xv6 Shell from the Outside

## Metadata
- **Course**: Operating Systems (FCIM / FAF, UTM, 2026-2027)
- **Module**: Lab 4 (Track B: Build Your Own Small OS, xv6)
- **Source Root**: xv6 RISC-V implementation. Copied `user.h` declares `sleep(int)`; the nested tree has no Git metadata, so its exact revision is unverified.
- **Evidence status (2026-10-10)**: The report now includes twelve genuine terminal captures from Dev1 Debian GNU/Linux 13 and a focused QEMU check of the xv6 line-editing keys. Dev1 is remote; the captures do not establish that the assigned course laptop or VM was used. The temporary build used official Debian packages extracted under `/tmp`; host packages and services were not changed.

---

## Part 1. Fix Sleep for the Current xv6

### System Call Versioning Check
- The copied course tree's `user/user.h` declares `int sleep(int);`.
- The handout says to inspect the header first. If it declares `pause(int)`, change the call in `sleep.c` to `pause(atoi(argv[1]))`; otherwise use the declared `sleep(int)` call. The handout associates the rename with August 2025.
- The 9 October serial transcript records `sleep` without an argument printing the usage message and `sleep 20` returning to the prompt; measured wall time was 1.96 seconds. The report's matching figure is a genuine 10 October terminal capture.
- The copied `Makefile` contains `$U/_sleep` and `$U/_args` entries. `args.c` matches the course tree's source copy; the lab4 `Makefile` matches the course tree's Makefile.

### Focused QEMU run
- `sudo -n true` returned exit code 1 with `sudo: a password is required`; no system package installation was possible.
- Debian packages were downloaded from the configured official `deb.debian.org` repository and extracted into `/tmp/codex-os-lab4-riscv-20261009/rootfs`. The isolated prefix used official Debian packages: `gcc-riscv64-unknown-elf` 14.2.0+19, `binutils-riscv64-unknown-elf` 2.44-3+7+b1, `qemu-system-riscv` 10.0.13+ds-0+deb13u1, `opensbi` 1.6-1, `bc` 1.07.1-4, `gcc` 4:14.2.0-1, and `gcc-x86-64-linux-gnu` 4:14.2.0-1. The host already had the GCC 14 backend and QEMU shared-library dependencies; a temporary `gcc` alias used its installed `x86_64-linux-gnu-gcc-14` binary.
- An 81-file, 283,120-byte temporary copy of `lab12/xv6-riscv` was built with the Lab 4 `sleep.c`, `args.c`, and `Makefile`. `make qemu` exited 0.
- `sleep 20` returned to the shell prompt after 1.96 seconds measured wall time. Running `sleep` without a value printed `usage: sleep <ticks>`.
- `args one two three` reported `argc = 4` and the expected four entries. `args *.c "x y"` reported `argc = 4`, with `*.c`, `"x`, and `y"` as literal arguments.
- The serial transcript is saved at `D:/ops/uni/os-lab3-4/lab4-xv6-smoke.log` (SHA-256 `1508AB7556AD6E828D1A6138A4E96F18A9339721F68598376DA8896822D894AB`). The run came from a temporary copy; the report's screenshots show live terminal sessions from Dev1 Debian GNU/Linux 13.

---

## Part 2. Bash Versus the xv6 Shell

### Comparison Matrix

The matrix records observed output for the nine shell-command rows in Bash and xv6. Bash Up-arrow, Tab, and Ctrl+R behavior was checked interactively. A focused QEMU interaction found no xv6 Up-arrow recall or Ctrl+R search; Tab at an empty prompt produced no completion list. Path-prefix completion was not tested. The adjacent command figures are genuine terminal captures.

| Command / Feature | Bash (Linux) Behavior | xv6 Shell Behavior | Underlying Mechanism / Difference |
| :--- | :--- | :--- | :--- |
| **Redirection**<br>`echo hello > f ; cat < f` | Writes `hello` to `f`, reads and prints `hello`. | Supported. Creates `f` and reads via `cat < f`. | Bash opens each target and arranges the requested descriptor. In this xv6 source, `runcmd()` closes descriptor 1 or 0, then `open()` returns the lowest free descriptor (`user/sh.c`, lines 83–91); xv6-specific `O_CREATE` flags are not Bash flags. |
| **Pipe**<br>`ls \| grep READ` | Pipes directory stream to `grep`, outputs matching line. | Supported. `ls` output passes through kernel pipe buffer. | Each shell connects the producer's stdout to the consumer's stdin through a kernel pipe. xv6 does this with `pipe()`, `fork1()`, `close()`, and `dup()` in `runcmd()` (`user/sh.c`, lines 101–123). |
| **Grouping / List**<br>`(echo a; echo b) \| wc` | Prints `2 2 4`. | Prints `2 2 4`. | The tested outputs match. xv6 has no `PAR` command node: `parseexec()` delegates to `parseblock()`, which returns the nested list; `parsepipe()` then uses that list as the producer side (`user/sh.c`, lines 367–378 and 405–431). |
| **Sequence**<br>`echo one ; echo two` | Prints `one`, then `two`. | Supported. Prints `one`, then `two`. | xv6 defines `LIST` command type (line 11 `#define LIST 4`) separated by `;`. |
| **Background**<br>`echo bg &` | Launches asynchronous job in background. | Supported. Spawns child process without calling `wait()`. | xv6 defines `BACK` command type (line 12 `#define BACK 5`) producing `fork()` without `wait()`. |
| **Globbing**<br>`ls *` | Expands `*` to all directory entries. | Fails. Looks for a literal file named `*`. | Bash expands glob patterns before `execve()`; xv6 shell performs no wildcard expansion. |
| **Variables**<br>`echo $HOME` | Expands to `/home/<user>`. | Prints `$HOME` literally. | xv6 shell has no environment variable table or `$` parser. |
| **Quotes**<br>`echo "a b"` | Preserves space, passes single argument `a b`. | Passes `"a` and `b"` as separate tokens including the quote characters. | xv6 tokenizer splits on its whitespace set and has no quote state machine. |
| **PATH / Lookup**<br>`mkdir d ; cd d ; ls ..` | Lists parent-directory entries. | `exec cd failed`; `ls ..` then lists entries from the unchanged root directory. | Bash handles `cd` in the command list and searches `$PATH`; xv6 tries `exec cd` inside the list. At a prompt, `cd d` works, but `ls` fails without `$PATH`. |
| **Line Editing**<br>Arrows, Tab, Ctrl+R | Up-arrow history, Tab completion, and Ctrl+R reverse search were confirmed interactively. | Up/Ctrl+R showed no history or search; Tab at an empty prompt produced no completion list. | Path-prefix completion was not tested. Source inspection found no history, completion, or reverse-search handler in the xv6 console. |

### Answers to Observe Questions (Part 2)
1. **List the features both shells have, and the ones only bash has:**
   - **Both shells have**: Basic command execution, input/output redirection (`<`, `>`), pipes (`|`), the tested parenthesized list in a pipeline (`(echo a; echo b) | wc`), sequential command execution (`;`), and background execution (`&`). The grouped xv6 command returned `2 2 4`. In xv6 this input is represented by nested `LIST` and `PIPE` nodes; there is no `PAR` node.
   - **Only bash has**: Globbing (`*`, `?`, `[...]`), environment variables (`$VAR`), quote processing (`"..."`, `'...'`), conditional chaining (`&&`, `||`), PATH resolution, command history, and tab completion.
2. **In xv6, `ls` stops working after `cd d`. Why? Find a way to run `ls` from inside `d` anyway:**
   - At the prompt, `cd d` succeeds. xv6 has no `$PATH` lookup, so `ls` is resolved relative to `d` and fails.
   - The captured working alternative is `../ls ../README`; it invokes the `ls` executable from the parent directory and lists `README`.
3. **Which missing feature would you miss most in daily work, and which would be easiest to add?**
   - **Most missed in daily work**: `$PATH` lookup and tab completion/history. Without `$PATH`, navigating directories breaks all standard tool invocations unless absolute paths are typed.
   - **Easiest to add**: A basic `$PATH` fallback loop in `user/sh.c`. If `exec(cmd, argv)` returns failure, prepend `"/bin/"` or `"/"` to `cmd` and retry `exec` once before failing.

---

## Part 3. Who Expands `*`? Program Arguments Analysis

### Implementation Comparison
- `user/args.c` (xv6):
  ```c
  #include "kernel/types.h"
  #include "user/user.h"
  int main(int argc, char *argv[]) {
    printf("argc = %d\n", argc);
    for(int i = 0; i < argc; i++)
      printf("argv[%d] = [%s]\n", i, argv[i]);
    exit(0);
  }
  ```
- `args_linux.c` (Linux):
  ```c
  #include <stdio.h>
  int main(int argc, char *argv[]) {
    printf("argc = %d\n", argc);
    for(int i = 0; i < argc; i++)
      printf("argv[%d] = [%s]\n", i, argv[i]);
    return 0;
  }
  ```

### Illustrative Linux Example and Measured xv6 Output for `args *.c "x y"`

#### Illustrative Bash output (not run in the 9 October QEMU check):
```
$ ./args *.c "x y"
argc = 4
argv[0] = [./args]
argv[1] = [args.c]
argv[2] = [args_linux.c]
argv[3] = [x y]
```
*(Assuming `args.c` and `args_linux.c` are present in directory).*

#### Measured xv6 output, from the retained serial transcript:
```
$ args *.c "x y"
argc = 4
argv[0] = [args]
argv[1] = [*.c]
argv[2] = ["x]
argv[3] = [y"]
```

### Answers to Observe Questions (Part 3)
1. **Paste both outputs for `args *.c "x y"`. How many arguments did each program receive?**
   - In Linux: Received 4 arguments (`argv[0]` through `argv[3]`). The glob `*.c` expanded to matching file names, and `"x y"` was parsed as a single argument without quotes.
   - In xv6: Received 4 arguments, but `*.c` remained a literal string, and `"x y"` was split on the space into two separate strings `["x]` and `[y"]`.
2. **Who turns `*.c` into file names and removes quotes: the program, the kernel, or the shell?**
   - **The shell**. The shell performs lexical scanning, globbing, variable expansion, and quote removal prior to invoking `exec()`. The kernel merely accepts the final array of null-terminated strings (`char *argv[]`) and copies them to the child process's stack. The user program receives whatever pointers the kernel placed in its address space.
3. **What happened to the extra spaces in `one   two   three`?**
   - Both shells treat these literal spaces as command-line word boundaries, and xv6's `gettoken()` skips every character in its `whitespace[]` set before reading the next token (`user/sh.c`, lines 268–313). The output contains three argument strings: `"one"`, `"two"`, and `"three"`. Bash's `IFS` is relevant to word splitting on unquoted expansion results, a later expansion step; it is not the lexer for literal spaces.

---

## Part 4. Read the xv6 Shell Source (`user/sh.c`)

### Shell Architecture Findings
- Source line count: 500 lines (`wc -l user/sh.c`).
- Five parsed command types defined in `user/sh.c` (lines 8–12):
  1. `EXEC` (`#define EXEC 1`): Basic executable command (no operator character).
  2. `REDIR` (`#define REDIR 2`): I/O redirection; produced by `<` or `>`.
  3. `PIPE` (`#define PIPE 3`): Pipeline; produced by `|`.
  4. `LIST` (`#define LIST 4`): Sequential list; produced by `;`.
  5. `BACK` (`#define BACK 5`): Background job; produced by `&`.

### Answers to Observe Questions (Part 4)
1. **Name the five kinds of command the xv6 shell knows and the character that produces each:**
   - `EXEC` (plain command invocation)
   - `REDIR` (produced by `<` and `>`)
   - `PIPE` (produced by `|`)
   - `LIST` (produced by `;`)
   - `BACK` (produced by `&`)
2. **Where is `cd` handled, and why is it not run as a separate program?**
   - `cd` is intercepted inside the main shell loop in `main()` of `user/sh.c` (lines 166–170):
     ```c
     if(cmd[0] == 'c' && cmd[1] == 'd' && cmd[2] == ' '){
       // Chdir must be called by the parent, not the child.
       cmd[strlen(cmd)-1] = 0;  // chop \n
       if(chdir(cmd+3) < 0)
         fprintf(2, "cannot cd %s\n", cmd+3);
     }
     ```
   - It cannot be run as a separate program because `fork()` gives the child separate process state for its current directory. If `cd` were external, `chdir()` in the child would change only that child directory, leaving the shell process unchanged.
3. **Search `sh.c` for any code that handles `*` or `$`. What does that explain about Part 2?**
   - Searching `sh.c` for `*` or `$` yields zero parsing logic for glob expansion or variable substitution. The characters `*` and `$` are ordinary word characters to `gettoken()`. This confirms why xv6 outputs literal `$HOME` and `*.c` without expansion.
