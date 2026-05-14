import base64
import json
import os
import secrets
import string
from getpass import getpass
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

from dfds.config import CONFIG_DIR, PASSWORDS_FILE, SALT_FILE

def _derive_key(master_password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(master_password.encode()))

def _get_cipher(master_password: str) -> Fernet:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not SALT_FILE.exists():
        salt = os.urandom(16)
        SALT_FILE.write_bytes(salt)
    else:
        salt = SALT_FILE.read_bytes()
    key = _derive_key(master_password, salt)
    return Fernet(key)

def _load_encrypted() -> bytes:
    if not PASSWORDS_FILE.exists():
        return b''
    return PASSWORDS_FILE.read_bytes()

def _save_encrypted(encrypted: bytes):
    PASSWORDS_FILE.write_bytes(encrypted)

def init_storage(master: str):
    cipher = _get_cipher(master)
    encrypted = cipher.encrypt(json.dumps({}).encode('utf-8'))
    _save_encrypted(encrypted)
    print(f"Storage created at {PASSWORDS_FILE}")

def load_passwords(master: str) -> dict | None:
    encrypted = _load_encrypted()
    if not encrypted:
        return {}
    try:
        cipher = _get_cipher(master)
        decrypted = cipher.decrypt(encrypted)
        return json.loads(decrypted.decode('utf-8'))
    except InvalidToken:
        print("Invalid master password or corrupted storage.")
        return None
    except json.JSONDecodeError:
        print("Password storage is corrupted (invalid JSON).")
        return None
    except Exception as e:
        print(f"Unexpected error while loading passwords: {e}")
        return None

def save_passwords(data: dict, master: str):
    cipher = _get_cipher(master)
    encrypted = cipher.encrypt(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    _save_encrypted(encrypted)

def generate_password(length=16) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def cmd_pass_generate(service: str = None):
    if not PASSWORDS_FILE.exists():
        master = getpass("Create master password: ")
        confirm = getpass("Repeat master password: ")
        if master != confirm:
            print("Passwords do not match.")
            return
        init_storage(master)
    else:
        master = getpass("Enter master password: ")
    passwords = load_passwords(master)
    if passwords is None:
        return
    if service:
        pwd = generate_password()
        passwords[service] = pwd
        save_passwords(passwords, master)
        print(f"Generated password for '{service}': {pwd}")
    else:
        nums = [int(k) for k in passwords.keys() if k.isdigit()]
        next_num = max(nums) + 1 if nums else 1
        pwd = generate_password()
        passwords[str(next_num)] = pwd
        save_passwords(passwords, master)
        print(f"Generated password #{next_num}: {pwd}")

def cmd_pass_get(key: str):
    if not PASSWORDS_FILE.exists():
        print("No password storage. Run 'dfds pass generate' first.")
        return
    master = getpass("Enter master password: ")
    passwords = load_passwords(master)
    if passwords is None:
        return
    if key in passwords:
        print(passwords[key])
    else:
        print(f"Password for '{key}' not found.")

def cmd_pass_list():
    if not PASSWORDS_FILE.exists():
        print("No password storage.")
        return
    master = getpass("Enter master password: ")
    passwords = load_passwords(master)
    if passwords is None:
        return
    for key, pwd in passwords.items():
        print(f"{key}: {pwd}")

def cmd_pass_clear():
    confirm = input("Are you sure you want to delete ALL passwords? (yes/no): ")
    if confirm.lower() == "yes":
        PASSWORDS_FILE.unlink(missing_ok=True)
        SALT_FILE.unlink(missing_ok=True)
        print("All passwords deleted. Storage destroyed.")
    else:
        print("Operation cancelled.")