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
mov dword [rbp-8], 65
sub rbp, 8
mov eax, dword [rbp]
add rbp, 8
sub rbp, 8
mov dword [rbp], eax
add rbp, 8
sub rsp, 8
call print
add rsp, 8
mov rsp, rbp
pop rbp
ret
print:
push rbp
mov rbp, rsp
push rcx
push r11
mov rax, 1
mov rdi, 1
add rbp, 16
mov rsi, rbp
sub rbp, 16
mov rdx, 8
syscall
pop r11
pop rcx
mov rsp, rbp
pop rbp
ret