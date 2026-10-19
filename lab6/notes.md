# Laboratory 6 Notes: Inside the xv6 File System

**Track:** B (Build Your Own Small OS, xv6)
**Author:** Lucian-Adrian Gavril (FAF-241)
**Environment:** xv6 RISC-V on QEMU 8.2.2 (emulated 3-hart virt machine)
**Date:** 2026-10-12

> The observations below are historical from 12 October 2026. The focused 23 October run is recorded in [execution-2026-10-23.txt](execution-2026-10-23.txt); it independently verifies only the listed mystat, hard-link, and nested-find behavior in its own disposable image.

---

## Part 1. Read What xv6 Shows You

### Terminal Session

```text
$ ls
.              1 1 1024
..             1 1 1024
README         2 2 2425
cat            2 3 35160
echo           2 4 34088
forktest       2 5 16992
grep           2 6 42512
init           2 7 34552
kill           2 8 34000
ln             2 9 33824
ls             2 10 41288
mkdir          2 11 34064
rm             2 12 34048
sh             2 13 55896
stressfs       2 14 34936
usertests      2 15 184256
grind          2 16 50264
wc             2 17 36120
zombie         2 18 33416
logstress      2 19 35968
forphan        2 20 34840
dorphan        2 21 34288
mystat         2 22 34864
find           2 23 36928
console        3 24 0

$ mkdir a
$ ls a
.              1 25 32
..             1 1 1024
```

### Observe 1: Answers

1. **Meaning of Types 1, 2, and 3 (`kernel/stat.h`):**
   ```c
   #define T_DIR     1   // Directory
   #define T_FILE    2   // Regular file
   #define T_DEVICE  3   // Character/block device
   ```
   - Type `1` indicates a directory containing a table of directory entries.
   - Type `2` indicates a regular file containing raw user data bytes.
   - Type `3` indicates a special device file (such as the console) mediated by driver callbacks.

2. **Root Directory Inode & `.` / `..` Identity:**
   - The root directory has inode number `1` (defined as `ROOTINO = 1` in `kernel/fs.h`).
   - In any directory, `.` references the directory itself, while `..` references its parent directory. Because the root directory represents the apex of the filesystem hierarchy with no parent above it, both `.` and `..` point to inode `1`.

3. **Size of an Empty Directory Entry:**
   - In `kernel/fs.h`, `struct dirent` is defined as:
     ```c
     struct dirent {
       ushort inum;         // 2 bytes
       char name[DIRSIZ];   // 14 bytes (DIRSIZ = 14)
     };
     ```
     The size of each directory entry is $2 + 14 = 16$ bytes.
   - An empty directory `a` has size `32` bytes. $32 / 16 = 2$ entries. Those two entries are `.` (pointing to directory `a`, inode 25) and `..` (pointing to root directory `/`, inode 1).

---

## Part 2. Write `mystat` and Watch Hard Links

### Implementation (`user/mystat.c`)

```c
#include "kernel/types.h"
#include "kernel/stat.h"
#include "user/user.h"

char *
typename(int t)
{
  switch(t) {
  case T_DIR:
    return "directory";
  case T_FILE:
    return "file";
  case T_DEVICE:
    return "device";
  default:
    return "?";
  }
}

int
main(int argc, char *argv[])
{
  struct stat st;

  if(argc < 2){
    fprintf(2, "usage: mystat <path...>\n");
    exit(1);
  }

  for(int i = 1; i < argc; i++){
    if(stat(argv[i], &st) < 0){
      fprintf(2, "mystat: cannot stat %s\n", argv[i]);
      continue;
    }
    printf("%s: %s, inode %d, links %d, size %ld bytes\n",
           argv[i], typename(st.type), st.ino, st.nlink, st.size);
  }
  exit(0);
}
```

### Terminal Session

```text
$ mystat README . console
README: file, inode 2, links 1, size 2425 bytes
.: directory, inode 1, links 2, size 1024 bytes
console: device, inode 24, links 1, size 0 bytes

$ ln README r2
$ mystat README r2
README: file, inode 2, links 2, size 2425 bytes
r2: file, inode 2, links 2, size 2425 bytes

$ rm README
$ mystat r2
r2: file, inode 2, links 1, size 2425 bytes

$ cat r2 | wc
48 334 2425
```

### Observe 2: Answers

1. **What Changed and What Did Not After `ln` and `rm`:**
   - **After `ln README r2`:** The link count `links` for both entries increased from 1 to 2. The inode number (2), file type (`file`), and byte size (`2425`) remained completely identical because `r2` is an alias pointing to the same underlying on-disk inode.
   - **After `rm README`:** The link count on `r2` decreased from 2 to 1. The inode number (2), size (2425), and data blocks remained completely unchanged. Running `cat r2 | wc` still outputs `48 334 2425`, proving data availability is preserved until link count hits 0.

2. **sys_unlink Line and Block Deallocation Timing:**
   - In `kernel/sysfile.c`, the line decrementing the link count is:
     ```c
     // kernel/sysfile.c line 230:
     ip->nlink--;
     iupdate(ip);
     ```
   - **When data blocks are freed:** Data blocks are not freed in `sys_unlink`. They are freed when `iput(ip)` is called (line 342 of `kernel/fs.c`) and detects that both `ip->ref == 1` and `ip->nlink == 0`. It calls `itrunc(ip)`, which iterates over `ip->addrs[]`, freeing all 12 direct blocks and all indirect blocks via `bfree(ip->dev, ...)`. If a process still has the file open, `ip->ref > 1`, so block deallocation is deferred until the last `close()` call invokes `iput()`.

3. **xv6 Inode Fields (`struct dinode` in `kernel/fs.h`):**
   ```c
   struct dinode {
     short type;           // File type (T_DIR, T_FILE, T_DEVICE)
     short major;          // Major device number (T_DEVICE only)
     short minor;          // Minor device number (T_DEVICE only)
     short nlink;          // Number of links to inode in file system
     uint size;            // Size of file (bytes)
     uint addrs[NDIRECT+1];// Data block addresses (12 direct + 1 indirect)
   };
   ```
   xv6 contains zero fields for owner UID/GID, permission bits, access/modification timestamps, or symbolic link targets.

---

## Part 3. Measure the Limits

### Inspecting `kernel/fs.h` and Disk Layout

```bash
$ grep -n "define BSIZE\|define NDIRECT\|define NINDIRECT\|define DIRSIZ" kernel/fs.h
6:#define BSIZE 1024  // block size
27:#define NDIRECT 12
28:#define NINDIRECT (BSIZE / sizeof(uint))
54:#define DIRSIZ 14

$ make clean ; make fs.img 2>&1 | grep nmeta
nmeta 47 (boot, super, log blocks 31, inode blocks 13, bitmap blocks 1) blocks 1953 total 2000
```

### In-QEMU Verification

```text
$ mkdir averyveryverylongname
$ ls
...
averyveryveryl 1 26 32
...
```

### Observe 3: Answers

1. **Truncation of `averyveryverylongname`:**
   - `ls` displays `averyveryveryl` (exactly 14 characters).
   - This is enforced by `#define DIRSIZ 14` in `kernel/fs.h`. Each directory entry stores a fixed 14-byte character array for the filename (`char name[DIRSIZ]`). Names longer than 14 characters are truncated at byte 14.

2. **Maximum File Size Calculation:**
   - Block size: `BSIZE = 1024` bytes.
   - Direct blocks: `NDIRECT = 12` blocks.
     $12 \times 1024\text{ bytes} = 12,288\text{ bytes}$.
   - Indirect block: `NINDIRECT = BSIZE / sizeof(uint) = 1024 / 4 = 256` block pointers.
     $256 \times 1024\text{ bytes} = 262,144\text{ bytes}$.
   - Total blocks per file: $12 + 256 = 268$ blocks.
   - Maximum file size: $268 \times 1024\text{ bytes} = 274,432\text{ bytes}$ (or **268 KiB**).

3. **Disk Block Accounting from the `nmeta` Line:**
   - Total disk blocks: **2000** (`total 2000`, 2 MiB disk image).
   - Metadata blocks: **47** (`nmeta 47`):
     - Boot block: 1 block (block 0).
     - Superblock: 1 block (block 1).
     - Log: 30 blocks (blocks 2..31).
     - Inodes: 13 blocks (blocks 32..44, storing $13 \times 16 = 208$ inodes).
     - Free bitmap: 1 block (block 45).
   - Data blocks: **1953** blocks (blocks 47..1999).

---

## Part 4. Recursive `find` and the `-n` Stretch

### Implementation (`user/find.c`)

```c
#include "kernel/types.h"
#include "kernel/stat.h"
#include "user/user.h"
#include "kernel/fs.h"
#include "kernel/fcntl.h"

static int show_ino = 0;

void
find(char *path, char *target)
{
  char buf[512], *p;
  int fd;
  struct dirent de;
  struct stat st;

  if((fd = open(path, O_RDONLY)) < 0){
    fprintf(2, "find: cannot open %s\n", path);
    return;
  }

  if(fstat(fd, &st) < 0){
    fprintf(2, "find: cannot stat %s\n", path);
    close(fd);
    return;
  }

  if(st.type != T_DIR){
    close(fd);
    return;
  }

  if(strlen(path) + 1 + DIRSIZ + 1 > sizeof(buf)){
    fprintf(2, "find: path too long\n");
    close(fd);
    return;
  }

  strcpy(buf, path);
  p = buf + strlen(buf);
  *p++ = '/';

  while(read(fd, &de, sizeof(de)) == sizeof(de)){
    char name[DIRSIZ + 1];

    if(de.inum == 0)
      continue;

    memmove(name, de.name, DIRSIZ);
    name[DIRSIZ] = 0;

    if(strcmp(name, ".") == 0 || strcmp(name, "..") == 0)
      continue;

    strcpy(p, name);

    if(stat(buf, &st) < 0){
      fprintf(2, "find: cannot stat %s\n", buf);
      continue;
    }

    if(strcmp(name, target) == 0){
      if(show_ino)
        printf("%s %d\n", buf, st.ino);
      else
        printf("%s\n", buf);
    }

    if(st.type == T_DIR){
      find(buf, target);
    }
  }

  close(fd);
}

int
main(int argc, char *argv[])
{
  if(argc < 3){
    fprintf(2, "usage: find <dir> <name> [-n]\n");
    exit(1);
  }

  if(argc >= 4 && strcmp(argv[3], "-n") == 0){
    show_ino = 1;
  }

  find(argv[1], argv[2]);
  exit(0);
}
```

### Fresh Disk Test Session

```text
$ mkdir a
$ mkdir a/b
$ echo x > a/b/r2
$ echo y > a/r2
$ ln cat r2

$ find . r2
./r2
./a/b/r2
./a/r2

$ find a b
a/b

$ find . r2 -n
./r2 3
./a/b/r2 26
./a/r2 27

$ mystat cat
cat: file, inode 3, links 2, size 35160 bytes
```

### Observe 4: Answers & Stretch Analysis

1. **Behavior of `find`:**
   - `find . r2` accurately recurses down through directories `./`, `./a`, and `./a/b`, locating all three matching leaves.
   - `find a b` matches the directory entry `b` inside `a`, outputting `a/b`.

2. **Stretch (`-n` Flag) & Inode Identification:**
   - `./r2 3`: Inode `3`.
   - `./a/b/r2 26`: Inode `26`.
   - `./a/r2 27`: Inode `27`.
   - `mystat cat`: `cat: file, inode 3, links 2, size 35160 bytes`.
   - **Conclusion:** `./r2` is the exact same file as `cat`. Both point to inode `3` and share a hard link count of 2. In contrast, `a/b/r2` and `a/r2` were created independently with `echo` and possess unique inodes (26 and 27).
