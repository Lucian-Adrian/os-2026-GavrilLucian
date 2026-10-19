# Lab 4: What a small shell must do

Lab 4 compares Bash with the xv6 shell to show that command syntax is handled in user space. A shell turns the text of a command into arguments, a command tree and file-descriptor connections. It then asks the kernel to create processes, open files and move data through pipes. The same kernel can run two shells with different features because wildcard expansion, variables, quotes and command parsing belong to the shell program.

The lab also traces an xv6 `sleep` program through its system-call interface. That provides a second boundary: user code decides what it asks for, a small generated stub enters the kernel, and kernel code performs the protected wait.

## Keep shell experiments in disposable copies

The source tree used for this lab is [`../lab2`](../lab2). These commands prepare a temporary copy so building and booting do not change the coursework files:

```bash
src=/mnt/d/edu/faf/sem5/os
work=$(mktemp -d /tmp/os-lab4.XXXXXX)
cp -a "$src/lab2/." "$work/"
cp "$src/lab4/sleep.c" "$src/lab4/args.c" "$work/user/"
cp "$src/lab4/Makefile" "$work/Makefile"
grep -n 'pause\|sleep' "$work/user/user.h"
make -C "$work" qemu
```

At the xv6 prompt, compare a missing and present sleep argument, then try:

```text
sleep
sleep 20
args one   two   three
args *.c "x y"
(echo a; echo b) | wc
```

For the Bash version of `args`, build in a separate temporary directory containing known glob matches:

```bash
linuxwork=$(mktemp -d)
cp /mnt/d/edu/faf/sem5/os/lab4/args_linux.c "$linuxwork/"
cd "$linuxwork"
touch a.c b.c
gcc -Wall -Wextra -o args args_linux.c
./args one   two   three
./args *.c "x y"
```

Here `*.c` matches `a.c`, `args_linux.c` and `b.c`. A Bash shell with its usual glob settings leaves an unmatched pattern literal; xv6 always passes `*.c` literally because it has no glob-expansion step.

## The argument vector reveals which shell did the work

The two programs, [`args.c`](args.c) and [`args_linux.c`](args_linux.c), print `argc` and each string in `argv`. They do not parse a command line, expand a star or remove quotes. That makes them a controlled comparison: the program is almost the same, so a difference in its output comes from the shell that prepared its arguments.

![Conceptual illustration of shell argument preparation before a program runs](assets/concept-shell-arguments.png)

The diagram is a high-level aid, not an execution capture or a complete Bash expansion-order specification.

For `./args *.c "x y"` in the temporary Bash directory, the shell expands the star to three filenames and groups `x y` into one argument without the quote marks. `argv[0]` is `./args`, so the program reports `argc = 5`. The argument strings are `./args`, `a.c`, `args_linux.c`, `b.c` and `x y`.

At the xv6 prompt, `args *.c "x y"` produces `argc = 4`: `args`, `*.c`, `"x` and `y"`. xv6 treats the quote characters as ordinary characters and whitespace as a word boundary. The repeated spaces in `args one   two   three` disappear in both shells because literal whitespace separates command words. In Bash, `IFS` is used later when an unquoted expansion result is split; it is not what tokenizes the literal spaces typed between `one`, `two` and `three`. xv6's `gettoken` skips characters from its explicit whitespace set.

## Follow `sleep` across the user-kernel boundary

In [`sleep.c`](sleep.c), `main` first requires exactly one argument after the program name. If `argc` is wrong, it writes the usage message to descriptor 2 and exits with status 1. Otherwise it converts the text in `argv[1]` with `atoi` and calls `sleep`.

In this source tree, [`../lab2/user/user.h`](../lab2/user/user.h) declares `sleep(int)`. The generated system-call stubs are built from [`../lab2/user/usys.pl`](../lab2/user/usys.pl), which contains `entry("sleep")`. The stub uses the syscall number from [`../lab2/kernel/syscall.h`](../lab2/kernel/syscall.h); [`../lab2/kernel/syscall.c`](../lab2/kernel/syscall.c) maps that number to `sys_sleep`, implemented in [`../lab2/kernel/sysproc.c`](../lab2/kernel/sysproc.c). That function waits until the requested number of timer ticks has elapsed. The integer conversion belongs to the user program; waiting on kernel timer state belongs to the kernel.

The [`Makefile`](Makefile) includes `_sleep` and `_args` in `UPROGS`, so the build places them in the xv6 filesystem image. The build and QEMU boot let the shell find these commands as programs. The argument to `sleep` is ticks, not seconds. A recorded run of `sleep 20` took 1.96 seconds, which is an observation from that run rather than a promise about wall-clock duration.

## Read command structure in `user/sh.c`

The shell source is [`../lab2/user/sh.c`](../lab2/user/sh.c). Its five command node types are `EXEC`, `REDIR`, `PIPE`, `LIST` and `BACK`. Constructors such as `execcmd`, `redircmd`, `pipecmd`, `listcmd` and `backcmd` make these nodes. The parser builds a tree; `runcmd` executes it.

Consider the brief's `(echo a; echo b) | wc`. When `parseexec` sees `(`, it calls `parseblock`. The block parses `echo a; echo b` with `parseline`, which returns a `LIST` node. The outer `parsepipe` then wraps that returned tree in a `PIPE` node:

```text
PIPE
|-- LIST
|   |-- EXEC echo a
|   `-- EXEC echo b
`-- EXEC wc
```

There is no `PAR` node. Parentheses tell the parser where the nested command begins and ends; the command inside is represented by the nodes it actually needs. For this example the saved QEMU output from `wc` was `2 2 4`: two words, two lines and four bytes.

The `PIPE` case in `runcmd` creates a kernel pipe and forks two children. The producer closes descriptor 1, duplicates the pipe's write end into descriptor 1, closes the unused pipe endpoints, then runs the left tree. The consumer similarly connects the read end to descriptor 0 before running `wc`. The parent closes its copies and waits for both children. Because the left side is a `LIST`, its first command runs in a child and the second runs after that child completes. Both outputs reach the pipe, and `wc` reads the resulting bytes from standard input.

Redirection uses the same descriptor idea with a different tree node. For `echo hello > f`, `parseredirs` makes a `REDIR` node whose target is descriptor 1. In the `REDIR` case, `runcmd` closes descriptor 1 and calls `open`. Since descriptor 1 is now the lowest free number, the kernel returns 1 for the opened file. The shell then runs `echo` with its output connected to `f`. xv6 uses its own open flags, including `O_CREATE`; these are details of xv6's implementation, not Bash flags.

For `echo one ; echo two`, `parseline` builds a `LIST`. `runcmd` forks the left command, waits, then runs the right. For `echo bg &`, the parser wraps the command in a `BACK` node and its execution forks without waiting at that point. An `EXEC` node calls `exec`, replacing the child process's program image with the requested program.

## Why xv6 handles `cd` specially

At the interactive prompt, `main` checks whether the raw command line begins with `cd ` and calls `chdir` before it forks. The working directory belongs to a process. If a separate `cd` child changed its directory, the parent shell would stay in its old directory, so the next prompt would not reflect the change.

This implementation is deliberately narrower than a general shell builtin. In `mkdir d ; cd d ; ls ..`, the original line begins with `mkdir`, so it does not match the special case. The parser represents the later `cd d` as an `EXEC` command, and `exec` fails because xv6 has no `cd` program. At a prompt after `cd d`, xv6 also has no `PATH` search: `ls` is looked up relative to the current directory and fails. The brief's `../ls ../README` works by naming the executable and file relative to `d`.

The tokenizer confirms what Part 2 showed. In `sh.c`, `whitespace` lists the characters skipped between words, while `symbols` lists `<|>&;()`. The characters `*`, `$`, single quote and double quote are not special symbols there. The tokenizer does not maintain quote state or perform glob and variable expansion, so those characters remain in the argument strings.

## A short speaking route

Begin with the `args` comparison: the same program receives different strings because Bash expands globs and groups quoted words, while xv6 does not. Then draw the tree for `(echo a; echo b) | wc` and trace how `runcmd` connects descriptor 1 to the pipe and descriptor 0 to `wc`. Use `cd` to show why the shell sometimes must act in its own process, then trace `sleep 20` from `atoi` through the syscall stub to `sys_sleep`. Close by naming which decisions belong to the shell and which services belong to the kernel.

## Practice prompts

Try the explanation before checking the answers.

1. Draw the command tree for `(echo a; echo b) | wc`. Which function returns the inner tree, and which function wraps it in a pipe?
2. In the producer branch of `runcmd`, why does `close(1); dup(p[1]);` connect the command's output to the pipe? Why are the extra pipe ends closed?
3. Compare `./args *.c "x y"` in Bash with `args *.c "x y"` in xv6. List each argument and count `argv[0]` too.
4. Compare `cd d` at the xv6 prompt with `mkdir d ; cd d ; ls ..`. Why does the same word `cd` behave differently?
5. Trace `sleep 20` from the characters `20` in `argv[1]` to the kernel's wait. Which layer converts the text, and which layer waits on ticks?
6. If the Bash directory contains no `.c` files, what can happen to `*.c` under default Bash settings? Why is that different from xv6's behavior?
7. Which of the five command types represents a parenthesized command? Explain why parentheses do not create a sixth type.

## Checking notes

1. `parseexec` calls `parseblock`; `parseblock` calls `parseline` and returns the nested `LIST`. The outer `parsepipe` wraps it in `PIPE`. There is no `PAR` node.
2. `close(1)` frees descriptor number 1. `dup(p[1])` returns the lowest free descriptor, which is 1, so writes go to the pipe. Closing unused ends prevents a process from keeping the pipe alive accidentally; the reader can see end-of-file after the last writer closes its copy.
3. In Bash, `argv` is `./args`, `a.c`, `args_linux.c`, `b.c`, `x y`, so `argc` is 5. In xv6 it is `args`, `*.c`, `"x`, `y"`, so `argc` is 4. `argc` includes the program name at index 0.
4. At the prompt, `main` recognizes a line that begins with `cd ` and calls `chdir` in the shell. In the longer list, the whole line begins with `mkdir`, so parsing sends `cd` through `exec` as if it were a program. xv6 has no `cd` executable.
5. `sleep.c` passes the text `20` to `atoi`, then calls the declared user-level `sleep(int)` stub. The stub enters the kernel; syscall dispatch reaches `sys_sleep`, which waits for timer ticks. A tick count does not guarantee an exact number of wall-clock seconds.
6. With default Bash settings, an unmatched glob normally remains the literal `*.c`; shell options can change that. xv6 always treats the star as an ordinary character because it has no glob pass.
7. None. The parenthesized expression is parsed into the command nodes inside it, then used as a child of another node. Here the inner node is `LIST` and the outer node is `PIPE`.

## Source and observation note

The assignment is [`L4_SO.pdf`](L4_SO.pdf). The argument and sleep explanations follow the local C files and the linked xv6 tree. The 1.96-second `sleep 20` result is preserved in [`notes.md`](notes.md) as one QEMU measurement; it does not establish a fixed duration for 20 ticks.
