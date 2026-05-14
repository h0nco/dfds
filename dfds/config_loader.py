import os
import yaml
from pathlib import Path

DEFAULT_CONFIG = {
    "whitelist_ports": [80,443,22,3389,21,25,53,110,143,993,995,8080,8443],
    "untrusted_processes": ["cmd.exe","powershell.exe","chrome.exe","firefox.exe","msedge.exe","telegram.exe","discord.exe","skype.exe"],
    "timeouts": {"netstat":5,"taskkill":5,"api_requests":10},
    "usb_key_filename": "dfds.key",
    "backup_dir": "%APPDATA%\\dfds",
    "log_file": "%APPDATA%\\dfds\\dfds.log",
    "log_level": "INFO",
    "log_to_console": False
}

def load_config():
    config_path = Path(os.getenv('APPDATA')) / 'dfds' / 'config.yaml'
    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(DEFAULT_CONFIG, f)
        return DEFAULT_CONFIG
    with open(config_path, 'r') as f:
        user_config = yaml.safe_load(f)
    config = DEFAULT_CONFIG.copy()
    config.update(user_config)
    config['backup_dir'] = os.path.expandvars(config['backup_dir'])
    config['log_file'] = os.path.expandvars(config['log_file'])
    return config