section .text
global _start
_start:
call main
mov rdi, rax
mov rax, 60
syscall
print:
push rbp
mov rbp, rsp
mov rax, 1
mov rdi, 1
add rbp, 16
mov r15, rbp
sub rbp, 16
mov rsi, r15
mov rdx, 8
syscall
mov rax, 0
print_ret:
mov rsp, rbp
pop rbp
ret
main:
push rbp
mov rbp, rsp
mov rax, 69
jmp main_ret
mov rax, 0
main_ret:
mov rsp, rbp
pop rbp
ret