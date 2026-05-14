import os
import json
from pathlib import Path

def get_appdata():
    return os.environ.get('APPDATA', str(Path.home() / 'AppData' / 'Roaming'))

DEFAULT_CONFIG = {
    "whitelist_ports": [80,443,22,3389,21,25,53,110,143,993,995,8080,8443],
    "untrusted_processes": ["cmd.exe","powershell.exe","chrome.exe","firefox.exe","msedge.exe","telegram.exe","discord.exe","skype.exe"],
    "timeouts": {"netstat":5,"taskkill":5,"api_requests":10},
    "usb_key_filename": "dfds.key",
    "backup_dir": get_appdata() + "\\dfds",
    "log_file": get_appdata() + "\\dfds\\dfds.log",
    "log_level": "INFO",
    "log_to_console": False
}

def load_config():
    config_dir = Path(get_appdata()) / 'dfds'
    config_path = config_dir / 'config.json'
    if not config_path.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        return DEFAULT_CONFIG.copy()
    with open(config_path, 'r') as f:
        user_config = json.load(f)
    config = DEFAULT_CONFIG.copy()
    config.update(user_config)
    return config