# Laboratory 4 Notes & Observations: The xv6 Shell from the Outside

## Metadata
- **Course**: Operating Systems (FCIM / FAF, UTM, 2026-2027)
- **Module**: Lab 4 (Track B: Build Your Own Small OS, xv6)
- **Environment**: Debian GNU/Linux 13, GNU Bash 5.2.37, RISC-V GCC 14, QEMU 10 (`qemu-system-riscv64`)

---

## Part 1. Fix Sleep for the Current xv6

### System Call Check and QEMU Run
- Upstream `mit-pdos/xv6-riscv` renamed `sleep(int)` to `pause(int)` in August 2025; the handout asks to check `user/user.h` first and match whichever declaration the tree provides.
- The pinned Lab 2 tree in this repository declares `int sleep(int);`, so the Lab 4 overlay calls `sleep(atoi(argv[1]))` and matches `lab2/Makefile` with `$U/_sleep` and `$U/_args` in `UPROGS`.
- In QEMU, `sleep` without an argument printed `usage: sleep <ticks>`, and `sleep 20` returned to the prompt after ~1.96 s (matching the 0.1 s xv6 timer tick).
- `args one two three` printed `argc = 4` with the three arguments; `args *.c "x y"` printed `argc = 4` with `*.c`, `"x`, and `y"` passed literally.

---

## Part 2. Bash Versus the xv6 Shell

### Comparison Matrix

Each command below was run in both GNU Bash and the xv6 shell. Up-arrow history, Tab completion, and Ctrl+R search were tested interactively; `user/sh.c` and the xv6 console have no handler for any of them.

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

### Output of `args *.c "x y"` in bash and in xv6

#### bash, in a directory holding `a.c`, `args_linux.c` and `b.c` (report Figure 3.3):
```
$ ./args *.c "x y"
argc = 5
argv[0] = [./args]
argv[1] = [a.c]
argv[2] = [args_linux.c]
argv[3] = [b.c]
argv[4] = [x y]
```

#### xv6:
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
   - In Linux: Received 5 arguments (`argv[0]` through `argv[4]`). The glob `*.c` expanded to matching file names, and `"x y"` was parsed as a single argument without quotes.
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
