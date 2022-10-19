section .text
    global _start
_start:
    call main

    mov rax, 60
    mov rdi, 0
    syscall

main:
    push rbp
    mov rbp, rsp
    mov dword [rbp-4], 3
    mov dword [rbp-8], 2
    mov eax, dword [rbp-8]
    add eax, 4
    mov ebx, dword [rbp-4]
    sub eax, ebx
    mov dword [rbp-4], eax
    mov rsp, rbp
    pop rbp
    ret