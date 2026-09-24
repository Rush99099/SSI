import sys
import os
import getpass
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
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
    if len(sys.argv) != 3: return
    op, fich = sys.argv[1], sys.argv[2]
    password = getpass.getpass("Introduza a passphrase: ").encode()

    if op == "enc":
        with open(fich, "rb") as f: ptxt = f.read()

        salt = os.urandom(16)
        nonce = os.urandom(12) 
        key = derive_key(password, salt)

        aesgcm = AESGCM(key)
        ctxt_with_tag = aesgcm.encrypt(nonce, ptxt, None) 

        with open(fich + ".enc", "wb") as f:
            f.write(salt + nonce + ctxt_with_tag)

    elif op == "dec":
        with open(fich, "rb") as f:
            salt = f.read(16)
            nonce = f.read(12)
            ctxt_with_tag = f.read()

        key = derive_key(password, salt)
        aesgcm = AESGCM(key)

        try:
            ptxt = aesgcm.decrypt(nonce, ctxt_with_tag, None)
        except Exception:
            print("ERRO: Integridade comprometida! Ficheiro alterado.")
            return

        with open(fich + ".dec", "wb") as f:
            f.write(ptxt)

if __name__ == "__main__":
    main()