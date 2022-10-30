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
add rbp, 20
mov rsi, rbp
sub rbp, 20
add rbp, 16
mov edx, [rbp]
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
sub rbp, 2
mov word [rbp], 65
add rbp, 2
sub rbp, 4
mov word [rbp], 66
add rbp, 4
sub rbp, 4
mov ax, word [rbp]
add rbp, 4
sub rbp, 6
mov word [rbp], ax
add rbp, 6
sub rbp, 10
mov dword [rbp], 2
add rbp, 10
sub rsp, 10
call print
add rsp, 10
sub rbp, 6
mov word [rbp], 10
add rbp, 6
sub rbp, 10
mov dword [rbp], 2
add rbp, 10
sub rsp, 10
call print
add rsp, 10
mov rsp, rbp
pop rbp
ret