section .text
global _start
_start:
call main
mov rax, 60
mov rdi, 0
syscall
print:
push rbp
mov rbp, rsp
mov r15, 1
mov rax, r15
mov r15, 1
mov rdi, r15
add rbp, 16
mov r15, rbp
sub rbp, 16
mov rsi, r15
mov r15, 8
mov rdx, r15
syscall
mov r15, 0
mov rax, r15
mov rsp, rbp
pop rbp
ret
main:
push rbp
mov rbp, rsp
mov r15, 3
add r15, 2
sub rbp, 4
mov dword [rbp], r15d
add rbp, 4
mov r15, 0
mov rax, r15
mov rsp, rbp
pop rbp
ret