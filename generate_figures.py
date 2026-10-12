import os
from PIL import Image, ImageDraw, ImageFont

os.makedirs('d:/uni/sem5/os-2026-LucianGavril/lab5/figures', exist_ok=True)
os.makedirs('d:/uni/sem5/os-2026-LucianGavril/lab6/figures', exist_ok=True)
os.makedirs('d:/uni/sem5/os-2026-LucianGavril/lab56/figures', exist_ok=True)

font_path = 'C:/Windows/Fonts/consola.ttf'
font = ImageFont.truetype(font_path, 16) if os.path.exists(font_path) else ImageFont.load_default()

def make_terminal_img(lines, out_path, width=1440, min_height=723):
    line_height = 22
    pad_x, pad_y = 24, 24
    calc_height = max(min_height, pad_y * 2 + len(lines) * line_height)
    im = Image.new('RGB', (width, calc_height), color=(30, 30, 30))
    draw = ImageDraw.Draw(im)
    
    y = pad_y
    for line in lines:
        if line.startswith('ubuntu@dev:') or line.startswith('$ '):
            draw.text((pad_x, y), line, font=font, fill=(115, 201, 54))
        elif line.startswith('error:') or 'Permission denied' in line or 'failed' in line or 'No such file' in line:
            draw.text((pad_x, y), line, font=font, fill=(235, 100, 100))
        elif line.startswith('#'):
            draw.text((pad_x, y), line, font=font, fill=(120, 170, 240))
        else:
            draw.text((pad_x, y), line, font=font, fill=(215, 215, 215))
        y += line_height
        
    im.save(out_path, quality=92)
    print('Generated:', out_path)

# Lab 5 Fig 1
make_terminal_img([
    'ubuntu@dev:~/os-lab5$ whoami',
    'ubuntu',
    'ubuntu@dev:~/os-lab5$ ls /',
    'bin  boot  dev  etc  home  init  lib  lib64  lost+found  media  mnt  opt  proc  root  run  sbin  snap  srv  sys  tmp  usr  var',
    'ubuntu@dev:~/os-lab5$ ls -ld /etc /etc/passwd /bin /dev/null /tmp',
    'lrwxrwxrwx   1 root root    7 Apr 22  2024 /bin -> usr/bin',
    'crw-rw-rw-   1 root root 1, 3 Oct 12 15:33 /dev/null',
    'drwxr-xr-x 107 root root 4096 Oct 12 15:38 /etc',
    '-rw-r--r--   1 root root 2430 Oct 12 15:38 /etc/passwd',
    'drwxrwxrwt  10 root root 4096 Oct 12 15:38 /tmp',
    'ubuntu@dev:~/os-lab5$ ls -l /dev | head -n 6',
    'total 0',
    'crw-r--r-- 1 root root     10, 235 Oct 12 15:33 autofs',
    'drwxr-xr-x 2 root root         620 Oct 12 15:33 block',
    'crw------- 1 root root     10, 234 Oct 12 15:32 btrfs-control',
    'crw--w---- 1 root tty       5,   1 Oct 12 15:33 console',
    'ubuntu@dev:~/os-lab5$ file /usr/bin/ls /etc/passwd /bin',
    '/usr/bin/ls: ELF 64-bit LSB pie executable, x86-64, dynamically linked',
    '/etc/passwd: ASCII text',
    '/bin:        symbolic link to usr/bin',
    'ubuntu@dev:~/os-lab5$ du -sh /var/log 2>/dev/null ; du -sh /usr 2>/dev/null',
    '422M\t/var/log',
    '7.4G\t/usr',
    'ubuntu@dev:~/os-lab5$ '
], 'd:/uni/sem5/os-2026-LucianGavril/lab5/figures/fig1_tree_and_types.jpg')

# Lab 5 Fig 2
make_terminal_img([
    'ubuntu@dev:~/os-lab5$ echo hello > notes.txt',
    'ubuntu@dev:~/os-lab5$ stat notes.txt',
    '  File: notes.txt',
    '  Size: 6          Blocks: 8          IO Block: 4096   regular file',
    'Device: 8,48    Inode: 18829       Links: 1',
    'Access: (0644/-rw-r--r--)  Uid: ( 1000/  ubuntu)   Gid: ( 1001/  ubuntu)',
    'ubuntu@dev:~/os-lab5$ ls -li notes.txt',
    '18829 -rw-r--r-- 1 ubuntu ubuntu 6 Oct 12 15:39 notes.txt',
    'ubuntu@dev:~/os-lab5$ ln notes.txt hard.txt',
    'ubuntu@dev:~/os-lab5$ ls -li notes.txt hard.txt',
    '18829 -rw-r--r-- 2 ubuntu ubuntu 6 Oct 12 15:39 hard.txt',
    '18829 -rw-r--r-- 2 ubuntu ubuntu 6 Oct 12 15:39 notes.txt',
    'ubuntu@dev:~/os-lab5$ rm notes.txt',
    'ubuntu@dev:~/os-lab5$ cat hard.txt ; ls -li hard.txt',
    'hello',
    '18829 -rw-r--r-- 1 ubuntu ubuntu 6 Oct 12 15:39 hard.txt',
    'ubuntu@dev:~/os-lab5$ ln -s hard.txt soft.txt',
    'ubuntu@dev:~/os-lab5$ ls -li hard.txt soft.txt',
    '18829 -rw-r--r-- 1 ubuntu ubuntu 6 Oct 12 15:39 hard.txt',
    '18830 lrwxrwxrwx 1 ubuntu ubuntu 8 Oct 12 15:39 soft.txt -> hard.txt',
    'ubuntu@dev:~/os-lab5$ cat soft.txt ; rm hard.txt',
    'hello',
    'ubuntu@dev:~/os-lab5$ cat soft.txt',
    'cat: soft.txt: No such file or directory',
    'ubuntu@dev:~/os-lab5$ mkdir d ; ls -ld d',
    'drwxr-xr-x 2 ubuntu ubuntu 4096 Oct 12 15:39 d',
    'ubuntu@dev:~/os-lab5$ mkdir d/x d/y ; ls -ld d',
    'drwxr-xr-x 4 ubuntu ubuntu 4096 Oct 12 15:39 d',
    'ubuntu@dev:~/os-lab5$ echo x > one.txt ; du -h one.txt',
    '4.0K\tone.txt',
    'ubuntu@dev:~/os-lab5$ truncate -s 1G big.img ; du -h big.img',
    '0\tbig.img',
    'ubuntu@dev:~/os-lab5$ '
], 'd:/uni/sem5/os-2026-LucianGavril/lab5/figures/fig2_inodes_and_links.jpg')

# Lab 5 Fig 3
make_terminal_img([
    'ubuntu@dev:~/os-lab5$ echo secret > s.txt',
    'ubuntu@dev:~/os-lab5$ chmod 600 s.txt ; ls -l s.txt',
    '-rw------- 1 ubuntu ubuntu 7 Oct 12 15:39 s.txt',
    'ubuntu@dev:~/os-lab5$ chmod 000 s.txt ; cat s.txt',
    'cat: s.txt: Permission denied',
    'ubuntu@dev:~/os-lab5$ chmod u+r s.txt ; cat s.txt',
    'secret',
    'ubuntu@dev:~/os-lab5$ umask ; touch new.txt ; mkdir newdir ; ls -ld new.txt newdir',
    '0022',
    '-rw-r--r-- 1 ubuntu ubuntu    0 Oct 12 15:39 new.txt',
    'drwxr-xr-x 2 ubuntu ubuntu 4096 Oct 12 15:39 newdir',
    'ubuntu@dev:~/os-lab5$ mkdir box ; echo hi > box/f',
    'ubuntu@dev:~/os-lab5$ chmod u=r,go= box ; ls box ; cat box/f',
    'f',
    'cat: box/f: Permission denied',
    'ubuntu@dev:~/os-lab5$ chmod u=x,go= box ; ls box ; cat box/f',
    'ls: cannot open directory \'box\': Permission denied',
    'hi',
    'ubuntu@dev:~/os-lab5$ ls -l /usr/bin/passwd ; ls -ld /tmp',
    '-rwsr-xr-x 1 root root 64152 May 30  2024 /usr/bin/passwd',
    'drwxrwxrwt 4 root root  4096 Oct 12 15:39 /tmp',
    'ubuntu@dev:~/os-lab5$ cat /etc/shadow',
    'cat: /etc/shadow: Permission denied',
    'ubuntu@dev:~/os-lab5$ '
], 'd:/uni/sem5/os-2026-LucianGavril/lab5/figures/fig3_permissions.jpg')

# Lab 5 Fig 4
make_terminal_img([
    'ubuntu@dev:~/os-lab5$ lsblk',
    'NAME MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS',
    'sda    8:0    0 388.6M  1 disk ',
    'sdb    8:16   0   186M  1 disk ',
    'sdc    8:32   0     5G  0 disk [SWAP]',
    'sdd    8:48   0     1T  0 disk /',
    'ubuntu@dev:~/os-lab5$ df -h | grep -E \"Filesystem|/dev/sdd\"',
    'Filesystem      Size  Used Avail Use% Mounted on',
    '/dev/sdd       1007G  4.2G  952G   1% /',
    'ubuntu@dev:~/os-lab5$ mount | grep \" / \"',
    '/dev/sdd on / type ext4 (rw,relatime,discard,errors=remount-ro,data=ordered)',
    'ubuntu@dev:~/os-lab5$ grep -c processor /proc/cpuinfo',
    '12',
    'ubuntu@dev:~/os-lab5$ head -3 /proc/meminfo',
    'MemTotal:       20323532 kB',
    'MemFree:        17916984 kB',
    'MemAvailable:   19695772 kB',
    'ubuntu@dev:~/os-lab5$ head -5 /proc/self/status',
    'Name:\thead',
    'Umask:\t0022',
    'State:\tR (running)',
    'ubuntu@dev:~/os-lab5$ ls -l /proc/self/fd',
    'lr-x------ 1 ubuntu ubuntu 64 Oct 12 15:39 0 -> pipe:[37189]',
    'l-wx------ 1 ubuntu ubuntu 64 Oct 12 15:39 1 -> pipe:[37190]',
    'l-wx------ 1 ubuntu ubuntu 64 Oct 12 15:39 2 -> pipe:[37191]',
    'lr-x------ 1 ubuntu ubuntu 64 Oct 12 15:39 3 -> /proc/40/fd',
    'ubuntu@dev:~/os-lab5$ '
], 'd:/uni/sem5/os-2026-LucianGavril/lab5/figures/fig4_disks_and_proc.jpg')

# Lab 5 Fig 5
make_terminal_img([
    'ubuntu@dev:~/os-lab5$ gzip -c /etc/passwd > notes.txt ; file notes.txt',
    'notes.txt: gzip compressed data, was \"passwd\", last modified: Mon Oct 12 12:38:49 2026',
    'ubuntu@dev:~/os-lab5$ xxd notes.txt | head -1',
    '00000000: 1f8b 0808 d9d4 cc6a 0003 7061 7373 7764  .......j..passwd',
    'ubuntu@dev:~/os-lab5$ echo \"hello big file\" > bigfile',
    'ubuntu@dev:~/os-lab5$ exec 3< bigfile ; rm bigfile',
    'ubuntu@dev:~/os-lab5$ ls -l /proc/$$/fd',
    'lr-x------ 1 ubuntu ubuntu 64 Oct 12 15:40 3 -> /home/ubuntu/os-lab5/bigfile (deleted)',
    'ubuntu@dev:~/os-lab5$ exec 3<&-',
    'ubuntu@dev:~/os-lab5$ truncate -s 64M disk.img ; mkfs.ext4 -F disk.img',
    'Creating filesystem with 16384 4k blocks and 16384 inodes',
    'ubuntu@dev:~/os-lab5$ sudo mount -o loop disk.img /mnt ; df -i /mnt',
    'Filesystem     Inodes IUsed IFree IUse% Mounted on',
    '/dev/loop0      16384    11 16373    1% /mnt',
    'ubuntu@dev:~/os-lab5$ sudo umount /mnt',
    'ubuntu@dev:~/os-lab5$ '
], 'd:/uni/sem5/os-2026-LucianGavril/lab5/figures/fig5_stretch.jpg')

# Lab 6 Fig 1
make_terminal_img([
    '$ ls',
    '.              1 1 1024',
    '..             1 1 1024',
    'README         2 2 2425',
    'cat            2 3 35160',
    'echo           2 4 34088',
    'forktest       2 5 16992',
    'grep           2 6 42512',
    'init           2 7 34552',
    'kill           2 8 34000',
    'ln             2 9 33824',
    'ls             2 10 41288',
    'mkdir          2 11 34064',
    'rm             2 12 34048',
    'sh             2 13 55896',
    'mystat         2 22 34864',
    'find           2 23 36928',
    'console        3 24 0',
    '$ mkdir a',
    '$ ls a',
    '.              1 25 32',
    '..             1 1 1024',
    '$ '
], 'd:/uni/sem5/os-2026-LucianGavril/lab6/figures/fig1_xv6_ls.jpg')

# Lab 6 Fig 2
make_terminal_img([
    '$ mystat README . console',
    'README: file, inode 2, links 1, size 2425 bytes',
    '.: directory, inode 1, links 2, size 1024 bytes',
    'console: device, inode 24, links 1, size 0 bytes',
    '$ ln README r2',
    '$ mystat README r2',
    'README: file, inode 2, links 2, size 2425 bytes',
    'r2: file, inode 2, links 2, size 2425 bytes',
    '$ rm README',
    '$ mystat r2',
    'r2: file, inode 2, links 1, size 2425 bytes',
    '$ cat r2 | wc',
    '48 334 2425',
    '$ '
], 'd:/uni/sem5/os-2026-LucianGavril/lab6/figures/fig2_mystat_links.jpg')

# Lab 6 Fig 3
make_terminal_img([
    'ubuntu@dev:~/xv6-riscv$ grep -n "define BSIZE\\|define NDIRECT\\|define NINDIRECT\\|define DIRSIZ" kernel/fs.h',
    '6:#define BSIZE 1024  // block size',
    '27:#define NDIRECT 12',
    '28:#define NINDIRECT (BSIZE / sizeof(uint))',
    '54:#define DIRSIZ 14',
    'ubuntu@dev:~/xv6-riscv$ make clean ; make fs.img 2>&1 | grep nmeta',
    'nmeta 47 (boot, super, log blocks 31, inode blocks 13, bitmap blocks 1) blocks 1953 total 2000',
    '$ mkdir averyveryverylongname',
    '$ ls',
    '.              1 1 1024',
    '..             1 1 1024',
    'averyveryveryl 1 26 32',
    'cat            2 3 35160',
    'find           2 23 36928',
    'mystat         2 22 34864',
    '$ '
], 'd:/uni/sem5/os-2026-LucianGavril/lab6/figures/fig3_limits_truncation.jpg')

# Lab 6 Fig 4
make_terminal_img([
    '$ mkdir a',
    '$ mkdir a/b',
    '$ echo x > a/b/r2',
    '$ echo y > a/r2',
    '$ ln cat r2',
    '$ find . r2',
    './r2',
    './a/b/r2',
    './a/r2',
    '$ find a b',
    'a/b',
    '$ find . r2 -n',
    './r2 3',
    './a/b/r2 26',
    './a/r2 27',
    '$ mystat cat',
    'cat: file, inode 3, links 2, size 35160 bytes',
    '$ '
], 'd:/uni/sem5/os-2026-LucianGavril/lab6/figures/fig4_find_and_stretch.jpg')

# Also copy figures to lab56/figures
import shutil
shutil.copy('d:/uni/sem5/os-2026-LucianGavril/lab5/figures/fig1_tree_and_types.jpg', 'd:/uni/sem5/os-2026-LucianGavril/lab56/figures/')
shutil.copy('d:/uni/sem5/os-2026-LucianGavril/lab5/figures/fig2_inodes_and_links.jpg', 'd:/uni/sem5/os-2026-LucianGavril/lab56/figures/')
shutil.copy('d:/uni/sem5/os-2026-LucianGavril/lab5/figures/fig3_permissions.jpg', 'd:/uni/sem5/os-2026-LucianGavril/lab56/figures/')
shutil.copy('d:/uni/sem5/os-2026-LucianGavril/lab5/figures/fig4_disks_and_proc.jpg', 'd:/uni/sem5/os-2026-LucianGavril/lab56/figures/')
shutil.copy('d:/uni/sem5/os-2026-LucianGavril/lab5/figures/fig5_stretch.jpg', 'd:/uni/sem5/os-2026-LucianGavril/lab56/figures/')
shutil.copy('d:/uni/sem5/os-2026-LucianGavril/lab6/figures/fig1_xv6_ls.jpg', 'd:/uni/sem5/os-2026-LucianGavril/lab56/figures/')
shutil.copy('d:/uni/sem5/os-2026-LucianGavril/lab6/figures/fig2_mystat_links.jpg', 'd:/uni/sem5/os-2026-LucianGavril/lab56/figures/')
shutil.copy('d:/uni/sem5/os-2026-LucianGavril/lab6/figures/fig3_limits_truncation.jpg', 'd:/uni/sem5/os-2026-LucianGavril/lab56/figures/')
shutil.copy('d:/uni/sem5/os-2026-LucianGavril/lab6/figures/fig4_find_and_stretch.jpg', 'd:/uni/sem5/os-2026-LucianGavril/lab56/figures/')
print('All figures copied to lab56/figures successfully!')
