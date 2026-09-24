#!/bin/bash

sudo apt update && sudo apt install acl -y

#Exercício 1
getfacl dir1/porto.txt

#Exercício 2
setfacl -m g:grupo-ssi:w porto.txt

#Exercício 3
#O getfacl agora mostra uma entrada específica para o "grupo-ssi", e adiciona
#uma enrada "mask" com as permissões rw-.

#Exercício 4
#O utilizador consegue escrever, mas como não tem permissão de leitura, não
#vai conseguir ler o que escreveu no ficheiro.