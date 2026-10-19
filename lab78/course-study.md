# Operating systems, command lines, files and processes

This guide follows the four published course sessions: Introduction to OS, Command Line, FileSystem, and Processes, Descriptors, Pipes. It connects their ideas through one practical question: when a person types a command, how does the computer turn that text into a running process, connect its input and output, find files, and safely share the hardware? The examples below use the course labs and the current xv6 and Linux programs. They explain the material covered by those sessions and labs; they do not establish the contents of later, unpublished sessions or the full scope of an exam.

## The operating system stands between programs and hardware

The computer provides a CPU, RAM, persistent storage and devices. If programs managed them directly, each would need to coordinate access; one could overwrite another's memory, claim an already-used device or hold the CPU indefinitely.

The operating system solves this by presenting usable abstractions and enforcing shared rules. A process is the abstraction for a running program. A file and directory are abstractions for persistent data and names. A file descriptor is a process's handle to an input or output stream. The kernel, the privileged core of the operating system, decides how these abstractions map to hardware and who may use them. It schedules processor time, manages memory, resolves paths, communicates with devices and keeps processes isolated.

Programs usually run in user mode, where hardware privilege rules prevent them from performing protected operations directly. The kernel runs with higher privilege. When a program needs a protected service, it requests it through a system call. The processor changes execution into the kernel at a controlled entry point; the kernel checks and performs the operation, then returns a result. The program keeps running in user mode. This boundary lets the kernel reject invalid requests and prevents a normal program from treating another process's memory or device state as its own.

A system-call name in C does not always mean the whole operation is implemented by one kernel function. A library can prepare arguments or add behavior around the kernel request. The useful distinction is between ordinary user-space work, such as formatting text, and the protected operation the program asks the kernel to perform. The Lab 7 programs make that distinction visible: printf formats output in a C library, while fork, open, close, dup, pipe, and waitpid request process or descriptor services from Linux.

The xv6 source makes the boundary especially easy to trace. In Lab 2, user/sleep.c converts the text argument to a number and calls the user-side sleep function. The syscall stub is generated from [user/usys.pl](../lab2/user/usys.pl); it puts the system-call number in the RISC-V a7 register and executes ecall. The trap entry in [kernel/trap.c](../lab2/kernel/trap.c) recognizes that request and calls [kernel/syscall.c](../lab2/kernel/syscall.c), which dispatches the saved number to the kernel implementation. [kernel/syscall.h](../lab2/kernel/syscall.h) assigns the number, and [kernel/sysproc.c](../lab2/kernel/sysproc.c) implements sys_sleep.

~~~mermaid
sequenceDiagram
    participant U as user/sleep.c
    participant T as syscall stub and ecall
    participant K as kernel dispatcher
    participant P as process scheduler
    U->>T: sleep(3)
    T->>K: request with number and arguments
    K->>P: wait for timer ticks
    P-->>K: timer wakeup
    K-->>U: return to user mode
~~~

Inside sys_sleep, the kernel checks the tick count in a loop and calls the separate process helper sleep to block on the ticks channel. A timer interrupt advances ticks and wakes processes on that channel. The system-call sleep is the user-visible request; proc.c:sleep is scheduler machinery used to wait without busy-spinning. When woken, the process becomes runnable and later gets CPU time. The result returns through the saved register state. This path shows why a system call is a controlled transition, not an ordinary user function calling privileged code directly.

Consider the Lab 1 command:

~~~bash
echo "hello operating systems" > note.txt
~~~

The shell reads the line and recognizes the greater-than sign as syntax. Before echo runs, the shell opens note.txt for output and connects the command's descriptor 1 to that file. Echo writes text to descriptor 1. Echo does not need to know that the destination changed from a terminal to a file. The kernel performs the open and write operations, while the shell chooses the connection. This is the basic OS story in miniature: a user-level program uses a stable interface, and the kernel manages the resource underneath it. The example and its permission follow-up are in [Lab 1's study note](../lab1/teaching-note.md).

## A stored program becomes a process

A program is a file containing instructions. A process is a running instance of those instructions with state the kernel tracks. That state includes a process identifier (PID), a current execution point, registers, a virtual address space, a current directory and open descriptors. Two processes can run the same program but have different PIDs and separate process state.

Virtual memory gives each process its own address space. The addresses used by a program are virtual addresses. Hardware translation, configured and protected by the kernel, maps them to physical RAM pages. That mapping lets two processes use the same virtual address without referring to the same physical memory. It also lets the kernel prevent an ordinary process from writing into another process's private memory. A process's virtual address space is not a measure of how much physical RAM it occupies: some pages may not be resident, and memory pages can be shared under implementation-specific rules. Linux often uses copy-on-write after fork, so pages are shared until a process changes them. The xv6 implementation is an educational system and its exact memory-management choices are visible in its own source, especially [kernel/proc.c](../lab2/kernel/proc.c).

The processor can execute only a limited number of instruction streams at once. The scheduler chooses which runnable process receives a CPU. On one core, the operating system can switch between processes so each makes progress over time. That overlapping progress is concurrency. With multiple cores, two processes may actually execute at the same time, which is parallelism. Parallel execution is one way to achieve concurrency, but concurrency does not require multiple cores. A scheduler can interrupt one process and run another even if neither program explicitly yields.

A process that is runnable can be selected by the scheduler. A process that is blocked or sleeping is waiting for an event, such as input, a timer tick or pipe data. While it waits, the kernel can let another runnable process use the CPU. This is different from repeatedly checking a condition in a tight loop, called busy waiting, which consumes processor time without useful progress. A wakeup generally changes the process to runnable; it does not promise that the process runs immediately. Another process may be scheduled first.

Lab 1 illustrates this from Linux with sleep 30 &, a PID, ps and /proc/PID/status. The process remains present while it sleeps, but it is not continuously executing. Lab 2 follows the xv6 version more deeply with sleep 3: user/sleep.c requests a delay in timer ticks, kernel/sysproc.c checks the tick count and kernel/proc.c puts the process to sleep. When a timer interrupt advances the ticks, the kernel wakes the process. It then waits for its turn on the scheduler. The relevant path is in [user/sleep.c](../lab2/user/sleep.c), [kernel/sysproc.c](../lab2/kernel/sysproc.c), [kernel/trap.c](../lab2/kernel/trap.c) and [kernel/proc.c](../lab2/kernel/proc.c). A tick is not necessarily one second; the call asks for ticks, not a wall-clock duration.

## The shell turns text into arguments and connections

The command line is a small language interpreted by a shell. A shell is an ordinary user program. It reads characters, recognizes syntax, prepares arguments and requests the kernel to start external commands. For an external program, the shell commonly creates a child process with fork and replaces the child's program with exec. The kernel supplies the new process with an argument count and an argument vector: argv[0] conventionally names the program, and later elements contain the remaining argument strings.

In the Lab 7 [run.c](../lab7/run.c), fork returns zero in the child and the child's positive PID in the parent; a negative value reports failure. Both parent and child continue after the call, but take different branches. The child calls execlp to search PATH and replace its program with ls. A successful exec keeps the same process and PID but never returns to the old instructions. If the command cannot be found, exec returns an error and the child reaches the perror and exit path. The parent calls waitpid for that particular child. It should test WIFEXITED before reading WEXITSTATUS because a wait status encodes more than one kind of termination.

[zombie.c](../lab7/zombie.c) delays waitpid after its ls child exits. During that interval Linux keeps a small process-table record with the PID and exit status so the parent can collect it; ps can show the child in state Z. The child is no longer executing. waitpid removes the remaining record. An orphan is a different condition: its parent exits while the child is still running. Linux reparents the child to an init-like reaper, which can later collect it. An orphan is not by definition a zombie, though it can become one briefly after it exits and before its new parent reaps it.

Shell processing happens before the program receives argv. Bash removes quote marks after using them to group words, expands variables, expands patterns such as *.c, and searches PATH for a command name without a slash. A builtin such as cd must run inside the shell because changing the current directory of a child would not change the interactive shell's directory. The program itself normally receives only the resulting strings; it does not receive the original punctuation or learn that a wildcard was used.

Lab 4 provides a direct comparison in [args.c](../lab4/args.c) and [args_linux.c](../lab4/args_linux.c). In Bash, the command

~~~bash
./args *.c "x y"
~~~

might become the strings ./args, a.c, args_linux.c, b.c, and x y if those three C files are in the current directory. The quote marks do not appear in argv, and the space inside them does not split x y into two arguments. The program's argc is 5 because argc counts argv[0]. Change the files in the directory and the wildcard may produce a different vector. Run the comparable command in xv6 and it does not behave like Bash: the supplied xv6 shell supports a smaller grammar and does not provide Bash's wildcard and PATH expansion. A shell's conveniences are not kernel behavior.

Redirection and pipes are also shell syntax, but the actual streams are process descriptors. Descriptor 0 is conventionally standard input, descriptor 1 standard output, and descriptor 2 standard error. These small integers index a process's descriptor table. An entry refers to an open kernel object, such as a file or one end of a pipe. Changing descriptor 1 changes where a program's output goes without changing the program.

The xv6 shell's implementation in [user/sh.c](../lab2/user/sh.c) makes the rule concrete. For a redirection such as echo hello > f, its parser builds a REDIR command node. During execution, the child closes descriptor 1, opens f, and then runs echo. The kernel allocates the lowest unused descriptor, which is now 1. For a pipeline, the shell creates a pipe, forks a producer and consumer, uses dup to connect the producer's output to the pipe's write end and the consumer's input to its read end, closes unneeded descriptors, then waits. Bash may use different implementation details, but the same descriptor relationships explain the behavior.

## A filesystem separates names from objects

A filesystem presents a directory tree. An absolute path begins at the root directory /. A relative path begins at the process's current working directory. Each directory maps a name to an object recorded by the filesystem. In xv6, that object is described by an inode; the inode stores metadata and references the disk blocks containing file data. A name is not the file's contents, and the inode number is only meaningful within its filesystem.

This separation explains links. A hard link is another directory entry naming the same inode. It does not point to a preferred original. A symbolic link is a separate filesystem object whose contents are a pathname. When a program follows a symbolic link, the filesystem resolves the stored path. If the target name disappears, the symbolic link can remain but become dangling. If another file later appears at that path, the symlink can resolve to that new file.

An open file descriptor follows a different route from a path. A process asks the kernel to open a path. The kernel resolves the name and creates an open-file reference. Reads and writes then use that descriptor and its open-file state, including a current offset, rather than looking up the path from scratch on every call. In the Unix model, descriptors refer to open file descriptions; in xv6, a descriptor points through the process table to a kernel struct file, which stores such state and points to an inode or pipe. After fork, parent and child descriptors refer to the inherited open-file references. They can therefore share an offset. Two independent opens normally create separate open-file state even if both resolve to the same inode.

Metadata inspection follows this same boundary. Lab 6's [mystat.c](../lab6/user/mystat.c) calls a user-library stat helper. In this xv6 tree, [user/ulib.c](../lab2/user/ulib.c) implements that helper with open, fstat and close. The kernel checks the descriptor, reads inode metadata and copies a stat structure into user memory; it does not hand user code a kernel inode pointer. Thus stat reports type, size and link count without reading all file contents. The helper closes its temporary descriptor while the directory name remains.

The difference between directory names and open references is important for unlink. Removing a name removes a directory entry and reduces the inode's link count. If another hard-link name remains, the inode and data remain reachable by that name. If no hard-link names remain but a process still has the file open, that process can continue using its descriptor. Only when the last name and last live reference are gone can the filesystem reclaim the inode and data. In xv6 this is visible across [kernel/sysfile.c](../lab2/kernel/sysfile.c), which handles link and unlink requests, and [kernel/fs.c](../lab2/kernel/fs.c), which releases an unlinked inode. Lab 5's Linux examples show the same distinction between paths, hard links, symlinks and open descriptors; Lab 6 follows the corresponding xv6 data structures and cleanup logic.

The xv6 cleanup condition is precise: the inode is eligible for final reclamation when its hard-link count is zero and the last live reference is being released. In this tree, iput checks ref == 1, valid and nlink == 0 before dropping the caller's final reference. It then frees the file's data blocks and metadata. The link count tracks names in the filesystem; the in-memory reference count tracks active kernel users of the inode. They answer different questions.

Permissions are also metadata checked by the operating system during operations. Traditional Unix permissions divide read, write and execute bits among owner, group and other users. For a regular file, read permits reading its contents, write permits changing contents, and execute permits running it as a program. For a directory, read permits listing names and execute means search or traversal through the directory. Thus permission to read a file is not the same as permission to reach it through every parent directory. Creation modes can also be filtered by a process's umask. These rules explain why a mode such as 600 restricts a file to its owner, while a directory needs its execute/search bit for path traversal. The exact checks can also be affected by ACLs and other system policy, so a three-digit mode is not the whole security model.

## Put the process and descriptor ideas together

The Lab 7 program pipeline.c creates the Linux pipeline ls /etc | wc -l by hand. The parent first calls pipe(p), receiving p[0] for reading and p[1] for writing. It then forks the producer child. That child closes descriptor 1 and duplicates p[1]; because descriptor 1 is the lowest free number, dup returns 1. It closes the original pipe descriptors and calls exec for ls. The running ls process writes its ordinary output to descriptor 1, which now reaches the pipe.

The parent then forks a consumer child. That child closes descriptor 0, duplicates p[0] so the read end becomes standard input, closes the spare pipe descriptors and execs wc -l. Wc reads bytes and counts newline characters. It does not receive a list of directory entries as structured objects. It receives a byte stream produced by the first program. The source and the descriptor setup are in [pipeline.c](../lab7/pipeline.c). [redirect.c](../lab7/redirect.c) shows the related file case, and [run.c](../lab7/run.c) demonstrates fork, exec and waitpid.

~~~mermaid
flowchart LR
    L["ls child, descriptor 1"] --> W["pipe write end"]
    W --> R["pipe read end"] --> C["wc child, descriptor 0"]
    P["parent"] -. closes its copies .-> W
~~~

A pipe is a kernel-managed, bounded byte stream. It has no message boundaries: if a writer makes two writes, a reader is not promised two matching reads. If the buffer is empty while a write end is still open, a read waits for data. If the buffer is full, a write can wait for the reader to make space. This blocking allows a producer and consumer to run at different speeds without spinning. It also means the parent should not wait for the producer before it starts the consumer when the producer might fill the buffer. The shell starts both pipeline stages before collecting their completion.

End-of-file on a pipe is not a special byte sent by the writer. The reader sees EOF after the pipe's buffered bytes are consumed and every open reference to the write end has been closed. Each fork duplicates the process's descriptor references, so unused ends must be closed in the parent and children. If the parent accidentally retains p[1], wc cannot know that no more bytes will arrive, even after ls exits. Wc waits for more input, and the parent may wait for wc. This is a resource-lifetime error that looks like a hang. Lab 7's intentionally broken pipeline demonstrates it; [Lab 7's README](../lab7/README.md) contains the safe run procedure and bounded cleanup.

Lab 8's ping-pong pattern makes direction explicit. One anonymous pipe carries a byte from parent to child; a second carries a byte back. In the required [user/pingpong.c](../lab8/user/pingpong.c), the child closes its inherited copy of the request pipe's write end and the reply pipe's read end. It reads one byte, prints that it received ping, writes the byte on the reply pipe, closes both used descriptors and exits. The parent closes the opposite unused ends, writes one initialized byte, reads the reply and waits for the child. Each process retains only the endpoints it needs. With one shared pipe, the two readers would compete for the same byte stream, so a process could consume its own message. The two-pipe arrangement gives the request and response independent paths.

The same ideas meet in xv6. The shell's PIPE case in user/sh.c creates endpoints, forks the stages, duplicates the needed endpoint onto descriptor 0 or 1, and closes extras. The kernel dispatches pipe, read and write system calls into file and pipe operations; kernel/pipe.c stores bytes and sleeps or wakes processes when buffer space or data becomes available. In xv6's current source the pipe buffer is 512 bytes, shown by PIPESIZE. That is an implementation detail, not a universal pipe capacity. The source exposes the mechanism directly: [kernel/pipe.c](../lab2/kernel/pipe.c), [kernel/sysfile.c](../lab2/kernel/sysfile.c), [kernel/syscall.c](../lab2/kernel/syscall.c), and [user/sh.c](../lab2/user/sh.c).

## Connect the ideas to the published sessions

The first session introduces OS abstractions and protected access to hardware; the second treats the shell as a program that interprets commands and prepares arguments and descriptors; the third studies names and metadata in a filesystem. The fourth published session, [Processes, Descriptors, Pipes](https://else.fcim.utm.md/mod/resource/view.php?id=72236), joins process creation and completion to inherited and connected streams.

Follow ls /etc | wc -l from text to bytes to connect all four. The shell parses two commands and prepares a pipe. The kernel creates and schedules the processes, resolves /etc, and moves output bytes between descriptors. The producer can block on a full pipe and the consumer on an empty one; EOF arrives only after every write reference closes. The parent collects status with waitpid. These general mechanisms appear in both Bash/Linux and xv6, while shell syntax, pipe capacity, filesystem limits and memory implementation vary. For example, xv6's name limit does not apply to Linux, and xv6 does not expand wildcards like Bash.

## A speaking route

Start with how a line of text becomes a result. Trace sleep 3 through argv and the xv6 system-call boundary, then distinguish timer wakeup from a scheduler decision. Show that redirection changes descriptor 1, not echo. Use ls | wc -l to explain byte flow and EOF, then contrast a path, inode and open reference. Mark which details are general and which come from the lab implementations.

## Oral prompts

1. Why can a normal process not directly change another process's memory or control a disk device?
2. Distinguish program, process, fork and exec. What does successful exec preserve?
3. Are shell, ls and wc concurrent on one CPU, and what changes on a multi-core machine?
4. Trace sleep 3 from argv to the kernel. Which event makes the process runnable?
5. Why do quotes and wildcard characters change before argv is passed? Does the kernel perform Bash expansion?
6. Why can an unchanged program write to a file after the shell redirects descriptor 1?
7. Compare a hard link, symbolic link, inode and open descriptor. What does stat report?
8. Why can an open file remain usable after unlink removes its final name? Which xv6 counts matter?
9. Why does a pipe not promise one read per write, and when does a reader see EOF?
10. The producer exits but wc waits forever. Name a descriptor mistake that explains this.
11. How does a zombie differ from an orphan, and what does waitpid collect?
12. Why does ping-pong use two pipes? Which details of the examples are xv6-specific?

## Checking answers

1. The kernel mediates privileged memory and device operations through validated system calls.
2. A program is stored instructions; a process is a running instance. fork creates a child process. Successful exec replaces its program image but keeps its process identity and PID; it returns only on failure.
3. On one core the scheduler interleaves processes, so they are concurrent. Multiple cores can also execute some instructions in parallel.
4. user/sleep.c converts argv[1] to a number and requests sleep. The kernel blocks on timer ticks; a timer wakeup makes it runnable, and the scheduler later runs it.
5. The shell parses and expands its language before starting the program. argv contains the resulting strings; the kernel does not perform Bash glob expansion.
6. Closing 1 makes it the lowest free descriptor. open assigns 1 to the file, so the unchanged program's stdout now reaches that file.
7. A hard link is another directory name for the same inode. A symlink stores a pathname. An open descriptor refers to open-file state. stat returns metadata such as type, size and link count.
8. unlink removes a directory entry, but the descriptor retains an open reference. xv6 distinguishes nlink, the remaining names, from ref, live in-memory references; both must allow reclamation.
9. A pipe is an unstructured byte stream, not a message queue. EOF follows after buffered bytes are read and all write references are closed.
10. If the parent or another child leaves a duplicate write end open, the kernel cannot report EOF, so wc keeps waiting.
11. A zombie has exited but awaits collection; an orphan is still running after its parent exits and is adopted. waitpid returns the child's status and releases its remaining record.
12. Two pipes provide the two directions of ping-pong. xv6-specific details include its parser, PIPESIZE of 512 and filesystem limits; Bash and Linux have their own implementation details.

## Source scope

The examples refer to current local lab sources and the four published session titles. Reports contain recorded observations; this guide gives source-based explanations and symbolic traces, not new measurements or confirmed future exam scope.

## Catching up on the commands from Labs 1 through 6

Learn each command through its input, operation and output. For a compound command, identify which parts are interpreted by the shell before the program starts. The examples in this section are worked explanations, not new measurements. The main command sources are [Lab 1](../lab1/report.md), [Lab 3](../lab3/notes.md), [Lab 4](../lab4/notes.md), [Lab 5](../lab5/report.md) and [Lab 6](../lab6/README.md).

### Reading a command and finding your place

In `ls -l /etc`, `ls` is the program, `-l` is an option asking for a long listing, and `/etc` is the path being listed. Options change behavior; operands identify the objects to work on. A program receives these words as arguments. Shell operators such as `|` and `>` have a different role: the shell uses them to connect commands and streams.

Every process has a current working directory. A path beginning with `/` is absolute and starts at the filesystem root. A relative path starts at the current directory. `.` means the current directory; `..` means its parent. In Bash, `~` expands to the user's home directory. `/` and the administrator's home `/root` are different directories.

| Command | Explain it aloud |
| --- | --- |
| `pwd` | Print the current working directory. It changes nothing. |
| `cd /etc` | Change this shell's current directory to `/etc`. |
| `cd ..` | Move to the parent of the current directory. |
| `ls` | List the current directory's non-hidden entries. |
| `ls -la /etc` | List `/etc` with details and entries beginning with a dot. |
| `ls -ld /etc` | Show the directory `/etc` itself, rather than listing its contents. |
| `ls -li notes.txt` | Show a detailed listing and the inode number. |
| `ls -t` | Sort entries by modification time, newest first by default. |
| `mkdir demo` | Create a directory named `demo` in the current directory. |
| `touch note.txt` | Create an empty file if absent; otherwise update its timestamps. |
| `cat note.txt` | Read the file and copy its bytes to standard output. |
| `cp a b` | Copy file `a` to `b`. The destination can be overwritten. |
| `mv a b` | Move or rename `a` to `b`. |
| `rm note.txt` | Remove that directory entry. Other hard links or open references can keep its data alive. |

After `mkdir demo`, the shell is still in its previous directory. Only `cd demo` changes where relative paths start. In `echo hello > note.txt`, the shell opens or truncates the file and connects stdout to it; `echo` writes `hello` and a newline through that connection. The resulting file has six bytes for this ASCII example.

### Understanding output, filters and pipelines

| Command | Operation and distinction |
| --- | --- |
| `head -n 3 access.log` | Print the first three lines. |
| `tail -n 3 access.log` | Print the last three lines. |
| `wc -l access.log` | Count newline characters and display the count with the filename. |
| `wc -l < access.log` | The shell supplies the file as stdin; wc normally displays only the count. |
| `grep FAIL access.log` | Print lines matching the pattern `FAIL`. |
| `grep -c FAIL access.log` | Count matching lines, not occurrences within each line. |
| `cut -d' ' -f5 access.log` | Split on the literal space delimiter and select field five. Repeated spaces can create empty fields. |
| `cut -d: -f7 /etc/passwd` | Select the seventh colon-separated field, the configured login shell. |
| `sort` | Order input lines lexically using the current locale. |
| `sort -n` | Compare numeric values rather than ordinary lexical order. |
| `sort -rn` | Sort numerically in reverse order, largest first. |
| `sort -u` | Sort and remove duplicate lines. |
| `uniq -c` | Count consecutive equal lines. Sort first when all copies must be grouped. |
| `tr ':' '\n'` | Translate colons into newline characters. |

The actual Lab 3 pipeline is:

```sh
grep FAIL access.log | cut -d' ' -f3 | sort | uniq -c | sort -rn | head -n 2
```

Read it left to right. Keep failed requests; select their user field; group equal users; count each group; order the counts largest first; retain the first two. The result is the two users with the most failed requests in this log. Each pipe connects the preceding command's stdout to the following command's stdin. Stderr is separate unless redirected. The pipeline does not normally change `access.log`.

For a symbolic example, suppose the selected users are `ann`, `bob`, `ann`. Sorting gives `ann`, `ann`, `bob`. `uniq -c` produces a count of 2 for ann and 1 for bob. If `uniq -c` had been run before sorting, the two separated ann entries would be counted as separate groups. This is why the order of the stages matters.

### Shell symbols, quoting and exit status

| Syntax | Meaning |
| --- | --- |
| `command > file` | Create or truncate a file and send stdout to it. |
| `command >> file` | Append stdout to the file. |
| `command < file` | Read stdin from the file. |
| `command 2> errors` | Send stderr, descriptor 2, to the file. |
| `command > all.txt 2>&1` | Send stdout to the file, then make stderr use stdout's current destination. |
| `a ; b` | Run a, then b regardless of a's success. |
| `a && b` | Run b only if a returns status zero. |
| `a || b` | Run b only if a returns a nonzero status. |
| `sleep 30 &` | Start the command asynchronously so the shell can accept another command. |
| `echo $?` | Print the exit status of the preceding command. |
| `echo $!` | Print the PID of the most recent background pipeline's final process. |
| `echo $$` | Print the shell's PID. |
| `$(command)` | Substitute the command's stdout, with trailing newlines removed. |
| `echo $PATH` | Expand the PATH variable, whose colon-separated directories control command lookup. |
| `type cd` | Ask the shell how it interprets the name: builtin, alias, function or executable. |

Redirections apply left to right. `> all.txt 2>&1` sends both streams into the file. `2>&1 > all.txt` first connects stderr to the original stdout destination, then changes stdout to the file. With a terminal as the original stdout, stderr stays on the terminal.

In Bash, `echo '$HOME'` prints the literal text `$HOME`; `echo "$HOME"` expands the variable but keeps its value in one argument. `echo *.c` receives filenames expanded by the shell; `echo '*.c'` receives the literal pattern. `*` matches any sequence of characters, `?` matches one character, and `[ab]*` selects names beginning with a or b. These glob patterns differ from grep's regular expressions. The shell's globbing and grep's pattern matching happen at different stages.

### Processes, memory and storage

| Command | What it inspects or changes |
| --- | --- |
| `ps aux` | A snapshot of processes, including owners, PIDs, CPU and memory information. |
| `top` | A repeatedly updated process and resource view. |
| `sleep 30` | On Linux, wait for roughly 30 seconds; in this course's xv6 program the argument is ticks. |
| `kill PID` | Send SIGTERM by default, requesting termination. It is a signal operation. |
| `kill -9 PID` | Send SIGKILL, which the target cannot catch to perform cleanup. |
| `jobs` | Show jobs managed by this interactive shell, rather than all system processes. |
| `fg` | Bring a shell job to the foreground. |
| `wait PID` | In a shell, wait for an appropriate child process and collect its status. |
| `cat /proc/PID/status` | Read kernel-provided information for that process; replace PID with its number. |
| `free -h` | Show memory accounting in readable units. Available memory includes reclaimable capacity. |
| `lsblk` | Show block devices and their relationships, such as disks and partitions. |
| `df -h` | Show filesystem capacity and free/used space in readable units. |
| `df -i` | Show inode usage and availability. |
| `du -sh directory` | Summarize the directory's allocated disk usage, subject to access and filesystem behavior. |
| `mount` | With no operands, show mounted filesystems. |
| `file path` | Inspect content/type information, rather than trusting the filename extension. |
| `xxd path` | Show file bytes in hexadecimal alongside a character representation. |

`ps aux | wc -l` counts the printed header too; it is not an exact process count without accounting for that line and snapshot timing. `lsblk`, `df` and `du` answer different questions: what devices exist, how much space a filesystem has, and how much space selected files occupy. A sparse file created with `truncate -s 1G big.img` can have a one-gigabyte logical size but little allocated storage. `ls -lh` and `du -h` therefore need not agree.

`/proc` is a kernel-provided virtual filesystem. Reading `/proc/meminfo` obtains memory information; it is not reading an ordinary saved text report. `/proc/self` refers to the process accessing it. Thus `head /proc/self/status` describes head, whereas `/proc/$$/status` uses the shell PID expanded by Bash.

### Permissions, links and filesystem commands

`-rw-r--r--` begins with a file-type character, then three permission groups: owner, group and others. In each group, r contributes 4, w contributes 2 and x contributes 1. Therefore 600 means owner read/write and no group/other access; 644 adds read access for group and others; 755 gives the owner all three permissions and the others read/execute.

| Command | Explain the effect |
| --- | --- |
| `chmod 600 s.txt` | Set owner read/write; remove group and other permissions. |
| `chmod u+r s.txt` | Add owner read permission without replacing every permission bit. |
| `chmod +x report.sh` | Add execute permission according to the applicable chmod/umask rules. |
| `umask 022` | Set a mask removing group and other write permission from requested creation modes. |
| `stat notes.txt` | Show metadata such as inode, size, link count and permissions. |
| `ln notes.txt hard.txt` | Add another hard-link name for the same inode. |
| `ln -s hard.txt soft.txt` | Create a symbolic link containing the target path `hard.txt`. |
| `find . -name '*.txt'` | GNU/Linux find searches below the current directory; quoting protects its pattern from early shell expansion. |
| `exec 3< bigfile` | In Bash, open the file on descriptor 3 in the current shell. With no program argument, this does not replace the shell. |
| `exec 3<&-` | Close that shell descriptor. |

For ordinary creation modes, a 022 mask turns requested file mode 666 into 644 and directory mode 777 into 755 by clearing bits. It does not simply subtract numbers in every possible case. On a directory, r permits listing names, x permits searching/traversing known names, and w together with the necessary search permission permits changes to directory entries. Reading a file's contents is governed by that file's permissions and the ability to traverse its path. Removing a name generally depends on permissions on its parent directory, with rules such as the sticky bit also relevant.

Hard links share an inode and its data. A symbolic link has its own inode and stores a pathname. Removing one hard-link name leaves the other usable; removing the symlink's target can leave a dangling symlink. The same name/inode distinction explains why an open descriptor can still read an unlinked file until the last relevant open reference closes.

### xv6 and the commands used to build it

| Command | Environment and purpose |
| --- | --- |
| `make qemu` | Run on the Linux host: build the needed xv6 artifacts and start QEMU. |
| `make clean` | Run on the host: remove the Makefile's generated build products. |
| `args one two` | In the course xv6 image, show argc and argv; argv[0] names the program too. |
| `mystat README . console` | Lab 6 utility: print type, inode, links and size for each path. |
| `find . r2` | Lab 6 utility: recursively find entries whose basename is r2. |
| `find . r2 -n` | Its optional mode also displays inode numbers. |
| `../ls ../README` | Explicitly locate the ls executable in the parent directory, then inspect the specified file. |

The course xv6 find command is a custom program with a different interface from GNU/Linux find. Its shell also lacks Bash quoting, wildcard expansion, variables and PATH search. It supports commands, redirection, pipes, sequential lists and background execution. At its prompt, `cd d` is handled in the shell process. In the supplied shell, putting cd inside a semicolon list is not equivalent to Bash's handling of cd in a list.

For `args *.c "x y"`, Bash expands the wildcard and keeps x y as one argument. This xv6 shell leaves `*.c` literal and splits the quoted text into two tokens containing quote characters. The shell determines those argument strings before exec loads the program. Read the exact examples in Lab 4 before transferring Bash syntax into xv6.

### Command practice prompts

1. Starting in `/home/student/os`, what does `pwd` print after `cd ..`? Why?
2. Explain the difference between `ls -l /etc` and `ls -ld /etc`.
3. Trace the six stages of the Lab 3 failed-request pipeline. Why is sort before uniq?
4. Explain why `wc -l < access.log` does not normally print the filename.
5. Compare `>` with `>>`, then explain why reversing `2>&1` and `> file` changes the result.
6. Who expands the star in `echo *.c`? What changes when it is quoted?
7. Interpret mode 640. Which permissions are needed to read a known file inside a directory?
8. Why can ls show a one-gigabyte file while du reports almost no allocated space?
9. Explain the different questions answered by ps, free, lsblk, df and du.
10. After `ln a b; rm a`, can b remain readable? What changes if b was a symbolic link to a?
11. Compare Linux `sleep 20` with the course's xv6 `sleep 20`.
12. Explain why Bash's find options and quoting cannot simply be copied into the Lab 6 xv6 find command.

### Command practice checking answers

1. `/home/student`: cd changes the shell's working directory to its parent; pwd prints that state.
2. The former lists contents with details; -d makes the latter describe /etc itself.
3. Select failures, select user field, sort users, count consecutive equal users, sort counts numerically descending, retain two lines. Sorting groups equal users for uniq.
4. The shell opens the file; wc gets stdin and no filename operand to display.
5. Overwrite/truncate versus append. Redirections are performed left to right, and descriptor duplication copies the destination at that moment.
6. Bash expands it. Quotes preserve the literal star; this xv6 shell does not implement that Bash expansion.
7. Owner read/write, group read, others none. Reading a known file also needs search permission on each directory in its path.
8. Logical size and allocated storage differ for sparse files.
9. Processes, memory, devices, filesystem capacity, and selected file allocation respectively.
10. A hard link still names the same inode. A symlink storing path a dangles after a is removed.
11. Linux uses seconds; this course's xv6 program passes a tick count to the kernel.
12. The custom program expects a starting path, basename and optional -n; the xv6 parser lacks Bash quote removal and glob expansion.
