NASM ?= nasm
CC = gcc
FILE ?= data.txt

.PHONY: all run clean
all: average

average: main.o
	$(CC) -no-pie main.o -o average

main.o: main.asm
	$(NASM) -f elf64 main.asm -o main.o

run: average
	./average "$(FILE)"

clean:
	rm -f average main.o
