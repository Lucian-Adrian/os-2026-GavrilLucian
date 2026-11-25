#!/usr/bin/env python3
"""Boot xv6 (make qemu) in DIR, type each command at the "$ " prompt, print the console.
Usage: xv6run.py DIR 'cmd1' 'cmd2' ...   (timeout per command: 60 s)"""
import os, pty, select, subprocess, sys, time

d, cmds = sys.argv[1], sys.argv[2:]
master, slave = pty.openpty()
p = subprocess.Popen(["make", "-s", "qemu", "CPUS=3"], cwd=d, stdin=slave, stdout=slave,
                     stderr=slave, start_new_session=True)
os.close(slave)
buf = b""

def read_until(tok, t=60):
    global buf
    end = time.time() + t
    while time.time() < end:
        r, _, _ = select.select([master], [], [], 0.5)
        if r:
            try:
                chunk = os.read(master, 65536)
            except OSError:
                return False
            buf += chunk
            if buf.endswith(tok):
                return True
    return False

read_until(b"$ ", 120)
for c in cmds:
    os.write(master, c.encode() + b"\n")
    read_until(b"\n$ ", 60)
os.write(master, b"\x01x")   # Ctrl-A x: quit qemu
time.sleep(1)
p.kill()
sys.stdout.write(buf.decode(errors="replace").replace("\r", ""))
