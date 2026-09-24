import sys
import random

def xor_bytes(bytes1, bytes2):
    return bytes(b1 ^ b2 for b1, b2 in zip(bytes1, bytes2))

def main():
    # Seguindo o exemplo do guião: sys.argv[1] = tamanho da chave, [2] = ficheiro .enc, [3:] = palavras
    if len(sys.argv) < 4:
        print("Uso: python3 bad_otp_attack.py <tamanho_chave> <ficheiro.enc> <palavra1> [palavra2 ...]")
        return

    n_bytes = int(sys.argv[1])
    ficheiro_enc = sys.argv[2]
    palavras_alvo = sys.argv[3:]

    # Ler o criptograma
    with open(ficheiro_enc, "rb") as f:
        criptograma = f.read()

    # O espaço da semente é de apenas 2 bytes. 256 * 256 = 65536 possibilidades
    for i in range(65536):
        # Converter o número i numa sequência de 2 bytes
        semente_tentativa = i.to_bytes(2, byteorder='big')
        
        # Inicializar o gerador com esta semente exata
        random.seed(semente_tentativa)
        chave_tentativa = random.randbytes(n_bytes)
        
        # Tentar decifrar
        texto_decifrado_bytes = xor_bytes(criptograma, chave_tentativa)
        
        # Tentar converter os bytes decifrados para string (ignorando erros de conversão de caracteres inválidos)
        try:
            texto_decifrado = texto_decifrado_bytes.decode('utf-8')
        except UnicodeDecodeError:
            continue  # Se os bytes não formam texto válido, não é esta a chave
            
        # Verificar se as palavras esperadas estão no texto decifrado
        match = True
        for palavra in palavras_alvo:
            if palavra not in texto_decifrado:
                match = False
                break
                
        if match:
            print("--- SEMENTE ENCONTRADA! ---")
            print(texto_decifrado.strip())
            return

    print("Não foi possível encontrar a mensagem.")

if __name__ == "__main__":
    main()