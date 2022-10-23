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
mov dword [rbp-4], 65
mov dword [rbp-8], 1
mov ebx, dword [rbp-4]
mov ecx, dword [rbp-8]
add ebx, ecx
mov dword [rbp-4], ebx
sub rsp, 4
mov rsp, [rbp-4]
call print
add rsp, 4
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
add rbp, 20
mov rsi, rbp
sub rbp, 20
mov rdx, 1
syscall
pop r11
pop rcx
mov rsp, rbp
pop rbp
ret