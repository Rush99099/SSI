#!/bin/bash

# Exercício 0: Observar ficheiros de sistema [cite: 63]
cat /etc/passwd
cat /etc/group

#Exercício 1
sudo adduser bruno
sudo adduser gonc
sudo adduser ric

#Exercício 2
sudo groupadd grupo-ssi
sudo groupadd par-ssi
sudo usermod -aG grupo-ssi bruno
sudo usermod -aG grupo-ssi mig
sudo usermod -aG grupo-ssi rod
sudo usermod -aG par-ssi bruno
sudo usermod -aG par-ssi rod

#Exercício 3

#Existem agora 2 novas entradas ("grupo-ssi" e "par-ssi") quando realizamos o comando
#cat /etc/group, tendo à frente destes uma lista com os elementos que formam o grupo.

#Exercício 4
sudo chown mig dir1/braga.txt 
sudo chown mig dir2/braga.txt 

#Exercício 5
cat braga.txt

#Exercício 6
su mig

#Exercício 7
id
groups
#Tanto num como no outro, aparecem os IDs do utilizador e os grupos a que tem acesso

#Exercício 8
#Todos os utilizadores conseguem ler o ficheiro. Estando na dir1.

#Exercício 9
su rod
#O utilizador "rod" não consegue ler o ficheiro porque não tem permissão para tal.
