import os
from pathlib import Path
from dfds.config_loader import load_config

config = load_config()
USB_KEY_FILENAME = config['usb_key_filename']

def find_usb_with_key():
    for drive_letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        drive_path = f"{drive_letter}:\\"
        if os.path.exists(drive_path) and os.path.isdir(drive_path):
            key_file = Path(drive_path) / USB_KEY_FILENAME
            if key_file.exists():
                return drive_path
    return None

def list_usb_drives():
    drives = []
    for drive_letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        drive_path = f"{drive_letter}:\\"
        if os.path.exists(drive_path) and os.path.isdir(drive_path):
            drives.append(drive_path)
    return drives