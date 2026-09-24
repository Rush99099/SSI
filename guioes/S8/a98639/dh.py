from multiprocessing import Process, Pipe
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization

P_HEX = (
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74"
    "020BBEA638139822514408798E3404DDEF951983CD3A431B302B0A6DF25F1437"
    "4FE1356D6D51C245E4858576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
    "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF05"
    "98DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F35620855288"
    "9ED5290770969660670C354E4ABC9804F1746008CA18217C32905E462E36CE3B"
    "E39E772C180E8603982783A2EC07A28FB5C55DF06F4C52C9DE2BCBF695581718"
    "3995497CEA956AE51502261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF"
)
P = int(P_HEX, 16)
G = 2

pn = dh.DHParameterNumbers(P, G)
parameters = pn.parameters()

def alice_process(conn):
    #Gerar chaves
    private_key = parameters.generate_private_key()
    public_key = private_key.public_key()

    alice_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    conn.send(alice_bytes)
    
    bob_bytes = conn.recv()
    bob_public_key = serialization.load_pem_public_key(bob_bytes)
    
    shared_key = private_key.exchange(bob_public_key)
    print(f"[Alice] Segredo K: {shared_key.hex()[:32]}...")

def bob_process(conn):
    #Gerar chaves
    private_key = parameters.generate_private_key()
    public_key = private_key.public_key()
    
    alice_bytes = conn.recv()
    alice_public_key = serialization.load_pem_public_key(alice_bytes)
    
    bob_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    conn.send(bob_bytes)
    
    shared_key = private_key.exchange(alice_public_key)
    print(f"[Bob]   Segredo K: {shared_key.hex()[:32]}...")

if __name__ == '__main__':
    parent_conn, child_conn = Pipe()
    p1 = Process(target=alice_process, args=(parent_conn,))
    p2 = Process(target=bob_process, args=(child_conn,))
    
    p1.start(); p2.start()
    p1.join(); p2.join()