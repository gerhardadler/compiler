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
mov dword [rbp-4], 3
mov dword [rbp-8], 2
mov eax, dword [rbp-8]
add eax, 4
mov ebx, eax
mov ecx, dword [rbp-4]
sub ebx, ecx
mov esi, ebx
add esi, 2
mov dword [rbp-4], esi
mov rsp, rbp
pop rbp
ret