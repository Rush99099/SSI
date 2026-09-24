#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>

int main() {
    int fd = open("/etc/passwd", O_WRONLY | O_APPEND);
    
    if (fd < 0) {
        perror("open /etc/passwd");
        exit(1);
    }

    printf("Passwd FD opened: %d\n", fd);

    if (close(fd) == -1) {
        perror("close");
    }

    if (setuid(getuid()) == -1) {
        perror("setuid");
        exit(1);
    }

    execl("/bin/sh", "sh", NULL);
    
    perror("execl");
    return 0;
}