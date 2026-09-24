#!/bin/bash

#Exercício 1
echo '#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    // Verifica se foi passado exatamente um argumento (o nome do ficheiro)
    if (argc != 2) {
        fprintf(stderr, "Uso: %s <nome_do_ficheiro>\n", argv[0]);
        return 1;
    }

    // Tenta abrir o ficheiro para leitura
    FILE *ficheiro = fopen(argv[1], "r");

    // Caso não consiga abrir, imprime o erro e termina
    if (ficheiro == NULL) {
        perror("Erro ao abrir o ficheiro");
        return 1;
    }

    // Lê e imprime o ficheiro carater a carater
    int c;
    while ((c = fgetc(ficheiro)) != EOF) {
        putchar(c);
    }

    // Fecha o ficheiro e termina com sucesso
    fclose(ficheiro);
    return 0;
}' > reader.c
gcc reader.c -o reader

#Exercício 2
sudo adduser userssi

#Exercício 3
sudo chown userssi reader dir1/braga.txt
sudo chown userssi reader dir2/braga.txt
sudo chmod 400 dir2/braga.txt

#Exercício 4
su mig
./reader dir2/braga.txt

#Exercício 5
sudo chmod u+s reader
sudo chmod +x dir2

#Exercício 6
#O programa está a correr com o UID do userssi, pelo que, ao usar "cat", os
#outros utilizadores não conseguem ler o ficheiro, porém ao "mascarar" o ficheiro
#executável com o UID, outros utilizadores podem ver o conteúdo do ficheiro através
#do reader.