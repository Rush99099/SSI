import sys

def main():

    criptograma = sys.argv[1].upper()

    palavras_alvo = [p.upper() for p in sys.argv[2:]]

    for i in range(26):
        chave_char = chr(i + ord('A'))
        
        #Tentar decifrar o criptograma
        texto_tentativa = []
        for char in criptograma:
            pos = ord(char) - ord('A')
            nova_pos = (pos - i) % 26
            texto_tentativa.append(chr(nova_pos + ord('A')))
        
        texto_decifrado = "".join(texto_tentativa)

        for palavra in palavras_alvo:
            if palavra in texto_decifrado:
                print(chave_char)
                print(texto_decifrado)
                return #Terminar no primeiro match

if __name__ == "__main__":
    main()