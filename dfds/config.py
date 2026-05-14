import os
from pathlib import Path

CONFIG_DIR = Path(os.getenv('APPDATA', Path.home() / '.dfds')) / 'dfds'
PASSWORDS_FILE = CONFIG_DIR / 'passwords.enc'
SALT_FILE = CONFIG_DIR / '.salt'
WHITELIST_PORTS = {80, 443, 22, 3389, 21, 25, 53, 110, 143, 993, 995, 8080, 8443}