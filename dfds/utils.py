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

def clear_clipboard():
    try:
        ctypes.windll.user32.OpenClipboard(0)
        ctypes.windll.user32.EmptyClipboard()
        ctypes.windll.user32.CloseClipboard()
    except Exception as e:
        print(f"Clipboard error: {e}")

def disable_network():
    try:
        subprocess.run('ipconfig /release', shell=True, check=False, capture_output=True, timeout=5)
        subprocess.run('netsh wlan disconnect', shell=True, check=False, timeout=5)
    except Exception as e:
        print(f"Network error: {e}")

def kill_untrusted_processes():
    untrusted = [
        "cmd.exe", "powershell.exe", "explorer.exe", 
        "chrome.exe", "firefox.exe", "msedge.exe",
        "telegram.exe", "discord.exe", "skype.exe"
    ]
    for proc in untrusted:
        try:
            subprocess.run(f'taskkill /F /IM {proc}', shell=True, check=False, capture_output=True, timeout=2)
        except Exception:
            pass

def lock_workstation():
    """Lock the Windows workstation."""
    try:
        ctypes.windll.user32.LockWorkStation()
    except Exception as e:
        print(f"Lock error: {e}")