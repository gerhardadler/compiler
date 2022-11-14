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
mov rsp, rbp
pop rbp
ret
main:
push rbp
mov rbp, rsp
sub rbp, 4
mov dword [rbp], 65
add rbp, 4
sub rbp, 4
mov eax, dword [rbp]
add rbp, 4
sub rbp, 12
mov qword [rbp], rax
add rbp, 12
sub rsp, 12
call print
add rsp, 12
sub rbp, 4
mov eax, dword [rbp]
add rbp, 4
mov r15, rax
add r15, 1
sub rbp, 4
mov dword [rbp], r15d
add rbp, 4
sub rbp, 4
mov eax, dword [rbp]
add rbp, 4
sub rbp, 12
mov qword [rbp], rax
add rbp, 12
sub rsp, 12
call print
add rsp, 12
sub rbp, 4
mov eax, dword [rbp]
add rbp, 4
mov r15, rax
add r15, 1
sub rbp, 4
mov dword [rbp], r15d
add rbp, 4
sub rbp, 4
mov eax, dword [rbp]
add rbp, 4
sub rbp, 12
mov qword [rbp], rax
add rbp, 12
sub rsp, 12
call print
add rsp, 12
sub rbp, 12
mov qword [rbp], 10
add rbp, 12
sub rsp, 12
call print
add rsp, 12
mov rsp, rbp
pop rbp
ret