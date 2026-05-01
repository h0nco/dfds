import ctypes
import subprocess
import sys

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