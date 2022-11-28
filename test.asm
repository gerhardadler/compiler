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
sub rbp, 4
mov dword [rbp], 1
add rbp, 4
sub rbp, 8
mov dword [rbp], 2
add rbp, 8
sub rbp, 8
mov dword [rbp], 3
add rbp, 8
mov rax, 0
main_ret:
mov rsp, rbp
pop rbp
ret