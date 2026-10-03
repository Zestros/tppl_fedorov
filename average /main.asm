default rel
global main
extern fopen, fgetc, ferror, fclose, printf

section .data
mode: db 'rb', 0
fmt: db '%s: %lld', 10, 0
bad: db '%s: файл испорчен', 10, 0
usage: db 'Usage: ./average <file>', 10, 0

section .text
main:
    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13
    push r14
    sub rsp, 32
    xor r12d, r12d
    cmp edi, 2
    jne .usage
    mov rbx, [rsi + 8]
    mov rdi, rbx
    lea rsi, [mode]
    call fopen
    test rax, rax
    jz .bad
    mov r12, rax
    mov rdi, r12
    call read_row
    test ecx, ecx
    jz .bad
    cmp r8d, 10
    jne .bad
    mov r13, rax
    mov r14, rdx
    mov rdi, r12
    call read_row
    test ecx, ecx
    jz .bad
    cmp rdx, r14
    jne .bad
    sub r13, rax
    jo .bad
    mov rdi, r12
    call fgetc
    cmp eax, -1
    jne .bad
    mov rdi, r12
    call ferror
    test eax, eax
    jnz .bad
    mov rax, r13
    cqo
    idiv r14
    mov rdx, rax
    mov rsi, rbx
    lea rdi, [fmt]
    xor eax, eax
    call printf
    mov dword [rbp - 40], 0
    jmp .close
.bad:
    mov rsi, rbx
    lea rdi, [bad]
    xor eax, eax
    call printf
    mov dword [rbp - 40], 1
.close:
    test r12, r12
    jz .return
    mov rdi, r12
    call fclose
.return:
    mov eax, [rbp - 40]
    jmp .done
.usage:
    lea rdi, [usage]
    xor eax, eax
    call printf
    mov eax, 2
.done:
    add rsp, 32
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp
    ret

read_row:
    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13
    push r14
    push r15
    sub rsp, 24
    mov r12, rdi
    xor r13d, r13d
    xor r14d, r14d
.number:
    xor r15d, r15d
    mov dword [rbp - 44], 0
    call .get
.leading:
    cmp eax, ' '
    je .leading_next
    cmp eax, 9
    je .leading_next
    cmp eax, '-'
    je .negative
    cmp eax, '+'
    jne .first_digit
    call .get
    jmp .first_digit
.leading_next:
    call .get
    jmp .leading
.negative:
    mov dword [rbp - 44], 1
    call .get
.first_digit:
    cmp eax, '0'
    jl .error
    cmp eax, '9'
    jg .error
.digit:
    sub eax, '0'
    imul r15, r15, 10
    jo .error
    sub r15, rax
    jo .error
    call .get
    cmp eax, '0'
    jl .number_done
    cmp eax, '9'
    jle .digit
.number_done:
    cmp dword [rbp - 44], 0
    jne .add
    neg r15
    jo .error
.add:
    add r13, r15
    jo .error
    inc r14
    jo .error
.trailing:
    cmp eax, ' '
    je .trailing_next
    cmp eax, 9
    je .trailing_next
    cmp eax, ','
    je .number
    cmp eax, 13
    jne .end
    call .get
    cmp eax, 10
    jne .error
.end:
    cmp eax, 10
    je .success
    cmp eax, -1
    jne .error
.success:
    mov r8d, eax
    mov rax, r13
    mov rdx, r14
    mov ecx, 1
    jmp .done
.trailing_next:
    call .get
    jmp .trailing
.error:
    xor ecx, ecx
.done:
    add rsp, 24
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp
    ret
.get:
    sub rsp, 8
    mov rdi, r12
    call fgetc
    add rsp, 8
    ret


section .note.GNU-stack noalloc noexec nowrite progbits
