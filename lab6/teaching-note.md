# Lab 6: explain the filesystem through xv6

How does a pathname become the metadata printed by `mystat`, and why can two pathnames report the same inode? This lab follows those questions through a small operating system whose implementation is available to read. It then uses `find` to show how a directory can be traversed as structured file data.

The work connects three levels: the user programs that ask questions, the kernel services that resolve paths and inspect objects, and the disk format that limits what the filesystem can represent. Keeping those levels distinct explains both the successful examples and the limits of the programs.

## First principles

A user program executes in a process with its own virtual address space. The kernel manages the filesystem and other protected services. A system call crosses that boundary with arguments describing the requested operation. User code can request metadata without being allowed to edit arbitrary kernel memory.

A directory entry maps a name to an inode number. The inode describes the object: its type, link count, size and block addresses. A path such as `a/r2` is resolved by looking up `a` in one directory and then `r2` in that directory. An inode number is an identity within a filesystem; it is not an address where file contents begin.

Opening a path gives the process a file descriptor, a small integer selecting one of its open kernel file objects. The descriptor is an existing reference, whereas the pathname is a route for a lookup. This distinction lets an open file outlive removal of its final name.

`struct stat` is a report of selected metadata. It is neither the on-disk inode nor permission to edit the kernel's inode. In `mystat`, the local `st` belongs to user memory. The kernel collects metadata in its own temporary structure and copies the result to the caller's address. The user program can then inspect that copy.

The disk inode and the kernel's cached inode also serve different purposes. The disk format stores persistent fields. The cached object adds runtime state such as references and locks. A hard-link count describes persistent names; an in-memory reference count describes current use of the cached object. Their different lifetimes are central to unlinking.

![Conceptual diagram of names, inodes, and links](assets/concept-filesystem-links.png)

The diagram omits the open-file-table layer; follow the source trace below for the descriptor path.

## Trace mystat through the source

Use this worked case in a fresh disposable xv6 image. `X` below is a symbolic inode label, not an observed number:

    $ ln README r2
    $ mystat README r2

    README -> inode X
    r2     -> inode X

After `ln`, both names should report inode `X` with link count 2, assuming `README` initially had one link and `r2` did not already exist. Hard linking adds a directory entry for the same inode; it does not copy the file contents. A pre-existing target name makes the link command fail, so the assumption belongs in the explanation.

1. The shell supplies `argc = 3` and the strings `mystat`, `README`, `r2`. [user/mystat.c](user/mystat.c) starts its loop at argument 1, excluding the program name, and calls `stat(argv[i], &st)` for each path.
2. In [user/ulib.c](../lab2/user/ulib.c), `stat` is a user-library helper implemented as `open`, `fstat`, `close`. The `open` system call resolves the name and returns a temporary descriptor. `stat` itself is not a separate system call in this tree.
3. `sys_fstat` in [kernel/sysfile.c](../lab2/kernel/sysfile.c) obtains the file object corresponding to that process's descriptor and the destination user address. It passes them to `filestat` in [kernel/file.c](../lab2/kernel/file.c).
4. `filestat` locks the inode, calls `stati` in [kernel/fs.c](../lab2/kernel/fs.c), then unlocks it. `stati` fills `dev`, `ino`, `type`, `nlink` and `size`, as defined in [kernel/stat.h](../lab2/kernel/stat.h). `filestat` uses `copyout` and the process's page table to copy that kernel-local structure into user memory. The two variables named `st` are separate objects on opposite sides of the boundary.
5. Back in user code, `typename(st.type)` selects the printable type, and `printf` prints the values. The current [user/printf.c](../lab2/user/printf.c) supports the `%ld` format used for the size. No file-content read is needed to report that size.

The fd used inside stat is temporary and is closed before stat returns. The caller receives metadata in st, not an open descriptor.

This trace also explains failure. If a pathname cannot be opened, the helper returns an error and `mystat` prints a message for that path, then continues its loop. In this implementation, `main` still reaches `exit(0)` after such per-path failures. An error message therefore does not automatically imply a failing overall exit status. That is a property of this source, not a universal convention for `stat` tools.

## Trace find through the source

Create a small directory and file, then search for the basename:

    $ mkdir a
    $ echo x > a/r2
    $ find a r2 -n

[user/find.c](user/find.c) receives `a` as `argv[1]`, `r2` as `argv[2]`, and enables inode output because `argv[3]` equals `-n`. It opens `a` and uses `fstat` to check its type. If the starting object is not a directory, the function closes it and returns without printing it.

A directory is represented as a sequence of `struct dirent` records in [kernel/fs.h](../lab2/kernel/fs.h). Each record contains an inode number and a fixed-width name. The `read` loop requests one complete record at a time. An inode number of zero marks an unused entry, so that record is skipped.

The name field has room for 14 bytes and need not contain a terminating zero when full. The code copies all 14 bytes into a 15-byte local array and explicitly sets `name[DIRSIZ] = 0`. This creates a valid C string before `strcmp` is used. The extra byte is a memory-safety requirement, not space for a longer on-disk filename.

The function first copies `a` into `buf`, adds `/`, and keeps `p` pointing just after that slash. For the `r2` entry, `strcpy(p, name)` makes `buf` contain `a/r2`. A `stat` of that full path supplies the child's type and inode. Comparing the entry's basename with the target succeeds, so the function prints `a/r2` and, for `-n`, its inode number. The numeric value is determined by the image's allocation history.

For a deeper example, suppose `a/sub/r2` also exists. When the current entry is `sub`, the target comparison fails, but its type is a directory, so `find("a/sub", "r2")` is called. That new call has its own local buffer and descriptor. It can discover `a/sub/r2`; after it returns, the parent call continues reading `a`. This is a depth-first traversal: a discovered directory is explored before the parent moves to its next entry.

Skipping `.` and `..` prevents the search from repeatedly entering the same directory or returning to its parent. A matching directory is printed before it is searched, because the match check appears before the recursive call. The starting directory itself is not tested for a name match; only entries discovered inside it are tested.

The path buffer is 512 bytes. Before reading entries, the code reserves room for the parent path, a slash, a full `DIRSIZ` name and the terminating zero. Its check is conservative: even when the next actual child name would be short, the reserved worst case can reject a long parent path. Ancestor descriptors remain open during recursive calls, so a deep tree may hit the process descriptor limit before reaching the path-buffer limit. No single small successful search proves those limits cannot be reached.

This program compares names with `strcmp`; it implements neither wildcard patterns nor the full Linux `find` expression language. An unquoted `*` may also be expanded by Bash before a Linux program sees it, while the course xv6 shell has different parsing behavior. Use a literal basename when explaining this code.

## Trace hard-link removal

Use X to follow the state without assuming a particular run's inode number:

    Before: README -> inode X, nlink 1
    ln README r2
    After:  README -> inode X, r2 -> inode X, nlink 2
    rm README
    After:  r2 -> inode X, nlink 1

In [kernel/sysfile.c](../lab2/kernel/sysfile.c), sys_unlink clears the selected directory entry, decrements ip->nlink, and calls iunlockput. Removing one name leaves the other directory entry pointing at the same inode.

When the last name is removed, the link count reaches zero. That makes the object eligible for reclamation once no other live references need it. In [kernel/fs.c](../lab2/kernel/fs.c), the relevant branch of `iput` is:

```c
if(ip->ref == 1 && ip->valid && ip->nlink == 0){
    // truncate and free the inode
}
```

Why does it test `ref == 1`, rather than zero? The caller is releasing the final reference it currently holds. The cleanup runs while that reference still protects the object; `iput` decrements `ref` afterward. An open file holding another reference prevents that branch at this point. `fileclose` in [kernel/file.c](../lab2/kernel/file.c) eventually releases the open file's inode reference through `iput`.

`itrunc` frees the direct data blocks. If the indirect block exists, it reads that block, frees the data blocks named inside it, then frees the indirect block itself. It clears the block addresses and resets the size. `iput` then marks the inode's type as unused and updates persistent metadata. The indirect pointer block is filesystem overhead that must also be reclaimed, even though it is not part of the file's byte contents.

A precise explanation distinguishes no remaining names from releasing the last cached reference: `nlink == 0` and `ref == 1` before the final decrement.

## Derive the file-size limit

An inode cannot contain an unlimited array of disk addresses. In this [kernel/fs.h](../lab2/kernel/fs.h), `addrs` has 12 entries that point directly to data blocks and one entry that points to another block of addresses. Each block is `BSIZE = 1024` bytes; each address is a 4-byte `uint`. The indirect block can therefore hold `1024 / 4 = 256` data-block addresses. This yields:

    (12 + 256) * 1024 = 274432 bytes = 268 KiB

The indirect block stores pointers, not another 1024 bytes of file data, so it does not add a 269th data block. Reaching this addressing limit also assumes enough free blocks and other required resources exist; a smaller or fuller image can fail earlier.

The corresponding `bmap` function in [kernel/fs.c](../lab2/kernel/fs.c) makes the boundary concrete:

| Byte offset | Logical block, using integer division by 1024 | Address lookup |
| --- | --- | --- |
| 0 | 0 | Direct entry 0 |
| 12,287 | 11 | Direct entry 11, last byte of the direct region |
| 12,288 | 12 | Indirect entry 0 after subtracting `NDIRECT` |
| 274,431 | 267 | Indirect entry 255, last representable byte |

The file size is a byte count, so its final valid byte offset is one less than the size. The size field's integer width alone does not determine this limit; the block-address scheme imposes the smaller bound here.

`DIRSIZ` is 14. A `dirent` contains a 2-byte inode number and a 14-byte name, giving a 16-byte record in this format. The kernel's directory-name handling uses that fixed width, so longer path components are truncated during lookup/creation in this tree. Names with equal first 14 bytes can therefore collide. This is a per-component filename limit, distinct from `find`'s complete-path buffer and descriptor limits. It is not a Linux filename limit.

## How the image separates metadata from data

The layout comment and `superblock` in [kernel/fs.h](../lab2/kernel/fs.h) describe the image as boot block, superblock, log, inode blocks, free-block bitmap and data blocks. The superblock records where the regions begin and how large the filesystem is. An inode number can therefore select an inode record, while the inode's block addresses select its data. The free-block bitmap answers which disk blocks are available for allocation; it is separate from the inode's reference count.

The saved [report](report.pdf), dated 12 October 2026, records the following observations:

- mystat README r2 showed the same inode for both names and a link count of 2. After removing README, r2 retained that inode with a link count of 1.
- find returned ./r2, ./a/b/r2, and ./a/r2. With -n, the report records inodes 3, 26, and 27. mystat cat records inode 3 with link count 2.
- The recorded mkfs output was nmeta 47, 1953 data blocks, and 2000 total blocks.

The layout arithmetic is `47 + 1953 = 2000`: the metadata and data regions account for the image's blocks. The reported data-region capacity is not a statement that all 1,953 blocks remain free after programs and files are placed in the image. Nor does an image-wide block count replace the per-file addressing bound derived above. These are historical observations, separate from the symbolic examples; no new run is represented here.

## Build path

The lab supplies user programs, not a complete kernel tree. Use a Linux/WSL shell with Bash, Python 3, make, a host C compiler, Perl, a RISC-V compiler and `qemu-system-riscv64` available:

```bash
cd /mnt/d/edu/faf/sem5/os
overlay=$(bash ./lab6/prepare-overlay.sh "$PWD")
cd "$overlay"
make qemu
```

[prepare-overlay.sh](prepare-overlay.sh) creates a fresh temporary copy of Lab 2's complete tree, installs the two Lab 6 user sources and adds their UPROGS entries. It retains the existing sleep and args registrations. The temporary image allows the link/unlink examples to change its files while leaving the course source tree untouched. Exit QEMU with Ctrl-A, release it, then X. The [README](README.md) contains a longer command sequence. The examples above describe expected behavior; they do not represent a new boot. The report's terminal-style figures are reconstructed illustrations rather than original QEMU captures.

## Explain the lab aloud

Start with `mystat README r2`: two names reach one inode, and a user-space helper obtains a metadata copy through kernel services. Walk through `open`, `fstat`, `stati` and `copyout`, then explain why closing the temporary descriptor does not remove the directory entries.

Use `find a r2 -n` to explain directories as records and recursion as repeated application of the same operation to a child directory. Point to the name-copy termination and the `.`/`..` exclusions before discussing output. Then remove a hard link and distinguish `nlink` from `ref`; name the exact `iput` condition rather than paraphrasing both as an open-file count.

Finish by deriving the file-size bound from the actual address layout. A defensible conclusion is: "The observed behavior follows from names referring to inodes, descriptors keeping open references, and a fixed block-address representation. The programs expose those mechanisms, but their successful examples do not establish unlimited path depth or support for Linux's complete command language."

## Practice prompts

1. Run the symbolic trace for `mystat README` when `README` has one link. Add a fresh `spare` hard link, then remove `README`. Predict which metadata changes and which should stay equal, without inventing an inode number.
2. Suppose `a/r2` is a file and `a/sub/r2` is another file. Explain how `find a r2 -n` discovers each. Which source lines cause recursion, and what determines the order?
3. Call `find a a` when `a` exists and is a directory. Must it print `a` itself? Explain from the code, rather than from expectations about Linux `find`.
4. Explain why a 14-byte on-disk name is copied into a 15-byte array before calling `strcmp`. What could go wrong without the extra byte and assignment?
5. A file has no remaining names but still has an open reference. What happens when unlink releases its temporary reference? What changes when the final open reference is released?
6. Derive the lookup for offsets 12,287 and 12,288. Why does the second require an indirect lookup even though the offsets differ by one byte?
7. `mystat` prints an error for a nonexistent path, yet its caller observes exit status 0. Is that incompatible with this implementation?

## Oral questions

1. Is `stat` a system call in this tree, and what does the caller receive?
2. Why does `filestat` use `copyout` instead of assigning through an arbitrary user pointer as if it were kernel memory?
3. Why does `iput` check `ref == 1` rather than `ref == 0` before reclamation?
4. Does the indirect block count toward the maximum file data length? Must it be freed?
5. Which separate limits affect filename length, complete paths, recursion depth and file contents?
6. Why does a successful search of one small tree not prove general correctness or unlimited depth?

## Checking explanations

### Practice

1. Both names initially reach the same inode with link count 2. Removing `README` leaves `spare` with that inode and link count 1; file contents and size are not copied or shortened by the name change. The exact inode value depends on the image.
2. Each directory entry is examined in stored order. A match is printed; a directory triggers a recursive call before the parent resumes its loop. The two paths are discovered through separate directory entries. Their order depends on entry order, not guaranteed alphabetical sorting.
3. No. The function checks its starting object's type but does not compare that object's own basename with the target. It tests only the children it reads.
4. A full-width disk name has no spare byte for a C string terminator. `name[14] = 0` bounds later string operations. Without it, `strcmp` could continue into unrelated memory looking for a zero.
5. Unlink reduces `nlink` to zero, but an additional live reference prevents the final-reference branch from reclaiming the inode. On release of the last reference, `iput` sees `ref == 1` before its own decrement, calls `itrunc` for a valid unlinked inode, marks it unused and finally decrements `ref`.
6. Integer division gives logical blocks 11 and 12. Blocks 0–11 use the 12 direct entries. For block 12, `bmap` subtracts 12 and uses indirect entry 0. The boundary comes from the address layout, not the magnitude of a one-byte change.
7. It matches the source: failed per-path `stat` calls print and continue, while the loop finishes with `exit(0)`. This limits how a script can use its overall status to detect those failures.

### Oral questions

1. Here `stat` is a user-library helper using `open`, `fstat` and `close`. The caller receives copied metadata in its own `struct stat`, not an inode pointer or a descriptor retained by the helper.
2. The address belongs to the process's virtual address space. `copyout` uses that process's page table to find and check the destination mapping, maintaining the separation between user and kernel memory.
3. One reference still belongs to the caller currently releasing it. Cleanup happens before `iput`'s final decrement, while the object remains protected by that reference.
4. It holds addresses rather than file bytes, so it does not add to the 268-data-block capacity. It consumes a filesystem block and must be freed along with the data blocks it names.
5. `DIRSIZ = 14` limits a directory component in this format. `find` uses a 512-byte path buffer and keeps ancestor descriptors during recursion; stack resources also constrain execution. The 12-direct-plus-256-indirect addressing scheme bounds file contents at 274,432 bytes if sufficient storage is available.
6. A small example does not exercise long paths, deep recursion, exhausted descriptors, errors or every directory layout. The source explains which cases are supported and exposes constraints that the example alone cannot test.

## Sources and scope

The original Lab 6 handout is unavailable. [README.md](README.md), [notes.md](notes.md) and the recovered report describe the task; the exact instructor wording is unknown. All implementation explanations refer to the linked local Lab 6 programs and Lab 2 kernel snapshot. In particular, Linux permission semantics from Lab 5 should not be assumed to exist unchanged in this smaller xv6 filesystem.

The report values above are historical observations; the symbolic traces and changed cases are worked reasoning. The [course overview](../README.md) records owner-confirmed completion and grades. Reading this material does not establish independently demonstrated understanding.

Correction to the previous study explanation: reclamation does not wait for `ref` to become zero before checking the inode. This tree checks `ref == 1`, `valid` and `nlink == 0`, then drops the caller's final reference after cleanup. The original code and report artifacts have not been changed.
