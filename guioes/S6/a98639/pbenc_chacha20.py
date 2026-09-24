import sys
import os
import getpass
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def derive_key(password: bytes, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return kdf.derive(password)

def main():
    if len(sys.argv) != 3:
        print("Uso: python3 pbenc_chacha20.py <enc/dec> <fich>")
        return

    op = sys.argv[1]
    fich = sys.argv[2]
    
    password = getpass.getpass("Introduza a passphrase: ").encode()

    if op == "enc":
        with open(fich, "rb") as f: ptxt = f.read()

        salt = os.urandom(16)
        nonce = os.urandom(16)
        chave = derive_key(password, salt)

        algorithm = algorithms.ChaCha20(chave, nonce)
        cipher = Cipher(algorithm, mode=None)
        encryptor = cipher.encryptor()
        ctxt = encryptor.update(ptxt)

        with open(fich + ".enc", "wb") as f:
            f.write(salt + nonce + ctxt)

    elif op == "dec":
        with open(fich, "rb") as f:
            salt = f.read(16)
            nonce = f.read(16)
            ctxt = f.read()

        chave = derive_key(password, salt)

        algorithm = algorithms.ChaCha20(chave, nonce)
        cipher = Cipher(algorithm, mode=None)
        decryptor = cipher.decryptor()
        ptxt = decryptor.update(ctxt)

        with open(fich + ".dec", "wb") as f:
            f.write(ptxt)

if __name__ == "__main__":
    main()