#include <stdio.h>
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
}