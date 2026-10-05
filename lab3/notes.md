# Laboratory 3 Notes & Observations: The Command Line

## Metadata
- **Course**: Operating Systems (FCIM / FAF, UTM, 2026-2027)
- **Module**: Lab 3 (Track A: Linux Shell, Pipes and Text Filters)
- **Environment**: Ubuntu Linux / Bash

---

## Part 1. Move Fast, Find Help

### Commands & Interactions
- `ls /usr/sh` + `<Tab><Tab>`: Displays matching completions (`/usr/share/`).
- `cd /et` + `<Tab>`: Completes unambiguously to `cd /etc/`.
- `Ctrl+R`: Initiates reverse incremental history search through commands previously typed in the session.
- `type cd`: `cd is a shell builtin`
- `type ls`: `ls is aliased to 'ls --color=auto'` (or `/usr/bin/ls`)
- `type echo`: `echo is a shell builtin`
- `which ls`: `/usr/bin/ls`
- `echo $PATH | tr ':' '\n'`: Lists each directory in the search path on an independent line.
- `nosuchprog ; echo "exit code: $?"`: Reports exit code `127` (command not found).

### Answers to Observe Questions (Part 1)
1. **Which of `cd`, `ls`, `echo` are built-ins, and why MUST `cd` be one?**
   - `cd` and `echo` are shell built-ins (`ls` is an external binary).
   - `cd` MUST be a built-in because the working directory is an attribute of the process environment. If `cd` were an external executable, the shell would `fork()` a child process to run it; the child would change its own working directory and immediately terminate, leaving the parent shell's working directory unchanged.
2. **How many directories are in your PATH, and in which one is `ls`?**
   - Typically 6 to 9 standard system paths (e.g., `/usr/local/sbin`, `/usr/local/bin`, `/usr/sbin`, `/usr/bin`, `/sbin`, `/bin`).
   - `ls` is located in `/usr/bin/ls` (or `/bin/ls` via symlink).
3. **What exit code does a command that is not found return?**
   - Bash returns exit status `127`.
4. **Which option of `ls` sorts by modification time?**
   - `ls -t` (and `ls -tr` for reverse chronological order).

---

## Part 2. What the Shell Does to Your Line

### Command Expansion & Prediction Table

| Command | Prediction | Real Output | Explanation |
| :--- | :--- | :--- | :--- |
| `echo *.c` | List all `.c` files | `a.c b.c` | The shell expands glob `*.c` before calling `echo`. |
| `echo file?.txt` | Match `file1.txt` and `file2.txt` | `file1.txt file2.txt` | `?` matches exactly one character. |
| `echo [a-b]*` | Match files starting with `a` or `b` | `a.c b.c` | Character class `[a-b]` expands to matching directory entries. |
| `echo *.xyz` | Literal string `*.xyz` | `*.xyz` | When no matching file exists, bash preserves the literal pattern unless `nullglob` is set. |
| `ls alfa beta.txt` | Fails or searches two files | `ls: cannot access 'alfa': No such file or directory`<br>`ls: cannot access 'beta.txt': No such file or directory` | Shell splits unquoted words by IFS (space) into two distinct arguments `alfa` and `beta.txt`. |
| `ls "alfa beta.txt"` | Lists the file with space | `'alfa beta.txt'` | Double quotes prevent word splitting across whitespace. |
| `echo '$HOME' "$HOME" \$HOME` | Literal, expanded, escaped | `$HOME /home/user $HOME` | Single quotes suppress expansion; double quotes expand variables; backslash escapes `$`. |
| `echo {1..5} ; echo $((7 * 6))` | Numbers 1 to 5; arithmetic 42 | `1 2 3 4 5`<br>`42` | Brace expansion generates sequence; `$((...))` evaluates arithmetic. |
| `echo "today is $(date +%A), I am $(whoami)"` | Current weekday and username | `today is Monday, I am <user>` | Command substitution executes commands in subshells and substitutes output. |
| `touch log{1..3}.txt && ls log*` | Creates 3 files and lists them | `log1.txt log2.txt log3.txt` | Brace expansion creates `log1.txt`, `log2.txt`, `log3.txt`; glob lists all three. |

### Answers to Observe Questions (Part 2)
1. **`echo` knows nothing about files, yet `echo *.c` printed file names. Who produced them?**
   - The shell expanded the glob pattern `*.c` against the filesystem before executing `echo`. `echo` merely receives the expanded strings as individual arguments `argv[1] = "a.c"` and `argv[2] = "b.c"`.
2. **Why did `ls alfa beta.txt` fail? Give two different ways to fix it.**
   - It failed because unquoted whitespace causes the shell to split the input into two arguments: `alfa` and `beta.txt`. Neither file exists individually.
   - Fix 1: Enclose in quotes: `ls "alfa beta.txt"` (or `ls 'alfa beta.txt'`).
   - Fix 2: Escape the whitespace with a backslash: `ls alfa\ beta.txt`.
3. **What is the difference between single and double quotes?**
   - Single quotes (`'...'`) treat every enclosed character literally, disabling all variable substitution (`$`), command substitution (`$(...)`), and arithmetic expansion.
   - Double quotes (`"..."`) preserve whitespace and prevent globbing/word splitting, but allow variable expansion (`$VAR`), command substitution (`$(command)`), and backslash escaping.
4. **Why does `ls` show `'alfa beta.txt'` in quotes?**
   - Modern GNU `ls` defaults to quoting filenames containing spaces or shell metacharacters so the output can be safely copy-pasted back into a shell prompt without ambiguity.

---

## Part 3. Redirection, Chaining and Jobs

### Redirection Experiments
- `ls /etc /nope > out.txt 2> err.txt`:
  - `out.txt`: receives directory listing for `/etc` (file descriptor 1, stdout).
  - `err.txt`: receives error `ls: cannot access '/nope': No such file or directory` (file descriptor 2, stderr).
- `ls /etc /nope > all.txt 2>&1`: Both stdout and stderr are written into `all.txt`.
- `ls /etc /nope 2>&1 > all.txt`: Stderr is redirected to the original destination of stdout (terminal screen); then stdout is redirected to `all.txt`. Thus error messages print to terminal while listing writes to `all.txt`.
- `echo first > notes.md ; echo second >> notes.md`: `>` overwrites or creates; `>>` appends to existing file.
- `wc -l < access.log`: Shell opens `access.log` and attaches it to stdin (file descriptor 0). `wc` reads from stdin and does not know the filename, printing only `500`.

### Answers to Observe Questions (Part 3)
1. **Which file got the error message, and which got the listing?**
   - `err.txt` received the error message; `out.txt` received the listing.
2. **What is the difference between `> all.txt 2>&1` and `2>&1 > all.txt`?**
   - Redirections are evaluated strictly from left to right.
   - In `> all.txt 2>&1`: stdout is directed to `all.txt`; then descriptor 2 (stderr) is redirected to descriptor 1 (`all.txt`). Both channels write to the file.
   - In `2>&1 > all.txt`: descriptor 2 is redirected to where descriptor 1 currently points (the terminal); then descriptor 1 is redirected to `all.txt`. Stderr stays on terminal.
3. **Why does `wc -l < access.log` print only a number, while `wc -l access.log` also prints the filename?**
   - When given a filename argument, `wc` opens the path itself and formats the output line with the file name.
   - When redirected via `<`, the shell opens the file and passes it on descriptor 0 (standard input). `wc` receives no path argument and outputs only the counted number.
4. **Explain each operator in one sentence: `;`, `&&`, `||`.**
   - `;`: Executes the following command unconditionally after the preceding command completes.
   - `&&`: Executes the following command only if the preceding command exited with status 0 (success).
   - `||`: Executes the following command only if the preceding command exited with non-zero status (failure).

---

## Part 4. One-Liners & Verification (`access.log`)

### Verified Pipeline Outputs (Dataset: 500 lines)

- **Q1. How many requests failed?**
  - Command: `grep -c FAIL access.log`
  - Output: `100`
- **Q2. How many different pages were requested, and which?**
  - Command: `cut -d' ' -f5 access.log | sort -u`
  - Output:
    ```
    /page0
    /page1
    /page2
    /page3
    ```
  - Total unique pages: 4.
- **Q3. How many requests did each page get?**
  - Command: `cut -d' ' -f5 access.log | sort | uniq -c`
  - Output:
    ```
    125 /page0
    125 /page1
    125 /page2
    125 /page3
    ```
  - Check: 125 * 4 = 500 total requests.
- **Q4. Which user or users have the most failed requests, and how many?**
  - Command: `grep FAIL access.log | cut -d' ' -f3 | sort | uniq -c | sort -rn | head -n 2`
  - Output:
    ```
    15 user3
    15 user5
    ```
  - Both `user3` and `user5` share the maximum with 15 failed requests.
- **Q5. How many requests did user3 make, and how many of them failed?**
  - Command: `echo "user3 total: $(grep -c 'user3 ' access.log), failed: $(grep 'user3 ' access.log | grep -c FAIL)"`
  - Output: `user3 total: 71, failed: 15`
- **Q6. Print the last 3 failed requests, showing only time and user.**
  - Command: `grep FAIL access.log | tail -n 3 | cut -d' ' -f2,3`
  - Output:
    ```
    10:10 user1
    10:15 user6
    10:20 user3
    ```
- **Q7. Which login shells appear in `/etc/passwd`, and how many accounts use each?**
  - Command: `cut -d: -f7 /etc/passwd | sort | uniq -c | sort -rn`
  - Typical system output: `/usr/sbin/nologin`, `/bin/false`, `/bin/bash`, `/bin/sync`.
- **Q8. Explain why `ls /etc | wc -l` and `ls -l /etc | wc -l` differ by exactly one.**
  - `ls -l` outputs an introductory summary line `total <blocks>` specifying filesystem block allocation before displaying entries. Non-long `ls` piped to a stream prints exactly one entry per line without the summary line.
- **Bonus (+1): Lines where the minute ends in 0 and request failed:**
  - Command: `grep -E '10:[0-5]0 .* FAIL' access.log`
  - Count: `50` matches. Because every minute ending in 0 (00, 10, 20, 30, 40, 50) is divisible by 5, all 50 occurrences in the dataset resulted in FAIL.

---

## Part 5. Shell Scripting (`report.sh`)

### Script Implementation
The script checks for file existence, calculates total requests and failures, and iterates through `user0` to `user6`.

### Answers to Observe Questions (Part 5)
1. **What does `#!/bin/bash` do, and what happens if you run `./report.sh` before `chmod +x`?**
   - The shebang `#!/bin/bash` instructs the operating system kernel (`execve`) which interpreter binary to launch to execute the script.
   - Running `./report.sh` before setting executable permissions yields `bash: ./report.sh: Permission denied`.
2. **Why must you type `./report.sh` and not just `report.sh`?**
   - The shell only searches directories enumerated in `$PATH`. The current working directory (`.`) is intentionally excluded from `$PATH` for security reasons. Prefacing with `./` provides an explicit path.
3. **Why does the script write errors with `>&2` and terminate with `exit 1`?**
   - `>&2` redirects the error message to standard error (descriptor 2), keeping diagnostic messages distinct from standard output (data).
   - `exit 1` returns a non-zero exit code to signal abnormal termination to the calling environment or pipeline.

### Cron Bonus
- Crontab entry:
  ```crontab
  * * * * * /home/user/os-lab3/report.sh /home/user/os-lab3/access.log >> /home/user/os-lab3/report.log 2>&1
  ```
- Result: Appends automated run summary to `report.log` every minute.
