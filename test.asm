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
add rbp, 0
mov word [rbp], 65
sub rbp, 0
sub rbp, 3
mov byte [rbp], 2
add rbp, 3
add rbp, 0
mov r15w, word [rbp]
sub rbp, 0
sub rbp, 3
add r14b, byte [rbp]
add rbp, 3
add r15w, r14b
sub rbp, 3
mov byte [rbp], r15w
add rbp, 3
sub rbp, 3
mov al, byte [rbp]
add rbp, 3
sub rbp, 12
mov byte [rbp], al
add rbp, 12
sub rsp, 12
call print
add rsp, 12
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
mov rdx, 2
syscall
pop r11
pop rcx
mov rsp, rbp
pop rbp
ret