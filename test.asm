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
sub rbp, 5
mov byte [rbp], 2
add rbp, 5
sub rbp, 5
movzx eax, byte [rbp]
add rbp, 5
sub rbp, 4
add dword [rbp], eax
add rbp, 4
sub rbp, 4
mov eax, dword [rbp]
add rbp, 4
mov r15, rax
add r15, 1
sub rbp, 13
mov qword [rbp], r15
add rbp, 13
sub rsp, 13
call print
add rsp, 13
mov rsp, rbp
pop rbp
ret