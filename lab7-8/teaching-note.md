# Presenting Labs 7 and 8

Use the presentation beside these notes. The diagrams show mechanisms, not measured PIDs. The optional programs are labelled in the lab reports. Read the two lab teaching notes for the full source walkthrough and answer keys.

## Speaking script

### Slide 1: Processes, descriptors and pipes

Today I will connect the shell commands from earlier labs to the operating-system mechanisms that make them work. Lab 7 uses Linux. Lab 8 repeats the process calls inside xv6 and adds communication through two pipes. I will explain the state changes before showing the output.

### Slide 2: A program asks; the kernel acts

A program is stored instructions. A process is a running instance with registers, memory and open files. Normal user code cannot manage hardware directly. A system call crosses a controlled boundary into the kernel, which validates the request and performs the operation. A library function is not necessarily a system call: printf formats text in user space and eventually writes bytes.

### Slide 3: fork: one call, two return paths

Before fork there is one process. After a successful fork there are two. The parent receives the child PID; the child receives zero, so both can choose different branches. A negative return means creation failed. There is no general promise that the child runs first. In run.c the parent waits, which guarantees the completion message comes after the child finishes.

### Slide 4: Copied memory, shared open objects

Each process has its own virtual address space. If the child changes a normal variable, the parent does not see that change. The descriptor table is copied too, but its entries refer to underlying kernel objects. A pipe created before fork therefore connects the two processes. Separate address spaces and shared pipe references explain why a pipe is needed for communication.

### Slide 5: exec changes the program, not the PID

The child calls execlp to run ls. This replaces the child program image. It does not create another process and it does not return on success. That is why perror after execlp appears only when execution fails. Linux execlp searches PATH; xv6 exec in this lab uses the executable name directly. The missing-program statuses 127 and 1 come from explicit exit calls in our source, not a universal rule of exec.

### Slide 6: An exited child still needs collecting

A zombie has already exited. The kernel retains a small exit record until the parent collects it with wait or waitpid. Delaying the parent by twenty seconds makes this state visible. Waiting then reaps it. A zombie is not a running program and is different from an orphan, whose parent has exited.

### Slide 7: Redirection changes a descriptor

A descriptor is a small per-process integer, not the file itself. The standard conventions are zero for input, one for output and two for errors. Closing one frees that slot. Open chooses the lowest free descriptor, so the file becomes standard output. After exec, ls uses descriptor one as usual. No change to ls is needed. The parent is unaffected because the child changed its own descriptor table.

### Slide 8: A pipeline is wiring plus processes

The pipe is created before either fork, so both children inherit references to it. The producer duplicates the write end onto standard output; the consumer duplicates the read end onto standard input. Then they close unused originals and the parent closes both ends. wc counts newline bytes in the stream. It does not count directory inodes directly, and it does not need to know who produced the data.

### Slide 9: Why the broken pipeline hangs

Finishing ls is not enough. A reader receives EOF only when the pipe buffer is empty and every write-end reference is closed. If the parent keeps its write end, the empty pipe still has a possible writer. wc blocks waiting for more bytes while the parent waits for wc. Closing the parent write end removes the cause of the wait. EOF is a condition reported as read returning zero, not a special character sent through the pipe.

### Slide 10: Lab 7: the observed behavior

These are the recorded results from the focused Ubuntu WSL run on nineteen October. The normal ls and date children exited with zero; the missing-program branch exited with 127. The zombie was visible as Z plus before waiting. Redirection allocated descriptor one. The two-stage and three-stage pipelines matched their corresponding shell counts. These directory counts are specific to this environment and can change; the equality under the same inputs is the relevant comparison.

### Slide 11: The same interface inside xv6

In xv6 we can follow the boundary in source. The generated user stub puts a system-call number in a7 and executes ecall. The trap handler enters kernel mode and the dispatcher selects the handler. Fork and wait use proc.c, exec loads a replacement image, and pipe.c implements the buffer and blocking. QEMU emulates the machine; xv6 is the guest operating system, while WSL Linux hosts the compiler and QEMU.

### Slide 12: pingpong: one pipe in each direction

The parent sends one byte through p2c. The child reads it, prints received ping and returns the byte through c2p. The parent read on c2p blocks until the reply is available, then it prints received pong. Wait happens after the pong message, so wait is not what enforces that message order. Two directional pipes avoid both processes competing to read the same stream.

### Slide 13: Each process owns only what it needs

The diagram abbreviates parent_to_child as p2c and child_to_parent as c2p. Fork copies all four descriptors into both processes. The parent keeps the request writer and reply reader. The child keeps the request reader and reply writer. Each closes the other pair immediately, and closes its used ends after the transfer. Close removes one process reference; it does not erase the endpoint from every process.

### Slide 14: An optional chain of prime filters

The first process receives the integers two through thirty-five. Each stage reads its first remaining number as its prime, prints it, creates a child stage and forwards only numbers not divisible by that prime. Earlier stages have already removed smaller prime factors, so the next surviving first number is prime. Closing unused ends is essential for EOF propagation and to avoid running out of descriptors.

### Slide 15: Lab 8: the observed behavior

This output was recorded after building a clean disposable xv6 overlay and booting it in QEMU. Run used parent three and child four and the echo child exited with zero. Pingpong printed the child ping before the parent pong. The optional program printed all eleven primes from two through thirty-five. The ls replacement exited with zero, while the missing-program branch printed exec failed and exited with one. The PIDs are observations from that boot, not values that future runs must match.

### Slide 16: Earlier labs: names become file data

The filesystem connects earlier exercises to descriptors. A path is resolved through directories; a directory entry names an inode. The inode contains metadata and data-block addresses. A hard link adds another name for the same inode. A symbolic link stores a path and has its own inode. Removing a name does not necessarily remove data immediately: link count and open references determine when storage can be reclaimed.

### Slide 17: Demonstrate the required behavior

For Lab 7 I will run the normal launch, show the saved zombie observation, inspect out.txt, and compare the manual pipeline with the shell pipeline. For Lab 8 I will boot the prepared overlay, run run, pingpong and primes, then show the measured ls and missing-program variants in notes.md. I will explain why each line follows from the mechanism. The optional programs extend the examples but do not change the required rubric.

### Slide 18: Explain a changed condition

I will answer by tracing ownership and execution, not by memorizing output. If exec fails, old code continues to the error branch. If the parent keeps a write descriptor, EOF is delayed. If the pipe is created after fork independently in each branch, they are different pipe objects. If the child never replies, the parent read waits while a writer exists. If every writer closes without replying, read returns zero and the error check catches the missing byte.

## Live demonstration

Open a WSL terminal and follow the exact commands in [Lab 7](../lab7/README.md) and [Lab 8](../lab8/README.md). Keep both reports open as a fallback for the 20-second zombie and temporary program variants. Use the saved measured output honestly if a live command is interrupted. PIDs and directory counts may differ between runs.

## Rehearse before looking at the answers

1. Draw fork and exec, including the return values and the unchanged PID across exec.
2. Draw all pipe descriptors after fork. Cross out every end each process must close.
3. Explain why an empty pipe does not always mean EOF.
4. Point to the read that orders ping before pong. Explain why the later wait is different.
5. Explain the relationship between a name, inode, open file and descriptor.
6. Describe the host, emulator and guest in the xv6 demonstration.

## Checking answers

1. fork creates a child and returns child PID to parent, zero to child. Successful exec replaces only the child program image and retains its PID.
2. Producer keeps its duplicated stdout writer, consumer its duplicated stdin reader. The parent keeps neither endpoint. Original descriptors are closed after dup.
3. An empty pipe with a writer still open can receive more data, so blocking read waits. Empty with no writers gives read == 0.
4. Parent read(c2p[0], ...) must obtain the reply before the pong print. wait later collects the exited child.
5. A directory entry maps a name to an inode. An open-file object describes an open instance, and a per-process descriptor refers to it. Several descriptors can share one object.
6. WSL Linux is the build host. QEMU emulates the RISC-V machine. xv6 runs as its guest OS.

## A useful final explanation

The shell composes ordinary programs by creating processes and arranging descriptors before exec. Pipes provide byte streams and blocking coordination; wait collects child completion. The same small interface is visible in Linux and traceable inside xv6.
