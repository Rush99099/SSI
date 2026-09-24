import sys

#Converter as letras para maiúsculas
def preproc(texto):
    l = []
    for c in texto:
        if c.isalpha():
            l.append(c.upper())
    return "".join(l)

def main():
    #Failsafe para que o o utilizador saiba como usar
    if len(sys.argv) != 4:
        print("Uso: python3 cesar.py <enc/dec> <chave_letra> <mensagem>")
        return

    op = sys.argv[1]
    chave_letra = sys.argv[2].upper()
    mensagem = preproc(sys.argv[3])

    #Converter letra para a sua posição do alfabeto
    deslocamento = ord(chave_letra) - ord('A')

    resultado = []
    for char in mensagem:
        pos = ord(char) - ord('A')
        
        if op == "enc":
            nova_pos = (pos + deslocamento) % 26
        elif op == "dec":
            nova_pos = (pos - deslocamento) % 26
        else:
            print("Operação inválida. Use 'enc' ou 'dec'.")
            return
        
        resultado.append(chr(nova_pos + ord('A')))

    print("".join(resultado))

if __name__ == "__main__":
    main()