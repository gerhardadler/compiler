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
push rcx
push r11
mov rax, 1
mov rdi, 1
add rbp, 18
movzx rsi, rbp
sub rbp, 18
add rbp, 16
movzx rdx, word [rbp]
sub rbp, 16
syscall
pop r11
pop rcx
mov rsp, rbp
pop rbp
ret
main:
push rbp
mov rbp, rsp
sub rbp, -4
mov dword [rbp], 65
add rbp, -4
sub rbp, -8
mov dword [rbp], 2
add rbp, -8
sub rbp, -4
mov eax, dword [rbp]
add rbp, -4
sub rbp, 12
mov dword [rbp], eax
add rbp, 12
sub rbp, 14
mov word [rbp], 4
add rbp, 14
sub rsp, 14
call print
add rsp, 14
sub rbp, 12
mov dword [rbp], 10
add rbp, 12
sub rbp, 14
mov word [rbp], 1
add rbp, 14
sub rsp, 14
call print
add rsp, 14
sub rbp, -4
mov r15d, dword [rbp]
add rbp, -4
sub rbp, -8
add r14d, dword [rbp]
add rbp, -8
add r15d, r14d
sub rbp, -4
mov dword [rbp], r15d
add rbp, -4
sub rbp, -4
mov eax, dword [rbp]
add rbp, -4
sub rbp, 12
mov dword [rbp], eax
add rbp, 12
sub rbp, 14
mov word [rbp], 4
add rbp, 14
sub rsp, 14
call print
add rsp, 14
sub rbp, 12
mov dword [rbp], 10
add rbp, 12
sub rbp, 14
mov word [rbp], 1
add rbp, 14
sub rsp, 14
call print
add rsp, 14
sub rbp, -4
mov r15d, dword [rbp]
add rbp, -4
sub rbp, -8
add r14d, dword [rbp]
add rbp, -8
add r15d, r14d
add r15d, 1
sub rbp, -4
mov dword [rbp], r15d
add rbp, -4
sub rbp, -4
mov eax, dword [rbp]
add rbp, -4
sub rbp, 12
mov dword [rbp], eax
add rbp, 12
sub rbp, 14
mov word [rbp], 4
add rbp, 14
sub rsp, 14
call print
add rsp, 14
sub rbp, 12
mov dword [rbp], 10
add rbp, 12
sub rbp, 14
mov word [rbp], 1
add rbp, 14
sub rsp, 14
call print
add rsp, 14
mov rsp, rbp
pop rbp
ret