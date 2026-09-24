import sys
import itertools

def rank_shifts(fatia):
    shifts = []
    for shift in range(26):
        count = 0
        for c in fatia:
            #Decifrar este caracter com o deslocamento atual
            dec_c = chr((ord(c) - ord('A') - shift) % 26 + ord('A'))
            if dec_c in 'AEOS':
                count += 1
        shifts.append((count, shift))
    
    #Ordenar o deslocamento do mais provável para o menos
    shifts.sort(reverse=True, key=lambda x: x[0])
    
    return [shift for count, shift in shifts]

def main():
    if len(sys.argv) < 4:
        print("Uso: python3 vigenere_attack.py <tamanho_chave> <criptograma> <palavra1> [palavra2 ...]")
        return

    tamanho_chave = int(sys.argv[1])
    criptograma = sys.argv[2].upper()
    palavras_alvo = [p.upper() for p in sys.argv[3:]]

    #Separar o criptograma em "fatias"
    fatias = [criptograma[i::tamanho_chave] for i in range(tamanho_chave)]

    #Para cada fatia, obter os deslocamentos ordenados por probabilidade
    deslocamentos_provaveis_por_fatia = [rank_shifts(f) for f in fatias]

    #Combinações mais prováveis são as primeiras
    for shifts_tentativa in itertools.product(*deslocamentos_provaveis_por_fatia):
        
        chave_char = "".join([chr(s + ord('A')) for s in shifts_tentativa])

        #Tentar decifrar o criptograma com esta chave
        texto_tentativa = []
        for i, char in enumerate(criptograma):
            pos_char = ord(char) - ord('A')
            pos_chave = shifts_tentativa[i % tamanho_chave]
            nova_pos = (pos_char - pos_chave) % 26
            texto_tentativa.append(chr(nova_pos + ord('A')))

        texto_decifrado = "".join(texto_tentativa)

        for palavra in palavras_alvo:
            if palavra in texto_decifrado:
                print(chave_char)
                print(texto_decifrado)
                return

if __name__ == "__main__":
    main()