#!/bin/bash

#Setup
gcc -o passwdleak passwdleak.c
sudo chown root:root passwdleak
sudo su root
chmod 4755 passwdleak

#Exercício 1
su bruno
./passwdleak

#Exercício 2
#O descritor não é fechado antes do execl, levando ao acesso indevido

#Exercício 3
#O ficheiro é aberto com permissões O_WRONLY e O_APPEND, mas não fecha
#antes de executar a shell. Assim, um utilizador normal pode injetar dados
#diretamente no /etc/passwd.

#Exercício 4
#O ssihacker é criado com o UID e GID 0, ou seja, previlégios iguais ao root
#, apenas precisando de fazer login com o ssihacker para ter acesso ao sistema.

#Exercício 5
#Tal como no exercício da secção 1, ao fechar o descritor antes do execl,
# a shell não tem qualquer ligação ao /etc/passwd, não permitindo o acesso.
