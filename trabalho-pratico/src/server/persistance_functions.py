import json
from cryptography.hazmat.primitives import serialization
from common.crypto import generate_identity_keypair
import os

DB_FILE = "users.json"


def load_users():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(users, f, indent=4)


def load_or_create_ca():
    if os.path.exists("ca_private.pem"):
        with open("ca_private.pem", "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)
    else:
        private_key, public_key = generate_identity_keypair()
        with open("ca_private.pem", "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

    return private_key, private_key.public_key()

def export_ca_public_key(public_key):
    with open("ca_public.pem", "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

def load_certificates():
    try:
        with open("certificates.json", "r") as f:
            return json.load(f)
    except:
        return {}


def save_certificates(certs):
    with open("certificates.json", "w") as f:
        json.dump(certs, f)


def load_or_create_identity_keypair(username):
    priv_file = f"{username}_private.pem"

    if os.path.exists(priv_file):
        with open(priv_file, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)
    else:
        private_key, public_key = generate_identity_keypair()
        with open(priv_file, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        return private_key, private_key.public_key()

    return private_key, private_key.public_key()