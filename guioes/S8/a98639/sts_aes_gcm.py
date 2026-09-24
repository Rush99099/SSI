import os
from multiprocessing import Process, Pipe
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import dh, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
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

def mkpair(x, y):
    """produz uma byte-string contendo o tuplo '(x,y)'"""
    len_x = len(x)
    len_x_bytes = len_x.to_bytes(2, "little")
    return len_x_bytes + x + y

def unpair(xy):
    """extrai componentes de um par codificado com 'mkpair'"""
    len_x = int.from_bytes(xy[:2], "little")
    x = xy[2:len_x+2]
    y = xy[len_x+2:]
    return x, y

def derivar_chave_aes(shared_key):
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b'sts handshake').derive(shared_key)

def verificar_certificado_ca(cert, ca_cert):
    ca_pub_key = ca_cert.public_key()
    try:
        ca_pub_key.verify(
            cert.signature,
            cert.tbs_certificate_bytes,
            padding.PKCS1v15(),
            cert.signature_hash_algorithm
        )
        return True
    except Exception:
        return False

def alice_process(conn):
    with open("CA.crt", "rb") as f: ca_cert = x509.load_pem_x509_certificate(f.read())
    with open("Alice.key", "rb") as f: rsa_priv = serialization.load_pem_private_key(f.read(), password=None)
    with open("Alice.crt", "rb") as f: cert_bytes = f.read()

    dh_priv = parameters.generate_private_key()
    g_x_bytes = dh_priv.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)

    conn.send(g_x_bytes)

    bob_g_y_bytes, bob_sig_and_cert = unpair(conn.recv())
    bob_sig, bob_cert_bytes = unpair(bob_sig_and_cert)

    bob_dh_pub = serialization.load_pem_public_key(bob_g_y_bytes)
    bob_cert = x509.load_pem_x509_certificate(bob_cert_bytes)
    
    if not verificar_certificado_ca(bob_cert, ca_cert):
        print("[Alice] ERRO: Certificado do Bob inválido!")
        return
        
    bob_rsa_pub = bob_cert.public_key()
    try:
        bob_rsa_pub.verify(
            bob_sig,
            bob_g_y_bytes + g_x_bytes,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
    except Exception:
        print("[Alice] ERRO: Assinatura do Bob inválida!")
        return

    alice_sig = rsa_priv.sign(
        g_x_bytes + bob_g_y_bytes,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )
    conn.send(mkpair(alice_sig, cert_bytes))

    shared_key = dh_priv.exchange(bob_dh_pub)
    aes_key = derivar_chave_aes(shared_key)
    aesgcm = AESGCM(aes_key)
    
    nonce = os.urandom(12)
    ctxt = aesgcm.encrypt(nonce, b"Ola Bob! Sou eu, a Alice verdadeira.", None)
    conn.send((nonce, ctxt))
    print("[Alice] Acordo STS concluído com sucesso e mensagem enviada.")

def bob_process(conn):
    with open("CA.crt", "rb") as f: ca_cert = x509.load_pem_x509_certificate(f.read())
    with open("Bob.key", "rb") as f: rsa_priv = serialization.load_pem_private_key(f.read(), password=None)
    with open("Bob.crt", "rb") as f: cert_bytes = f.read()

    dh_priv = parameters.generate_private_key()
    g_y_bytes = dh_priv.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)

    alice_g_x_bytes = conn.recv()
    alice_dh_pub = serialization.load_pem_public_key(alice_g_x_bytes)

    bob_sig = rsa_priv.sign(
        g_y_bytes + alice_g_x_bytes,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )
    sig_and_cert = mkpair(bob_sig, cert_bytes)
    conn.send(mkpair(g_y_bytes, sig_and_cert))

    alice_sig, alice_cert_bytes = unpair(conn.recv())
    alice_cert = x509.load_pem_x509_certificate(alice_cert_bytes)

    if not verificar_certificado_ca(alice_cert, ca_cert):
        print("[Bob] ERRO: Certificado da Alice inválido!")
        return

    alice_rsa_pub = alice_cert.public_key()
    try:
        alice_rsa_pub.verify(
            alice_sig,
            alice_g_x_bytes + g_y_bytes,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
    except Exception:
        print("[Bob] ERRO: Assinatura da Alice inválida!")
        return

    shared_key = dh_priv.exchange(alice_dh_pub)
    aes_key = derivar_chave_aes(shared_key)
    aesgcm = AESGCM(aes_key)
    
    nonce, ctxt = conn.recv()
    ptxt = aesgcm.decrypt(nonce, ctxt, None)
    
    print("[Bob] Acordo STS concluído. Identidade da Alice confirmada.")
    print(f"[Bob] Mensagem decifrada: '{ptxt.decode()}'")

if __name__ == '__main__':
    parent_conn, child_conn = Pipe()
    p1 = Process(target=alice_process, args=(parent_conn,))
    p2 = Process(target=bob_process, args=(child_conn,))
    
    p1.start(); p2.start()
    p1.join(); p2.join()