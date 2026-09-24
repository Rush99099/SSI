import sys
import os
import getpass
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def derive_keys(password: bytes, salt: bytes) -> tuple:

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=64,
        salt=salt,
        iterations=480000,
    )
    key_material = kdf.derive(password)
    return key_material[:32], key_material[32:]

def main():
    if len(sys.argv) != 3: return
    op, fich = sys.argv[1], sys.argv[2]
    password = getpass.getpass("Introduza a passphrase: ").encode()

    if op == "enc":
        with open(fich, "rb") as f: ptxt = f.read()

        salt = os.urandom(16)
        nonce = os.urandom(16)
        key_enc, key_mac = derive_keys(password, salt)

        #AES-CTR
        cipher = Cipher(algorithms.AES(key_enc), modes.CTR(nonce))
        encryptor = cipher.encryptor()
        ctxt = encryptor.update(ptxt) + encryptor.finalize()

        h = hmac.HMAC(key_mac, hashes.SHA256())
        h.update(nonce + ctxt)
        mac_tag = h.finalize()

        with open(fich + ".enc", "wb") as f:
            f.write(salt + nonce + mac_tag + ctxt)

    elif op == "dec":
        with open(fich, "rb") as f:
            salt = f.read(16)
            nonce = f.read(16)
            mac_tag_original = f.read(32)
            ctxt = f.read()

        key_enc, key_mac = derive_keys(password, salt)

        h = hmac.HMAC(key_mac, hashes.SHA256())
        h.update(nonce + ctxt)
        try:
            h.verify(mac_tag_original)
        except Exception:
            print("ERRO: Integridade comprometida! Ficheiro alterado.")
            return

        cipher = Cipher(algorithms.AES(key_enc), modes.CTR(nonce))
        decryptor = cipher.decryptor()
        ptxt = decryptor.update(ctxt) + decryptor.finalize()

        with open(fich + ".dec", "wb") as f:
            f.write(ptxt)

if __name__ == "__main__":
    main()