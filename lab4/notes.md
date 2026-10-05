# Laboratory 4 Notes & Observations: The xv6 Shell from the Outside

## Metadata
- **Course**: Operating Systems (FCIM / FAF, UTM, 2026-2027)
- **Module**: Lab 4 (Track B: Build Your Own Small OS, xv6)
- **Source Root**: xv6 RISC-V implementation

---

## Part 1. Fix Sleep for the Current xv6

### System Call Versioning Check
- Header inspection in `user/user.h`:
  ```bash
  grep -n "pause\|sleep" user/user.h
  ```
  - Pinned repository checkout (revision `9374395cd3dc`): declares `int sleep(int);` on line 25.
  - Upstream xv6 revisions (post-August 2025): renamed to `int pause(int);` to avoid naming collision with POSIX sleep semantics.
- Execution behavior in xv6 shell:
  - `$ sleep 20`: Suspends the user process for 20 clock ticks, then returns cleanly to the shell prompt `$`.
  - `$ sleep`: Detects `argc != 2`, prints `usage: sleep <ticks>` to stderr (file descriptor 2), and calls `exit(1)`.

---

## Part 2. Bash Versus the xv6 Shell

### Comparison Matrix

| Command / Feature | Bash (Linux) Behavior | xv6 Shell Behavior | Underlying Mechanism / Difference |
| :--- | :--- | :--- | :--- |
| **Redirection**<br>`echo hello > f ; cat < f` | Writes `hello` to `f`, reads and prints `hello`. | Supported. Creates `f` and reads via `cat < f`. | Both shells open file descriptors with `O_CREATE \| O_WRONLY` (for `>`) and `O_RDONLY` (for `<`) using `dup()`/`close()`. |
| **Pipe**<br>`ls \| grep READ` | Pipes directory stream to `grep`, outputs matching line. | Supported. `ls` output passes through kernel pipe buffer. | Both implement `pipe()`, `fork()`, and file descriptor redirection (`dup()`). |
| **Grouping / List**<br>`(echo a; echo b) \| wc` | Subshell grouping executed, piped to `wc`. | Not supported. Parentheses `(...)` are not parsed. | Bash supports compound commands; xv6 `sh.c` has no syntax node for subshell grouping. |
| **Sequence**<br>`echo one ; echo two` | Prints `one`, then `two`. | Supported. Prints `one`, then `two`. | xv6 defines `LIST` command type (line 11 `#define LIST 4`) separated by `;`. |
| **Background**<br>`echo bg &` | Launches asynchronous job in background. | Supported. Spawns child process without calling `wait()`. | xv6 defines `BACK` command type (line 12 `#define BACK 5`) producing `fork()` without `wait()`. |
| **Globbing**<br>`ls *` | Expands `*` to all directory entries. | Fails. Looks for a literal file named `*`. | Bash expands glob patterns before `execve()`; xv6 shell performs no wildcard expansion. |
| **Variables**<br>`echo $HOME` | Expands to `/home/<user>`. | Prints `$HOME` literally. | xv6 shell has no environment variable table or `$` parser. |
| **Quotes**<br>`echo "a b"` | Preserves space, passes single argument `a b`. | Passes `"a` and `b"` as separate tokens (or literal quotes). | xv6 tokenizer splits strictly on spaces and has no quote state machine. |
| **PATH / Lookup**<br>`mkdir d ; cd d ; ls ..` | Finds `ls` in `/usr/bin` despite working directory `d`. | `exec ls failed`. xv6 cannot find `ls`. | Linux uses `$PATH`; xv6 only looks in the current directory (`d/ls`). Alternative: `/ls ..`. |
| **Line Editing**<br>Arrows, Tab, Ctrl+R | Readline library history, completion, searching. | Prints raw escape sequences or does nothing. | xv6 terminal driver (`console.c`) provides minimal line buffering with backspace only. |

### Answers to Observe Questions (Part 2)
1. **List the features both shells have, and the ones only bash has:**
   - **Both shells have**: Basic command execution (`exec`), input/output redirection (`<`, `>`), single pipes (`|`), sequential command execution (`;`), and background execution (`&`).
   - **Only bash has**: Globbing (`*`, `?`, `[...]`), environment variables (`$VAR`), quote handling (`"..."`, `'...'`), subshell grouping (`(...)`), conditional chaining (`&&`, `||`), PATH resolution, command history, and tab completion.
2. **In xv6, `ls` stops working after `cd d`. Why? Find a way to run `ls` from inside `d` anyway:**
   - xv6 has no `$PATH` environment variable mechanism. When a command like `ls` is entered, `user/sh.c` invokes `exec("ls", argv)`. The xv6 kernel interprets relative paths starting from the current directory `d`. Because `ls` resides in the filesystem root `/`, the lookup for `d/ls` fails.
   - Working alternative from inside `d`: Specify the absolute path `/ls` (e.g., `/ls` or `/ls ..`).
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

### Experimental Output for `args *.c "x y"`

#### In Bash (Linux):
```
$ ./args *.c "x y"
argc = 4
argv[0] = [./args]
argv[1] = [args.c]
argv[2] = [args_linux.c]
argv[3] = [x y]
```
*(Assuming `args.c` and `args_linux.c` are present in directory).*

#### In xv6 Shell:
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
   - The shell parses whitespace as argument delimiters (Internal Field Separator). Consecutive spaces are discarded by the lexer during argument tokenization, resulting in exactly three distinct argument strings: `"one"`, `"two"`, and `"three"`.

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
   - It cannot be run as a separate program because each child program executes in a separate process address space after `fork()`. If `cd` were an external binary, only the child process would change its directory, leaving the shell in the original working directory upon process termination.
3. **Search `sh.c` for any code that handles `*` or `$`. What does that explain about Part 2?**
   - Searching `sh.c` for `*` or `$` yields zero parsing logic for glob expansion or variable substitution. The characters `*` and `$` are simply treated as normal alphanumeric text characters. This confirms why xv6 outputs literal `$HOME` and `*.c` without expansion.
