#!/bin/bash

#Exercício 1
echo "Texto de Lisboa" > lisboa.txt
echo "Texto de Porto" > porto.txt
echo "Texto de Braga" > braga.txt
touch porto.txt
touch braga.txt

#Exercício 2
ls -l lisboa.txt

#Exercício 3
chmod -f 666 lisboa.txt

#Exercício 4
chmod -f 500 porto.txt

#Exercício 5
chmod -f 400 braga.txt

#Exercício 6
mkdir dir1 dir2
ls -ld dir1 dir2

#Exercício 7
chmod 766 dir2

