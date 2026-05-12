import os
import secrets
import json
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

KEY_FILENAME = "dfds.key"
BACKUP_FILE = Path(os.getenv('APPDATA')) / "dfds" / "usb_backup.json"

def generate_key() -> str:
    """Generate a 256-bit random key in hex."""
    return secrets.token_hex(32)

def save_key_to_usb(key: str, usb_path: str):
    """Save key to the root of a USB drive."""
    key_file = Path(usb_path) / KEY_FILENAME
    key_file.write_text(key)
    print(f"Key saved to {key_file}")

def verify_key(key: str, usb_path: str) -> bool:
    """Check if the USB drive contains the correct key file."""
    key_file = Path(usb_path) / KEY_FILENAME
    if not key_file.exists():
        return False
    return key_file.read_text().strip() == key

def save_backup(key: str, password: str):
    """Encrypt the key with a rescue password and store it."""
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200000,
    )
    enc_key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    cipher = Fernet(enc_key)
    encrypted = cipher.encrypt(key.encode())
    BACKUP_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "salt": salt.hex(),
        "data": encrypted.hex()
    }
    with open(BACKUP_FILE, "w") as f:
        json.dump(data, f)
    print(f"Backup saved. Remember your rescue password: {password}")

def load_backup(password: str) -> str | None:
    """Restore the key from backup using the rescue password."""
    if not BACKUP_FILE.exists():
        return None
    try:
        with open(BACKUP_FILE, "r") as f:
            data = json.load(f)
        salt = bytes.fromhex(data["salt"])
        encrypted = bytes.fromhex(data["data"])
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=200000,
        )
        enc_key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        cipher = Fernet(enc_key)
        key = cipher.decrypt(encrypted).decode()
        return key
    except Exception:
        return None