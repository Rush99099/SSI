import sys
import random

def bad_prng(n):
    """ an INSECURE pseudo-random number generator"""
    random.seed(random.randbytes(2))
    return random.randbytes(n)
            
def xor_bytes(bytes1, bytes2):
    # Aplica a operação XOR byte a byte
    return bytes(b1 ^ b2 for b1, b2 in zip(bytes1, bytes2))

def main():
    if len(sys.argv) < 4:
        print("Uso:")
        print("  setup <n_bytes> <ficheiro_chave>")
        print("  enc <ficheiro_mensagem> <ficheiro_chave>")
        print("  dec <ficheiro_criptograma> <ficheiro_chave>")
        return

    op = sys.argv[1]

    if op == "setup":
        n_bytes = int(sys.argv[2])
        ficheiro_chave = sys.argv[3]
        chave = bad_prng(n_bytes)
        with open(ficheiro_chave, "wb") as f:
            f.write(chave)

    elif op == "enc":
        ficheiro_msg = sys.argv[2]
        ficheiro_chave = sys.argv[3]
        
        with open(ficheiro_msg, "rb") as f:
            msg = f.read()
        with open(ficheiro_chave, "rb") as f:
            chave = f.read()
            
        criptograma = xor_bytes(msg, chave)
        
        # O resultado da cifra será guardado num ficheiro com sufixo .enc
        with open(ficheiro_msg + ".enc", "wb") as f:
            f.write(criptograma)

    elif op == "dec":
        ficheiro_criptograma = sys.argv[2]
        ficheiro_chave = sys.argv[3]
        
        with open(ficheiro_criptograma, "rb") as f:
            cripto = f.read()
        with open(ficheiro_chave, "rb") as f:
            chave = f.read()
            
        msg_original = xor_bytes(cripto, chave)
        
        # O resultado da decifra será guardado num ficheiro com sufixo .dec
        with open(ficheiro_criptograma + ".dec", "wb") as f:
            f.write(msg_original)

if __name__ == "__main__":
    main()