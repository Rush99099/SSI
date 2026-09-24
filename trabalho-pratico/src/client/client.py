import socket
import threading
import json
import base64
from common.Datagram import Datagram
from common.crypto import generate_ephemeral_keypair, compute_shared_secret, derive_key, encrypt, decrypt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from server import persistance_functions
import ssl

HOST = '127.0.0.1'
PORT = 12345

# load CA public key
with open("ca_public.pem", "rb") as f:
    ca_public_key = serialization.load_pem_public_key(f.read())

# create client and TLS context
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
context.load_verify_locations("server_cert.pem")
context.check_hostname = False
raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client = context.wrap_socket(raw_socket, server_hostname="localhost")
client.connect((HOST, PORT))

# store own username 
my_username = None

# trusted peers: username -> {peer's public key, ephemeral private key, ephemeral public key}
trusted_peers = {} 

# session keys: username -> session key
session_keys = {}

# convert public key to bytes
def get_public_bytes(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )


# login phase (handled in main thread only)
buffer = ""
while True:
    try:
        data = client.recv(4096)
        if not data:
            print("Disconnected from server")
            exit()
    
        buffer += data.decode()

        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            if not line.strip():
                continue
            
            dgram = Datagram.decode(line.encode())

            if dgram.command == "request_username":
                username = input("Pick your username: ")
                my_username = username
                client.send(Datagram.login(username).encode())
            
            elif dgram.command == "login_ok":
                print(f"[OK] {dgram.content}")
                
                print("\n=== COMANDOS DISPONÍVEIS ===")
                print("/add <user>         - Adiciona um utilizador aos contactos")
                print("/remove <user>      - Remove um utilizador dos contactos")
                print("/list_contacts      - Mostra a tua lista de contactos")
                print("/session <user>     - Inicia uma sessão segura com um contacto")
                print("/msg <user> <texto> - Envia uma mensagem cifrada para a sessão")
                print("/quit ou /exit      - Sai da aplicação")
                print("============================\n")

                # client key pair
                private_key, public_key = persistance_functions.load_or_create_identity_keypair(username)

                # send public key to server
                public_bytes = get_public_bytes(public_key)
                public_key_b64 = base64.b64encode(public_bytes).decode() # raw bytes -> b64 bytes -> b64 string
                client.send(Datagram.register_key(public_key_b64).encode())

                break # sucessful login
            
            elif dgram.command == "error":
                print(f"[ERROR] {dgram.content}")
        else:
            continue
        break

    except Exception as e:
        print(f"Login error: {e}")
        client.close()
        exit()
            


# receive thread
def receive():
    buffer = ""

    while True:
        try:
            data = client.recv(4096)
            if not data:
                print("\nDisconnected from server")
                break

            buffer += data.decode()

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip():
                    continue
                dgram = Datagram.decode(line.encode())

                # receive message
                if dgram.command == "msg":
                    # check if sender has session key with receiver
                    sender = dgram.from_user
                    if sender not in session_keys:
                        # session may never have been created or may have expired
                        client.send(Datagram.no_session_inform(sender).encode())
                        continue

                    key = session_keys[sender]
                    data = base64.b64decode(dgram.content.encode()) # b64 string -> b64 bytes -> raw bytes
                    nonce = data[:12]
                    ciphertext = data[12:]

                    try:
                        plaintext = decrypt(key, nonce, ciphertext)
                    except Exception:
                        print("Decryption failed")
                        continue

                    print(f"\n[{sender}] {plaintext}")

                # success
                elif dgram.command == "ack":
                    print(f"\n[OK] {dgram.content}")

                # error
                elif dgram.command == "error":
                    print(f"\n[ERROR] {dgram.content}")
                
                # info
                elif dgram.command == "info":
                    print(f"\n[INFO] {dgram.content}")

                # list contacts (or users)
                elif dgram.command == "contacts_list":
                    print(f"\nContacts: {dgram.content}")

                # receive requested session
                elif dgram.command == "session_response":
                    peer = dgram.from_user

                    cert = json.loads(dgram.content)

                    username = cert.get("username")
                    public_key_b64 = cert.get("public_key")
                    signature_b64 = cert.get("signature")

                    data = (username + public_key_b64).encode()
                    signature = base64.b64decode(signature_b64.encode()) # b64 string -> b64 bytes -> raw bytes

                    if username != peer:
                        print("Certificate username mismatch!")
                        continue
                    
                    # verify signature (bind public key received to an identity via trust of CA)
                    try:
                        ca_public_key.verify(signature, data)
                    except Exception:
                        print("Invalid certificate!")
                        continue

                    # identity has been confirmed, store trusted peer and generate ephemeral key pair
                    eph_priv, eph_pub = generate_ephemeral_keypair()
                    
                    # trusted peer info
                    peer_info = {
                        "peer_public_key": public_key_b64, # peer's public key
                        "my_eph_priv": eph_priv, # ephemeral private key
                        "my_eph_pub": eph_pub # epehemeral public key
                    }

                    trusted_peers[peer] = peer_info
                    
                    eph_public_bytes = get_public_bytes(eph_pub)
                    eph_b64 = base64.b64encode(eph_public_bytes).decode() # raw bytes -> b64 bytes -> b64 string
                    data = (my_username + eph_b64).encode()

                    # sign with personal private key
                    signature = private_key.sign(data)

                    payload = {
                        "username": my_username,
                        "eph_public_key": eph_b64,
                        "signature": base64.b64encode(signature).decode() # raw bytes -> b64 bytes -> b64 string
                    }

                    client.send(Datagram.send_session_ephemeral(peer, payload).encode())
                
                elif dgram.command == "session_ephemeral":
                    payload = json.loads(dgram.content)

                    username = payload.get("username")
                    eph_b64 = payload.get("eph_public_key")
                    signature_b64 = payload.get("signature")

                    # verify we have trusted peer beforehand
                    eph_info = trusted_peers.get(username)

                    if not eph_info:
                        print("Missing identity key, cannot verify")
                        continue

                    public_key_b64 = eph_info.get("peer_public_key")
                    my_eph_priv = eph_info.get("my_eph_priv")

                    peer_public_bytes = base64.b64decode(public_key_b64.encode()) # b64 string -> b64 bytes -> raw bytes
                    peer_public_key = ed25519.Ed25519PublicKey.from_public_bytes(peer_public_bytes) # raw bytes -> public key

                    data = (username + eph_b64).encode()
                    signature = base64.b64decode(signature_b64.encode()) # b64 string -> b64 bytes -> raw bytes

                    # verify signature (bind ephemeral public key received to an identity who we trust via trust of CA)
                    try:
                        peer_public_key.verify(signature, data)
                    except:
                        print("Invalid ephemeral payload!")
                        continue

                    peer_eph_public_bytes = base64.b64decode(eph_b64.encode()) # b64 string -> b64 bytes -> raw bytes
                    shared_secret = compute_shared_secret(my_eph_priv,peer_eph_public_bytes)
                    session_key = derive_key(shared_secret)
                    # store session key
                    session_keys[username] = session_key
                    print(f"[SESSION] Secure session with {username} established")
                elif dgram.command == "no_session":
                    # in here peer is the original message receiver, it told server to inform original messsage sender (this client) that he doesn't have session with it
                    peer = dgram.from_user
                    if peer in session_keys:
                        del session_keys[peer]
                    print(f"\n[INFO] {peer} has no session with you. Run /session {peer}.")

                print("=> ", end="", flush=True)

        except Exception as e:
            print(f"Receive error: {e}")
            break


threading.Thread(target=receive, daemon=True).start()

# send loop
while True:
    user_input = input("=> ")

    if user_input.startswith("/msg "):
        try:
            _, to_user, content = user_input.split(" ", 2)

            # check if sender has session key with receiver
            if to_user not in session_keys:
                print("No secure session. Run /session <user>")
                continue
            
            key = session_keys[to_user]
            nonce, ciphertext = encrypt(key,content)
            payload = base64.b64encode(nonce + ciphertext).decode() # raw bytes -> b64 bytes -> b64 string
            client.send(Datagram.msg(None, to_user, payload).encode()) # sender should not be trusted on who he is based on from_user camp but rather on connection that server holds
        except ValueError:
            print("Correct use: /msg <username> <mensagem>")

    elif user_input.startswith("/add "):
        contact = user_input.split(" ", 1)[1]
        client.send(Datagram.add(contact).encode())

    elif user_input.startswith("/remove "):
        contact = user_input.split(" ", 1)[1]
        client.send(Datagram.remove(contact).encode())

    elif user_input == "/list_contacts":
        client.send(Datagram.list_contacts().encode())
    
    elif user_input.startswith("/session "):
        target_user = user_input.split(" ", 1)[1]

        client.send(Datagram.request_session(target_user).encode())

    elif user_input in ["/quit", "/exit"]:
        client.send(Datagram.quit().encode())
        client.close()
        break

    else:
        print("Comandos: /msg /add /remove /list_contacts /session /quit")
    
    