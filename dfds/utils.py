import ctypes
import subprocess
import sys
from pathlib import Path
from dfds.config_loader import load_config
from dfds.logger_setup import logger

config = load_config()

def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_as_admin():
    if getattr(sys, 'frozen', False):
        exe = sys.executable
    else:
        exe = sys.executable
    ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, " ".join(sys.argv[1:]), None, 1)
    sys.exit()

def ensure_admin(message: str):
    if not is_admin():
        print(message)
        run_as_admin()

def check_windows() -> bool:
    if sys.platform != "win32":
        print("This command is Windows‑only.")
        return False
    return True

def clear_clipboard():
    try:
        ctypes.windll.user32.OpenClipboard(0)
        ctypes.windll.user32.EmptyClipboard()
        ctypes.windll.user32.CloseClipboard()
        logger.debug("Clipboard cleared")
    except Exception as e:
        logger.warning(f"Clipboard clear failed: {e}")

def disable_network():
    try:
        subprocess.run('ipconfig /release', shell=True, check=False, capture_output=True, timeout=5)
        subprocess.run('netsh wlan disconnect', shell=True, check=False, timeout=5)
        logger.info("Network disabled (IP released, Wi-Fi disconnected)")
    except Exception as e:
        logger.error(f"Network disable error: {e}")

def kill_untrusted_processes():
    untrusted = config.get('untrusted_processes', [])
    for proc in untrusted:
        try:
            subprocess.run(f'taskkill /F /IM {proc}', shell=True, check=False, capture_output=True, timeout=2)
            logger.debug(f"Killed {proc}")
        except Exception:
            pass

def lock_workstation():
    try:
        ctypes.windll.user32.LockWorkStation()
        logger.info("Workstation locked")
    except Exception as e:
        logger.error(f"Lock error: {e}")