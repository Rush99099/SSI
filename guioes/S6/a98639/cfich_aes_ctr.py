import sys
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def main():
    if len(sys.argv) < 3:
        return
    op = sys.argv[1]

    if op == "setup":
        fkey = sys.argv[2]
        with open(fkey, "wb") as f:
            f.write(os.urandom(32))

    elif op == "enc":
        fich, fkey = sys.argv[2], sys.argv[3]
        with open(fkey, "rb") as f: chave = f.read()
        with open(fich, "rb") as f: ptxt = f.read()


        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(chave), modes.CTR(iv))
        encryptor = cipher.encryptor()
        ctxt = encryptor.update(ptxt_padded) + encryptor.finalize()

        with open(fich + ".enc", "wb") as f:
            f.write(iv + ctxt)

    elif op == "dec":
        fich, fkey = sys.argv[2], sys.argv[3]
        with open(fkey, "rb") as f: chave = f.read()
        with open(fich, "rb") as f:
            iv = f.read(16)
            ctxt = f.read()

        cipher = Cipher(algorithms.AES(chave), modes.CTR(iv))
        decryptor = cipher.decryptor()
        ptxt_padded = decryptor.update(ctxt) + decryptor.finalize()

        with open(fich + ".dec", "wb") as f:
            f.write(ptxt)

if __name__ == "__main__":
    main()