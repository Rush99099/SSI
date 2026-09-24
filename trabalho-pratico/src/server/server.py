import socket
import threading
from common.Datagram import Datagram
from . import persistance_functions
import json
import base64
from cryptography.hazmat.primitives.asymmetric import ed25519
import ssl


HOST = '127.0.0.1'
PORT = 12345


# persisted users (username and contacts list)
users = persistance_functions.load_users()

# active clients: username -> connection 
clients = {}

# certificates: username -> certificates
certificates = persistance_functions.load_certificates()

# thread safety
clients_lock = threading.Lock()
users_lock = threading.Lock()
certificates_lock = threading.Lock()

# CA(central authority) key pair
ca_private_key, ca_public_key = persistance_functions.load_or_create_ca()
# export CA public key for it's distribution
persistance_functions.export_ca_public_key(ca_public_key)

# handle client
def handle_client(conn, addr):
    print(f"Client {addr} connected")
    buffer = ""


    # request username 
    while True:
        conn.send(Datagram.request_username().encode())

        data = conn.recv(4096)
        if not data:
            break
        
        buffer += data.decode()

        
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            if not line.strip():
                continue

            datagram = Datagram.decode(line.encode())

            if datagram.command != "login" or not datagram.content:
                conn.send(Datagram.error("Expected login").encode())
                continue

            username = datagram.content

            with clients_lock:
                if username in clients:
                    conn.send(Datagram.error("Username already online").encode())
                    continue
            
            with users_lock:
                if username not in users:
                    users[username] = {"contacts": []}
                    persistance_functions.save_users(users)

            # success -> break loop
            break
        else:
            continue
        break
    
    with clients_lock:
        clients[username] = conn
    print(f"{username} connected")
    conn.send(Datagram.login_ok(f"Welcome {username}").encode())

    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break

            buffer += data.decode()

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip():
                    continue

                datagram = Datagram.decode(line.encode())

                # message
                if datagram.command == "msg":
                    target = datagram.to_user

                    # cannot message yourself
                    if target == username:
                        conn.send(Datagram.error("You cannot message yourself").encode())
                        continue

                    # user must exist
                    with users_lock:
                        if target not in users:
                            conn.send(Datagram.error("User not found").encode())
                            continue

                        # must be in contacts
                        if target not in users[username]["contacts"]:
                            conn.send(Datagram.error("User not in your contacts").encode())
                            continue

                    # must be online
                    with clients_lock:
                        target_conn = clients.get(target)

                    if not target_conn:
                        conn.send(Datagram.error("User is offline").encode())
                        continue

                    # send message
                    msg = Datagram.msg(username, target, datagram.content)

                    try:
                        target_conn.send(msg.encode())
                    except:
                        conn.send(Datagram.error("Failed to deliver message").encode())
                
                # add contact 
                elif datagram.command == "add":
                    contact = datagram.contact

                    if contact == username:
                        conn.send(Datagram.error("You cannot add yourself").encode())
                        continue

                    with users_lock:
                        if contact not in users:
                            conn.send(Datagram.error("User does not exist").encode())
                        else:
                            if contact not in users[username]["contacts"]:
                                users[username]["contacts"].append(contact)
                                persistance_functions.save_users(users)
                                conn.send(Datagram.ack(f"{contact} added").encode())
                            else:
                                conn.send(Datagram.error(f"Already in contacts").encode())

                # remove contact 
                elif datagram.command == "remove":
                    contact = datagram.contact

                    with users_lock:
                        if contact in users[username]["contacts"]:
                            users[username]["contacts"].remove(contact)
                            persistance_functions.save_users(users)
                            conn.send(Datagram.ack(f"{contact} removed").encode())
                        else:
                            conn.send(Datagram.error("Not in contacts").encode())

                # list contacts
                elif datagram.command == "list_contacts":
                    with users_lock:
                        contacts = list(users[username]["contacts"])
                    conn.send(Datagram.contacts_list(", ".join(contacts)).encode())
                
                # register key 
                elif datagram.command == "register_key":
                    if username in certificates:
                        conn.send(Datagram.info("You are already certified").encode())
                        continue

                    public_key_b64 = datagram.content

                    # create data to sign
                    data = (username + public_key_b64).encode()
                    
                    # sign with CA private_key
                    signature = ca_private_key.sign(data)

                    cert = {
                        "username": username,
                        "public_key": public_key_b64,
                        "signature": base64.b64encode(signature).decode() # raw bytes -> b64 bytes -> b64 string
                    }

                    with certificates_lock:
                        certificates[username] = cert
                        persistance_functions.save_certificates(certificates)

                    conn.send(Datagram.ack("Certificate registered").encode())
                
                elif datagram.command == "request_session":
                    target = datagram.to_user

                    # cannot message yourself
                    if target == username:
                        conn.send(Datagram.error("You cannot message yourself").encode())
                        continue

                    # user must exist
                    with users_lock:
                        if target not in users:
                            conn.send(Datagram.error("User not found").encode())
                            continue

                        # must be in contacts
                        if target not in users[username]["contacts"]:
                            conn.send(Datagram.error("User not in your contacts").encode())
                            continue
                        
                    with clients_lock:
                        target_conn = clients.get(target)
                    
                    # must be online
                    if not target_conn:
                        conn.send(Datagram.error("User offline").encode())
                        continue

                    with certificates_lock:
                        sender_cert = certificates.get(username)
                        target_cert = certificates.get(target)

                    if not sender_cert or not target_cert:
                        conn.send(Datagram.error("Missing certificate").encode())
                        continue


                    # certificate objects to json formatted string
                    sender_cert_package = json.dumps(sender_cert)
                    target_cert_package = json.dumps(target_cert)

                    # server sends to sender target certificate
                    conn.send(Datagram.session_response(target, target_cert_package).encode())
                    # server sends to target certificate
                    target_conn.send(Datagram.session_response(username, sender_cert_package).encode())
                
                elif datagram.command == "no_session_inform":
                    # original message sender
                    target = datagram.to_user

                    with clients_lock:
                        sender_conn = clients.get(target)

                    if sender_conn:
                        # inform original message sender that original message receiver session has expired
                        sender_conn.send(Datagram.no_session(username).encode())

                elif datagram.command == "send_session_ephemeral":
                    target = datagram.to_user

                    with clients_lock:
                        target_conn = clients.get(target)
                    if not target_conn:
                        conn.send(Datagram.error("User offline").encode())
                        continue

                    try:
                        target_conn.send(Datagram.session_ephemeral(datagram.content).encode())
                    except:
                        conn.send(Datagram.error("Failed to deliver ephemeral").encode())

                # quit
                elif datagram.command == "quit":
                    break

                else:
                    conn.send(Datagram.error("Unknown command").encode())
    except Exception as e:
        print(f"Error: {e}")

    print(f"{username} disconnected")
    with clients_lock:
        if username in clients:
            del clients[username] # client not active anymore
    conn.close()    



# create server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()

# create TLS context
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

context.load_cert_chain(
    certfile="server_cert.pem",
    keyfile="server_key.pem"
)

print("Server (TLS) listening...")

# accept client connection
while True:
    conn, addr = server.accept()

    try:
        secure_conn = context.wrap_socket(conn, server_side=True)
        threading.Thread(
            target=handle_client,
            args=(secure_conn, addr),
            daemon=True
        ).start()
    except ssl.SSLError as e:
        print(f"TLS error: {e}")
        conn.close()