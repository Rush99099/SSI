import sys

def preproc(texto):
    l = []
    for c in texto:
        if c.isalpha():
            l.append(c.upper())
    return "".join(l)

def main():
    if len(sys.argv) != 4:
        print("Uso: python3 vigenere.py <enc/dec> <chave> <mensagem>")
        return

    op = sys.argv[1]
    chave = preproc(sys.argv[2])
    mensagem = preproc(sys.argv[3])

    if not chave:
        print("A chave deve conter letras.")
        return

    resultado = []
    
    for i, char in enumerate(mensagem):
        pos_char = ord(char) - ord('A')
        
        #Descobrir qual a letra da chave a usar para cada caracter
        letra_chave = chave[i % len(chave)]
        pos_chave = ord(letra_chave) - ord('A')
        
        if op == "enc":
            nova_pos = (pos_char + pos_chave) % 26
        elif op == "dec":
            nova_pos = (pos_char - pos_chave) % 26
        else:
            print("Operação inválida. Use 'enc' ou 'dec'.")
            return
        
        resultado.append(chr(nova_pos + ord('A')))

    print("".join(resultado))

if __name__ == "__main__":
    main()