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
sub rbp, 4
mov eax, dword [rbp]
add rbp, 4
sub rbp, 12
mov dword [rbp], eax
add rbp, 12
sub rsp, 12
call print
add rsp, 12
mov ebx, dword [rbp-4]
mov ecx, dword [rbp-8]
add ebx, ecx
mov dword [rbp-4], ebx
sub rbp, 4
mov eax, dword [rbp]
add rbp, 4
sub rbp, 12
mov dword [rbp], eax
add rbp, 12
sub rsp, 12
call print
add rsp, 12
mov ebx, dword [rbp-4]
mov ecx, dword [rbp-8]
add ebx, ecx
mov dword [rbp-4], ebx
sub rbp, 4
mov eax, dword [rbp]
add rbp, 4
sub rbp, 12
mov dword [rbp], eax
add rbp, 12
sub rsp, 12
call print
add rsp, 12
mov ebx, dword [rbp-4]
mov ecx, dword [rbp-8]
add ebx, ecx
mov dword [rbp-4], ebx
sub rbp, 4
mov eax, dword [rbp]
add rbp, 4
sub rbp, 12
mov dword [rbp], eax
add rbp, 12
sub rsp, 12
call print
add rsp, 12
mov ebx, dword [rbp-4]
mov ecx, dword [rbp-8]
add ebx, ecx
mov dword [rbp-4], ebx
sub rbp, 4
mov eax, dword [rbp]
add rbp, 4
sub rbp, 12
mov dword [rbp], eax
add rbp, 12
sub rsp, 12
call print
add rsp, 12
mov ebx, dword [rbp-4]
mov ecx, dword [rbp-8]
add ebx, ecx
mov dword [rbp-4], ebx
sub rbp, 4
mov eax, dword [rbp]
add rbp, 4
sub rbp, 12
mov dword [rbp], eax
add rbp, 12
sub rsp, 12
call print
add rsp, 12
mov ebx, dword [rbp-4]
mov ecx, dword [rbp-8]
add ebx, ecx
mov dword [rbp-4], ebx
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
mov rdx, 4
syscall
pop r11
pop rcx
mov rsp, rbp
pop rbp
ret