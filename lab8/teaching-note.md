# Teaching note: process calls and pipes in xv6

The lab asks you to recognize familiar operating-system ideas inside a small kernel you can read. First, a child changes from one program to another while its parent waits. Then the parent and child exchange bytes through file descriptors. The same call names do not guarantee identical APIs: xv6 is a compact teaching system, and its implementation makes the process and pipe rules visible.

## 1. `fork`, `exec` and `wait`

In `user/run.c`, the parent prints its process ID and calls `fork`. The return value separates the two paths. A negative value means the kernel could not create a process. A zero value is returned in the child. A positive value is returned in the parent and is the child's PID.

The child prints its own PID, constructs the argument vector, and calls `exec("echo", args)`. The vector is a sequence of string pointers terminated by a null pointer. Here it contains the program name and four words: `echo`, `hello`, `from`, `the`, and `child`. xv6 `exec` replaces the current process's user program with the new one. The process keeps its PID, but its program code and address space change. The parent still runs the original `run` code.

On success, `exec` does not return. The line that prints `exec failed` is reached only when the target cannot be loaded. The child then exits with status 1. This is why the error path follows the `exec` call immediately: if the call returns, replacement failed.

The parent calls `wait(&child_status)`. In this xv6 source tree, [kernel/proc.c](../lab2/kernel/proc.c) stores the integer supplied to `exit(status)` in the child's process record. `wait` finds a zombie child, copies that value to the address supplied by the parent, releases the process slot and returns the child PID. The parent can then print both values. On the successful echo path, the `echo` program exits with 0.

Follow the user-visible system-call wrappers in [user/user.h](../lab2/user/user.h), the generated stubs in [user/usys.pl](../lab2/user/usys.pl), and dispatch in [kernel/syscall.c](../lab2/kernel/syscall.c). The child reaches `exec` through the xv6 system-call interface; on success, `exec` constructs the new user image before returning to user mode. The system call changes which program runs in the child, not which process the parent is waiting for.

### Compare the Linux spellings carefully

The conceptual sequence also appears in Unix-like Linux programs, but this lab's calls are not literal API equivalents in every detail. xv6 offers `exec(path, argv)` and one `wait(int *)` operation. Linux programs often use `execlp`, which searches `PATH`, and `waitpid`, which can select a child. Linux wait status is encoded and should be decoded with macros such as `WEXITSTATUS`. This xv6 tree copies the integer exit status directly to the supplied address. A child's explicit `exit(1)` therefore explains xv6's status 1 without any shell convention.

Lab 7 makes the contrast concrete: its Linux [run.c](../lab7/run.c) calls `exit(127)` after a failed `execlp`, while this xv6 program calls `exit(1)` after a failed `exec`. In both labs, the child program chooses its own status after the call returns with an error. `exec` itself does not choose 1 or 127. The value 127 is also commonly used by shells when a command cannot be found, but that convention does not change what xv6 `exec` returns. If you remove the explicit exit and fall through, the source would no longer express the intended failure result.

## 2. Trace the argument vector

The declared array in `run.c` has five string entries plus a null terminator. The array itself is local to the child branch, but the kernel copies the strings and pointers into the new process image during `exec`. The `echo` user program reads the resulting `argc` and `argv`, skips `argv[0]`, and writes the remaining words with spaces and a newline. See [user/echo.c](../lab2/user/echo.c).

Thus the parent does not print `hello from the child`; the `echo` image does. The parent receives no text through `wait`. It receives the child's PID and exit status. Text reaches the terminal because both processes inherit the console descriptors across `fork` and the `echo` program writes to descriptor 1.

The two requested variants change only the target and vector:

```c
char *args[] = {"ls", 0};
exec("ls", args);
```

```c
char *args[] = {"nosuchprog", 0};
exec("nosuchprog", args);
```

The successful `ls` run demonstrates that the child can execute a different program. The missing name exercises the failure path. Make these edits in the disposable overlay, leaving the submitted echo example intact.

## 3. Descriptors and ping-pong

A file descriptor is a small integer that selects an open file-like object in one process. `pipe(fd)` fills two array entries: `fd[0]` is the read end and `fd[1]` is the write end. In xv6, the pipe is one-way. A process can write bytes at one end and another process can read those bytes at the other.

`user/pingpong.c` creates both pipes before `fork`, so both processes inherit descriptors for both directions. After the fork, each process closes the copies it does not need:

| Direction | Writer | Reader |
| --- | --- | --- |
| Ping | Parent `parent_to_child[1]` | Child `parent_to_child[0]` |
| Pong | Child `child_to_parent[1]` | Parent `child_to_parent[0]` |

The parent writes one initialized byte, closes that write end and reads a byte back. The child blocks in its first `read` until the parent sends the ping. It prints the ping message, writes the same byte on the reply pipe and closes its remaining endpoints. The parent then prints the pong message and calls `wait` to collect the child.

The call that waits for the pong is the parent's `read` from `child_to_parent[0]`. A pipe read blocks while no byte is available and a writer remains open. `wait` is later: it waits for process termination after the reply exchange. The code closes unused pipe ends so that a process cannot accidentally keep a direction open through an inherited descriptor. The xv6 pipe read/write and close behavior is implemented in [kernel/pipe.c](../lab2/kernel/pipe.c) and reached through [kernel/sysfile.c](../lab2/kernel/sysfile.c).

Two pipes make the two directions independent. If both processes read and write the same pipe, a process may read its own byte before the other process does. The separate channels make the intended protocol visible: ping travels parent to child, pong travels child to parent.

## 4. Optional prime filters

`user/primes.c` sends the integers 2 through 35 from a producer into the first filter. Each filter reads its first remaining value and prints it as a prime. It then creates a pipe and forks the next filter. The current process forwards only values that are not divisible by its prime. For example, the first filter keeps 3, 5, 7, and the other odd candidates; the filter for 3 removes 9, 15, 21, 27 and 33; the filter for 5 removes 25 and 35.

The data flow is a chain. Each stage reads one pipe, removes multiples of one prime, and writes the survivors to the next pipe. When a stage has read all input, it closes its writer. That close lets the next stage's `read` return zero at end of file. Each stage waits for the child it created, so the pipeline is reaped from the end back toward the producer.

This optional program is useful for reviewing the same descriptor rules at more than two processes. It does not change the required ping-pong solution or the required `run` source.

## Report route and ten-minute reading practice

Use this note to explain the source and captured behavior, then use the formal report for the evidence. Part 1, pages 5-6, traces fork, exec, wait and the user-to-kernel system-call path. The `exec` variants are on pages 8-9. Part 2, pages 10-11, explains the two pipes; QEMU observations are on pages 12-13; the optional primes extension is on page 14; references are on page 16; source excerpts follow on pages 17-23. The [recorded execution session](../lab78/execution-session-2026-10-19.txt) preserves the actual build, boot and command output. The official handout link is in [Source links](#source-links); its contents were not available in this local working copy, so this practice is grounded in the saved source, notes and report.

For ten minutes, spend two minutes drawing the parent and child paths after fork. Spend two minutes tracing `user/run.c` through exec and wait; state what changes and what stays the same. Spend two minutes following the xv6 syscall stub through `ecall`, trap handling and dispatch. Spend two minutes drawing both pingpong pipes and naming every unused endpoint each process closes. Use the final two minutes to distinguish a pipe read waiting for bytes from wait waiting for process exit, then answer one changed-condition prompt.

## Oral practice prompts

Try to reconstruct each answer aloud before reading the checking section. The first fifteen are likely questions about the required examples. The last five ask what changes when ownership, ordering or input bounds change.

### Fifteen likely prompts

1. In xv6 run.c, what does fork return in the child and the parent?

2. After the child successfully execs echo, is it a new process with a new PID?

3. Why does the line after exec print an error only when exec fails?

4. What is argv in the run example, and why must its last pointer be null?

5. Which process prints the echo words, and what does the parent get from wait?

6. Why is failed exec status 1 in xv6 while the Linux Lab 7 example uses 127?

7. What does wait do for the parent in this xv6 tree?

8. Trace one xv6 system call from a user program toward the kernel dispatcher.

9. The recording shows parent PID 3 and child PID 4. Should the next run show the same numbers?

10. Which end of an xv6 pipe is read, and which is written?

11. Why does pingpong create two pipes instead of using one for both directions?

12. Trace the one-byte ping-pong order. What happens before the parent calls wait?

13. Name three different calls that may block in this exercise and what each waits for.

14. Why must each pingpong process close pipe descriptors it will not use?

15. Why should the source check fork, pipe, read and write return values?


### Five harder, changed-condition prompts

16. In xv6 pipe.c, when does a read return zero rather than wait?

17. The optional primes program feeds 2 through 35. Why does its output end at 31, and what would 2 through 50 add?

18. If both pingpong directions shared one pipe, what race appears?

19. Could the parent call wait immediately after sending ping and then read pong safely?

20. Suppose the receive pipe is empty after the child writes, but another process retains its writer. What does the parent read observe?


## Checking answers

Each answer gives the rule, why it follows, a changed condition to test, and where to trace it in source and report.


1. **Answer:** The child gets 0. The parent gets the child's positive PID. A negative return indicates failure to create the child. **Why:** The same fork call creates two continuations whose return values select their branches. **If changed:** On failure, the parent must handle the negative value instead of waiting for a child that does not exist. **Trace:** `user/run.c:12-18`; report Part 1, pp. 5-6.


2. **Answer:** No. exec replaces the program image inside the existing child process, so the PID remains the same. **Why:** fork creates a process; exec changes what that process runs. **If changed:** If the child forked again instead of execing, there would be another process and another PID. **Trace:** `user/run.c:18-24`; report Part 1, pp. 5-6.


3. **Answer:** A successful exec does not return to the old image. A failed exec returns, so the child prints the error and explicitly exits with status 1. **Why:** The failure path follows the call because normal success replaces that path entirely. **If changed:** Changing the target to a valid program bypasses the error and exit(1) lines. **Trace:** `user/run.c:18-24`; report Part 1, pp. 5-6; variants, pp. 8-9.


4. **Answer:** argv is an array of pointers to argument strings. xv6 exec expects a null-terminated vector so it can identify where the arguments end. **Why:** The program receives arguments as a sequence rather than as one shell command string. **If changed:** Changing one string changes what echo prints; omitting the null terminator makes the vector invalid. **Trace:** `user/run.c:19-20; user/echo.c:6-18`; report Part 1, pp. 5-6.


5. **Answer:** The child, now running echo, prints the words. The parent gets the terminated child's PID and exit status from wait; it does not receive the child's text through wait. **Why:** Output uses inherited console descriptors, while wait communicates process termination information. **If changed:** Redirecting the child's stdout would change where the words appear without changing the parent's wait result. **Trace:** `user/run.c:18-32; user/echo.c:6-18`; report Part 1, pp. 5-6.


6. **Answer:** Each child chooses an explicit exit value after exec returns with failure. Lab 8 calls exit(1); Lab 7 calls exit(127). exec does not choose either value. **Why:** The status is application policy layered on the failed system call. **If changed:** Changing the explicit exit argument changes the value wait later reports. **Trace:** `user/run.c:22-24; ../lab7/run.c:18-20`; report Part 1, pp. 5-6; variants, pp. 8-9.


7. **Answer:** It waits for a child to exit, returns that child's PID and copies its exit status to the supplied address; it also releases the zombie process slot. **Why:** The kernel separates child exit from the parent's collection of its status. **If changed:** If the child has not exited yet, wait blocks; if the parent has no waitable child, the return path differs. **Trace:** `user/run.c:27-32; ../lab2/kernel/proc.c:368-397`; report Part 1, pp. 5-6.


8. **Answer:** The program uses a declaration in user.h; usys.pl generates a stub that puts the syscall number in a7 and executes ecall; usertrap enters the syscall dispatcher, which selects a sys_* handler. **Why:** The wrapper gives ordinary user code a controlled path across the user/kernel privilege boundary. **If changed:** A different call uses a different syscall number and dispatcher entry, but the boundary pattern remains. **Trace:** `../lab2/user/user.h:6-14; usys.pl:9-21; kernel/trap.c:38-68; kernel/syscall.c:132-142`; report Part 1, pp. 5-6.


9. **Answer:** No. Those are measured values from one QEMU boot. Process IDs depend on the current xv6 process table and previous commands. **Why:** PID order is runtime state, while parent-child roles follow the fork return values. **If changed:** Running another command first may consume IDs and shift both values. **Trace:** `user/run.c:10-21`; report QEMU observations, pp. 12-13; execution session, 19 Oct 2026.


10. **Answer:** fd[0] is the read end and fd[1] is the write end. One process can write bytes and another can read them in order. **Why:** The two descriptors represent different sides of one kernel-managed byte stream. **If changed:** Swapping the roles without changing the calls makes a process read from the wrong endpoint or write to the wrong one. **Trace:** `user/pingpong.c:7-8; ../lab2/kernel/sysfile.c:478-497`; report Part 2, pp. 10-11.


11. **Answer:** One pipe carries parent-to-child ping and the other carries child-to-parent pong. Separate streams avoid a process consuming its own byte before the peer does. **Why:** A pipe is one-way; two independent directions need two independent channels for this protocol. **If changed:** A more complex single-pipe protocol would need extra coordination or message framing to prevent self-read and ordering races. **Trace:** `user/pingpong.c:7-24`; report Part 2, pp. 10-11.


12. **Answer:** The parent writes the ping byte and closes that writer. The child reads it, prints ping, writes the reply and closes its writer. The parent reads and prints pong, then waits for the child's exit. **Why:** The pipe read is the synchronization for the reply; wait is process-lifetime synchronization afterward. **If changed:** If the parent reads before sending the first byte, the child and parent can both wait for data and deadlock. **Trace:** `user/pingpong.c:31-74`; report Part 2, pp. 10-13.


13. **Answer:** The child's first read waits for ping; the parent's second read waits for pong; the parent's wait waits for child termination. These are distinct conditions. **Why:** Blocking describes waiting for an event, but the event can be pipe data or process exit. **If changed:** A read can return immediately if data is buffered; wait can return only after a child is waitable. **Trace:** `user/pingpong.c:34,62,70-74`; report Part 2, pp. 10-11.


14. **Answer:** Unused copies waste descriptors and can keep a writer open. A reader gets EOF only after buffered bytes drain and all write references are closed. **Why:** fork duplicates descriptor references, so both processes initially hold both directions. **If changed:** Leaving one inherited writer open can make a reader wait indefinitely after the intended writer exits. **Trace:** `user/pingpong.c:31-68; ../lab2/kernel/pipe.c:59-74,106-129`; report Part 2, pp. 10-11.


15. **Answer:** These calls can fail or transfer fewer bytes than requested. Checking the result prevents the program from treating a failed setup or incomplete transfer as success. **Why:** Operating-system calls report both success and failure through their return values. **If changed:** If a read returns 0 at EOF, retrying forever is also wrong; the program must interpret zero as no more data. **Trace:** `user/pingpong.c:7-29,34-74`; report Part 2, pp. 10-11.


16. **Answer:** When the pipe has no buffered bytes and no write endpoint remains open. While a writer remains, an empty read waits for data. **Why:** EOF means there can be no future bytes, not merely that the buffer is momentarily empty. **If changed:** If one inherited writer stays open, the empty reader can continue waiting instead of returning zero. **Trace:** `../lab2/kernel/pipe.c:106-129`; report Part 2, pp. 10-11.


17. **Answer:** 31 is the largest prime in the tested input range. Extending the producer through 50 would also send 37, 41, 43 and 47 through the filters. **Why:** The filter only reports values it receives; it cannot emit a prime that the producer never sends. **If changed:** Changing the upper bound changes the tested output, not the prime-filter rule. **Trace:** `user/primes.c:7-28,112-126`; report Optional primes, p. 14; execution session, 19 Oct 2026.


18. **Answer:** After the parent writes ping, its own read and the child's read would compete for the same bytes. The parent could consume its own ping, leaving the child blocked. **Why:** A pipe delivers bytes to whichever reader consumes them first; it has no sender/receiver identity. **If changed:** Separate pipes give each direction one clear reader and writer. **Trace:** `user/pingpong.c:7-24`; report Part 2, pp. 10-11.


19. **Answer:** For this one-byte reply, likely yes because it fits in the pipe buffer and the child can exit. For a larger reply, the child could fill the pipe and block writing while the parent blocks in wait, so neither progresses. **Why:** wait synchronizes on process exit, while reading frees pipe-buffer space; ordering can create a deadlock. **If changed:** If the parent reads concurrently or before waiting, a large response can drain and let the writer finish. **Trace:** `user/pingpong.c:55-74; ../lab2/kernel/pipe.c:77-102`; report Part 2, pp. 10-11.


20. **Answer:** It cannot see EOF yet. Once buffered data is consumed, the empty read waits because the retained writer means more data may still arrive. **Why:** The kernel counts open writer references, not the number of processes that intend to write. **If changed:** Closing the final writer lets the read return zero after existing bytes drain. **Trace:** `../lab2/kernel/pipe.c:59-74,106-129`; report Part 2, pp. 10-11.


## Source links

- [Lab 8 Moodle handout](https://else.fcim.utm.md/mod/resource/view.php?id=72240)
- [Lab 2 xv6 user and kernel sources](../lab2/README.md)
- [xv6 user `echo`](../lab2/user/echo.c)
- [xv6 process exit and wait](../lab2/kernel/proc.c)
- [xv6 shell pipe setup](../lab2/user/sh.c)

## Visual explanation route

Start with the [process-lifetime diagram](assets/concept-process-lifetime.png). Point to fork and explain why there are two PIDs. Point to exec and explain why the child keeps its PID. Point to the amber interval and explain why exit alone does not reap the child.

Then use the [pipe-ownership diagram](assets/concept-pipe-ownership.png). Ask what changes if the parent keeps one writer open. Predict the blocked reader before checking the captured result in the report. These are concept illustrations, not execution captures.
