import sys

def main():
    if len(sys.argv) != 5:
        print("Uso: python3 chacha20_int_attck.py <fctxt> <pos> <ptxtAtPos> <newPtxtAtPos>")
        return
    
    fctxt = sys.argv[1]
    pos = int(sys.argv[2])
    
    ptxtAtPos = sys.argv[3].encode()
    newPtxtAtPos = sys.argv[4].encode()
    
    if len(ptxtAtPos) != len(newPtxtAtPos):
        print("Erro: Os textos original e novo devem ter o mesmo tamanho.")
        return

    with open(fctxt, "rb") as f:
        data = bytearray(f.read())
        
    offset = 16 + pos
    
    for i in range(len(ptxtAtPos)):
        data[offset + i] = data[offset + i] ^ ptxtAtPos[i] ^ newPtxtAtPos[i]
        
    with open(fctxt + ".attck", "wb") as f:
        f.write(data)
        
    print(f"Ficheiro atacado gravado com sucesso em {fctxt}.attck")

if __name__ == "__main__":
    main()