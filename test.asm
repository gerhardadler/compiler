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
    mov dword [rbp-4], 0a214945h
    mov dword [rbp-8], 66

    mov rax, 1
    mov rdi, 1
    mov rsi, rbp
    sub rsi, 4
    mov rdx, 4
    syscall

    mov rsp, rbp
    pop rbp
    ret