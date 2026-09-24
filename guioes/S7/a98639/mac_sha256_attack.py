import sys
import hashpumpy

def main():
    if len(sys.argv) != 3:
        print("Uso: python3 mac_sha256_attack.py <fich> <ext>")
        return

    fich = sys.argv[1]
    ext = sys.argv[2].encode()

    with open(fich, "rb") as f: msg_original = f.read()
    with open(fich + ".mac", "rb") as f: mac_original_hex = f.read().hex()

    novo_mac_hex, mensagem_estendida = hashpumpy.hashpump(mac_original_hex, msg_original, ext, 32)

    with open(fich + ".ext", "wb") as f:
        f.write(mensagem_estendida)

    with open(fich + ".ext.mac", "wb") as f:
        f.write(bytes.fromhex(novo_mac_hex))

    print(f"Ataque concluído! Verifique com: python3 mac_sha256.py ver {fich}.ext <fkey>")

if __name__ == "__main__":
    main()