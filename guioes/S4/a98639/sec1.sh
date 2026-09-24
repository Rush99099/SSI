#!/bin/bash

#Setup
gcc -o backupssi backupssi.c
sudo chown root:root backupssi
sudo su root
chmod 4755 backupssi

#Exercício 1
./backupssi

#Exercício 2
#O root é aberto, porém nunca é fechado, por isso todos podem ver
#o que está na pasta /root porque o root usou o seu UID.

#Exercício 3
ls -la /proc/self/fd/3/

#Exercício 4
#Ao usar o close(dfd) antes do setuid, fechamos o acesso à diretoria
#enquanto estamos como root.