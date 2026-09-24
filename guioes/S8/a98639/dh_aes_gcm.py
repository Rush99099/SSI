import os
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

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

def derivar_chave_aes(shared_key):
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake data'
    ).derive(shared_key)

def alice_process(conn):
    private_key = parameters.generate_private_key()
    alice_bytes = private_key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
    conn.send(alice_bytes)
    
    bob_bytes = conn.recv()
    bob_public_key = serialization.load_pem_public_key(bob_bytes)
    shared_key = private_key.exchange(bob_public_key)
    
    aes_key = derivar_chave_aes(shared_key)
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)
    ctxt = aesgcm.encrypt(nonce, b"Ola Bob, o acordo foi um sucesso!", None)
    
    conn.send((nonce, ctxt))

def bob_process(conn):
    private_key = parameters.generate_private_key()
    alice_bytes = conn.recv()
    alice_public_key = serialization.load_pem_public_key(alice_bytes)
    
    bob_bytes = private_key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
    conn.send(bob_bytes)
    
    shared_key = private_key.exchange(alice_public_key)
    
    aes_key = derivar_chave_aes(shared_key)
    aesgcm = AESGCM(aes_key)
    
    nonce, ctxt = conn.recv()
    ptxt = aesgcm.decrypt(nonce, ctxt, None)
    print(f"[Bob] Mensagem decifrada: {ptxt.decode()}")