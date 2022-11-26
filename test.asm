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
mov rax, 1
mov rdi, 1
add rbp, 16
mov rsi, rbp
sub rbp, 16
mov rdx, 8
syscall
mov rax, 0
mov rsp, rbp
pop rbp
ret
add:
push rbp
mov rbp, rsp
add rbp, 20
mov eax, dword [rbp]
sub rbp, 20
mov r15, rax
add rbp, 16
mov eax, dword [rbp]
sub rbp, 16
add r15, rax
mov rax, r15
mov rsp, rbp
pop rbp
ret
main:
push rbp
mov rbp, rsp
sub rbp, 4
mov dword [rbp], 30
add rbp, 4
sub rbp, 8
mov dword [rbp], 35
add rbp, 8
sub rsp, 8
call add
add rsp, 8
sub rbp, 8
mov qword [rbp], rax
add rbp, 8
sub rsp, 8
call print
add rsp, 8
sub rbp, 8
mov qword [rbp], 10
add rbp, 8
sub rsp, 8
call print
add rsp, 8
mov rax, 0
mov rsp, rbp
pop rbp
ret