import sys
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms

def main():
    if len(sys.argv) < 3:
        print("Uso:")
        print("  setup <fkey>")
        print("  enc <fich> <fkey>")
        print("  dec <fich> <fkey>")
        return

    op = sys.argv[1]

    if op == "setup":
        fkey = sys.argv[2]
        chave = os.urandom(32)
        with open(fkey, "wb") as f:
            f.write(chave)
        print(f"Chave gerada e guardada em '{fkey}'.")

    elif op == "enc":
        if len(sys.argv) != 4:
            print("Uso: python3 cfich_chacha20.py enc <fich> <fkey>")
            return
        
        fich = sys.argv[2]
        fkey = sys.argv[3]

        with open(fkey, "rb") as f:
            chave = f.read()

        with open(fich, "rb") as f:
            ptxt = f.read()

        nonce = os.urandom(16)
        
        algorithm = algorithms.ChaCha20(chave, nonce)
        cipher = Cipher(algorithm, mode=None)
        encryptor = cipher.encryptor()
        
        ctxt = encryptor.update(ptxt)

        with open(fich + ".enc", "wb") as f:
            f.write(nonce + ctxt)
        
        print(f"Ficheiro cifrado com sucesso: {fich}.enc")

    elif op == "dec":
        if len(sys.argv) != 4:
            print("Uso: python3 cfich_chacha20.py dec <fich> <fkey>")
            return
            
        fich = sys.argv[2]
        fkey = sys.argv[3]

        with open(fkey, "rb") as f:
            chave = f.read()

        with open(fich, "rb") as f:
            #NONCE
            nonce = f.read(16)
            #Criptograma
            ctxt = f.read()

        algorithm = algorithms.ChaCha20(chave, nonce)
        cipher = Cipher(algorithm, mode=None)
        decryptor = cipher.decryptor()
        
        ptxt = decryptor.update(ctxt)

        with open(fich + ".dec", "wb") as f:
            f.write(ptxt)
            
        print(f"Ficheiro decifrado com sucesso: {fich}.dec")

    else:
        print("Operação inválida.")

if __name__ == "__main__":
    main()