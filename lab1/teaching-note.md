# Lab 1: how Linux manages a computer

This lab asks what the operating system does between a command and the resources that command uses. Linux gives you an outside view: you ask the shell to inspect a file, start a process, read memory information or inspect a device, and the kernel provides a controlled answer.

The kernel is the privileged part of the operating system. It decides how programs share the processor, RAM, files and devices. The shell is an ordinary program that reads commands and asks the kernel to start or connect other programs. When a program needs a protected service, it uses a system call. The terminal is where you see the shell's input and output.

## Follow one file from a command line

The handout's example creates a file with this command:

    echo "hello operating systems" > note.txt

The shell reads the whole line first. The greater-than symbol is shell syntax: before running echo, the shell opens note.txt for output and connects the command's standard output to that open file. Standard output is file descriptor 1, a small number the process uses to name an open stream. Echo writes its text to descriptor 1, so the text reaches the file rather than the terminal.

A file path is a name in a directory tree. The root path, /, is the top of that tree; ~ is the current user's home directory. pwd shows the current working directory, which tells the shell how to interpret a relative name such as note.txt. mkdir adds a directory, cp makes another file with copied contents, mv changes a name or location, and rm removes a name from the directory. These commands change different things: cp creates another file, while chmod changes permission metadata without changing the text inside the file.

For a regular file, ls -l prints a type marker followed by nine permission characters. The first three permissions belong to the owner, the next three to the group, and the last three to other users. The listing then names the owner and group. r allows reading, w allows writing, and x allows execution. For a directory, x means that a user may traverse it. The report recorded its files as owned by ubuntu and group ubuntu; those names can differ on another machine.

After chmod 600 note.txt, the permission part is -rw-------. The first - says this is a regular file. In the octal mode 600, the owner's 6 means read (4) plus write (2); each 0 gives the group and other users no permissions. By comparison, 644 is -rw-r--r--: the owner can read and write, while the group and others can read. If ls -l shows a leading d instead of -, the item is a directory and the x bits govern access to names inside it.

The shell can connect streams in another way. In ps aux | wc -l, the pipe sends the output of ps to the input of wc. The shell starts processes and connects their file descriptors. Wc counts lines, including the heading line printed by ps, so subtract one for a rough process count. The count can still change while commands run. The handout's optional strace -c ls counts system calls made while ls lists a directory, making the user/kernel requests visible. Its count can vary with the program's execution.

## A process is a running program

A program is stored instructions. A process is one running instance of a program. The kernel tracks each process with a PID, a state, memory and open file descriptors. The scheduler gives processor time to runnable processes. A process waiting for a timer or another event can sleep, leaving the processor available to other work.

The handout uses sleep 300 & to start a process in the background. The ampersand tells the shell to return to the prompt while the child keeps running. $! is the PID of the most recently started background process. jobs lists background jobs known to that shell; ps shows a broader process snapshot. If you read /proc/PID/status, the kernel supplies current details for that process through a pseudo-filesystem. The path looks like a file, but the status is generated from live kernel state rather than saved as a normal disk file.

A sleeping process commonly reports state S, for interruptible sleep. kill PID sends SIGTERM by default, which asks that process to stop. The shell's wait PID collects its exit status after it ends. The distinction matters: kill sends a request; wait is how the shell later learns that its child has finished.

The report found PID 1 to be systemd, running as /sbin/init. PID 1 is the first user-space process started by the kernel, but its implementation can differ, so inspect the machine rather than assuming it uses systemd.

Use this contained example to see the chain:

    mkdir -p "$HOME/os-lab1/demo"
    cd "$HOME/os-lab1/demo"
    printf 'hello operating systems\n' > note.txt
    chmod 600 note.txt
    ls -l note.txt

    sleep 30 &
    pid=$!
    jobs
    ps -o pid,stat,cmd -p "$pid"
    grep '^State:' "/proc/$pid/status"
    kill "$pid"
    wait "$pid" 2>/dev/null || true

The file commands create and restrict a file only inside the lab folder. The process commands inspect and stop only the sleep process they just started. The wait line tolerates the nonzero status expected after SIGTERM.

## Memory numbers answer different questions

Each process uses virtual addresses, which form its own view of memory. The processor and kernel translate those addresses to physical RAM. This separation lets two processes use the same virtual address without referring to the same physical memory. It also prevents one user program from freely changing another process's memory.

free -h summarizes RAM and swap. Free is RAM not currently in use; available estimates how much the kernel could give programs without swapping, including memory held in reclaimable caches. Thus available can be larger than free. Swap is disk space used to hold memory pages when RAM is under pressure, and it is slower than RAM. /proc/meminfo exposes more system totals.

VmRSS in /proc/PID/status answers a narrower question: how much of this process's memory is resident in RAM now. It is not the process's full virtual address space. A sleeping process can still have code, a stack and library pages resident, so its RSS does not have to be zero.

The recorded report snapshot shows 3.8 GiB total RAM, 3.0 GiB free, 3.4 GiB available, no configured swap, and 1,968 kB of resident memory for its sleep process. Those figures describe one Ubuntu VM on 28 September 2026. They are examples of what the commands report, not values another machine should produce.

## Storage and devices have different views

A disk is a block device. A partition divides its storage, and a filesystem organizes files on that partition. lsblk shows the device and partition layout. df -h / shows the capacity and free space of the filesystem mounted at /. It is possible for one device to contain several partitions, while df reports the filesystem currently mounted at a particular path. mount shows where filesystems join the directory tree.

Linux exposes many devices under /dev. A path such as /dev/cdrom may be a symbolic link to another device path, such as /dev/sr0. The recorded report found /dev/cdrom linking to a ROM device. “Everything is a file” describes the common file-like interface used for many devices. It does not mean a device is an ordinary document or that every device has the same operations as a regular file.

## A short route for explaining the lab

Start with the kernel as the manager that mediates access to resources, then trace echo with output redirection: the shell opens the file and redirects descriptor 1 before text is written. Use chmod 600 to explain how file metadata controls access. Then compare a stored program with the running sleep process, using its PID and /proc state to show what the kernel tracks. Explain that free, VmRSS, df and lsblk answer different questions about memory and storage. Close by describing /dev as a shared file-like interface, with the limit that a device is not a regular file.

## Practice prompts

1. Predict the permission characters after chmod 600 note.txt. Explain why each group of three has those characters.
2. After sleep 30 &, what does $! contain? How does jobs differ from ps?
3. Why might a sleeping process still have nonzero VmRSS? What does that value leave out?
4. df -h / and lsblk show different output. Which one answers “How much space is free on the mounted root filesystem?”
5. Explain “everything is a file” using /dev/cdrom. Give one reason the phrase can be misleading.

## Check your answers

1. The mode is -rw------- for a regular file. The first - marks the file type. The owner has read and write; group and others have no permissions.
2. $! contains the PID of the last background process started by that shell. jobs reports that shell's background jobs; ps asks for a system process snapshot.
3. Code, stack and other pages can remain resident while the process waits. RSS counts resident memory, not the full virtual address space or all kernel bookkeeping.
4. df -h / reports space on the filesystem mounted at /. lsblk shows block devices and partitions.
5. /dev/cdrom may name a device through a file-like interface and may link to /dev/sr0. A device is not a normal document, and its operations can differ from regular-file reads and writes.

## Source note

The command examples follow Parts 1 to 4 of [the handout](lab-01-brief.docx). The dated outputs above come from [the existing report](report.md); Lab 1 contains no C implementation to trace. The [course overview](../README.md#completion-record) records the owner's 15 October confirmation that all six labs were completed with 10/10 each; the portal gradebook was not independently checked.
