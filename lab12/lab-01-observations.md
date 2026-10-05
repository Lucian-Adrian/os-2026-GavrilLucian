# Operating Systems Lab 1: The OS as a Resource Manager

**Track:** A, Linux  
**Environment:** Ubuntu 24.04.4 LTS VM, Linux kernel 6.8.0-136-generic, x86_64  
**VM user:** `ubuntu`  
**Date:** 2026-09-28

## Files and directories

**Interesting output: permissions after `chmod 600`**

```text
$ ls -l note.txt
-rw------- 1 ubuntu ubuntu 24 Sep 28 14:24 note.txt
```

The created files were owned by `ubuntu` and belonged to group `ubuntu`. After `chmod 600`, the mode was `-rw-------`. The first character, `-`, marks a regular file. The next three characters are the owner's permissions (`rw-`), followed by the group's (`---`) and others' (`---`). So the owner could read and write the file, while the group and other users had no permissions.

Two directories directly under `/` are `/etc`, which holds system configuration, and `/home`, which contains users' home directories.

## Processes

**Interesting output: sleeping process in `/proc`**

```text
Name:   sleep
State:  S (sleeping)
Pid:    1784
```

Process 1 had PID `1` and was `systemd`, running as `/sbin/init`. The idle process snapshot returned 103 lines from `ps aux | wc -l`; one line is the header, so the snapshot contained about 102 processes. `top` also showed 102 tasks. The test `sleep` process had state `S (sleeping)` while it was waiting, and the script stopped it afterward.

## Memory

**Interesting output: `free -h`**

```text
               total        used        free      shared  buff/cache   available
Mem:           3.8Gi       407Mi       3.0Gi       976Ki       614Mi       3.4Gi
Swap:             0B          0B          0B
```

At the time of the measurement, the VM had `3.8 GiB` of RAM in total and `3.0 GiB` free. The `available` value was `3.4 GiB`, which also counts memory the system can reclaim if needed. Swap is storage the OS can use to hold memory pages when RAM is under pressure; this VM had `0 B` configured.

The `sleep` process used `1,968 kB` of resident memory (`VmRSS`). A small nonzero resident set is expected even while the process waits: executable code, stack pages and mapped runtime pages still occupy memory. The kernel's own process bookkeeping is not part of this user-process RSS value.

## Devices and storage

**Interesting output: root filesystem from `df -h`**

```text
/dev/sda1        19G  1.9G   17G  11% /
```

The root filesystem `/` was mounted on `/dev/sda1`, an ext4 partition. `lsblk` showed the 20 GiB virtual disk `sda` and its partitions. One `/dev` entry was `/dev/cdrom`, a symbolic link to `/dev/sr0`; `lsblk` identified `sr0` as a ROM device.

Here, “everything is a file” means the OS exposes many devices through file-like paths under `/dev`, such as `/dev/cdrom` linking to `/dev/sr0`, so programs can access devices through a common interface.

## Closing synthesis

The OS manages files and directories, which I inspected with `ls -l` and `ls -la /`, and processes, which I inspected with `ps aux` and `/proc/<pid>/status`.  
It manages memory, which I inspected with `free -h` and `/proc/meminfo`.  
It manages devices and storage, which I inspected with `lsblk`, `df -h`, and `ls -l /dev`.

## Visual evidence

![Lab 1 Linux output rendered from the saved VM transcript](D:/ops/uni/os/lab1/proof-linux-output.png)

The image renders selected lines from the actual VM capture in [the original transcript](D:/ops/uni/os/lab1/evidence.txt). The text file is the complete primary record.
