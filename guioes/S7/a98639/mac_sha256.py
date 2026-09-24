import sys
import os
from cryptography.hazmat.primitives import hashes

def main():
    if len(sys.argv) < 3:
        print("Uso:")
        print("  setup <fkey>")
        print("  mac <fich> <fkey>")
        print("  ver <fich> <fkey>")
        return

    op = sys.argv[1]

    if op == "setup":
        fkey = sys.argv[2]
        with open(fkey, "wb") as f:
            f.write(os.urandom(32))
        print(f"Chave de 32 bytes gerada em '{fkey}'.")

    elif op == "mac":
        fich = sys.argv[2]
        fkey = sys.argv[3]

        with open(fkey, "rb") as f: chave = f.read()
        with open(fich, "rb") as f: msg = f.read()

        digest = hashes.Hash(hashes.SHA256())
        digest.update(chave + msg)
        mac = digest.finalize()

        with open(fich + ".mac", "wb") as f:
            f.write(mac)
        print(f"MAC gerado em '{fich}.mac'.")

    elif op == "ver":
        fich = sys.argv[2]
        fkey = sys.argv[3]

        with open(fkey, "rb") as f: chave = f.read()
        with open(fich, "rb") as f: msg = f.read()
        
        try:
            with open(fich + ".mac", "rb") as f: mac_original = f.read()
        except FileNotFoundError:
            print("False")
            return

        digest = hashes.Hash(hashes.SHA256())
        digest.update(chave + msg)
        mac_calculado = digest.finalize()

        print(mac_calculado == mac_original)

if __name__ == "__main__":
    main()