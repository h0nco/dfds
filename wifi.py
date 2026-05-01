import re
import subprocess
import sys

def _is_windows():
    return sys.platform == "win32"

def _get_wifi_profiles():
    out = subprocess.check_output('netsh wlan show profiles', shell=True, text=True, encoding='cp866', errors='ignore')
    profiles = re.findall(r':\s+(.+)$', out, re.MULTILINE)
    return [p.strip() for p in profiles if p.strip()]

def _get_profile_auth(ssid: str):
    try:
        out = subprocess.check_output(f'netsh wlan show profile name="{ssid}" key=clear', shell=True, text=True, encoding='cp866', errors='ignore')
        match = re.search(r'Authentication\s*:\s*(.+)', out, re.IGNORECASE)
        return match.group(1).strip() if match else "Unknown"
    except:
        return "Unknown"

def _get_current_ssid():
    out = subprocess.check_output('netsh wlan show interfaces', shell=True, text=True, encoding='cp866', errors='ignore')
    match = re.search(r'SSID\s*:\s*(.+)', out, re.IGNORECASE)
    return match.group(1).strip() if match else None

def cmd_wifi_list():
    if not _is_windows():
        print("Wi‑Fi commands are Windows‑only.")
        return
    profiles = _get_wifi_profiles()
    if not profiles:
        print("No saved Wi‑Fi networks.")
        return
    current = _get_current_ssid()
    print(f"{'SSID':<30} {'Auth':<20} Active")
    print("-" * 60)
    for ssid in profiles:
        auth = _get_profile_auth(ssid)
        active = "Yes" if current and current == ssid else ""
        print(f"{ssid[:30]:<30} {auth[:20]:<20} {active}")

def cmd_wifi_remove(ssid: str):
    if not _is_windows():
        print("Wi‑Fi commands are Windows‑only.")
        return
    current = _get_current_ssid()
    if current == ssid:
        print(f"Cannot delete currently active network '{ssid}'.")
        return
    confirm = input(f"Delete saved network '{ssid}'? (y/n): ")
    if confirm.lower() != 'y':
        print("Cancelled.")
        return
    subprocess.run(f'netsh wlan delete profile name="{ssid}"', check=True, shell=True)
    print(f"Network '{ssid}' deleted.")

def cmd_wifi_clean():
    if not _is_windows():
        print("Wi‑Fi commands are Windows‑only.")
        return
    profiles = _get_wifi_profiles()
    if not profiles:
        print("No saved Wi‑Fi networks.")
        return
    current = _get_current_ssid()
    to_delete = []
    for ssid in profiles:
        if current and ssid == current:
            continue
        auth = _get_profile_auth(ssid)
        if auth.lower() in ("open", "none", ""):
            to_delete.append(ssid)
    if not to_delete:
        print("No open networks to delete (current active network is protected).")
        return
    print("The following open networks will be deleted:")
    for ssid in to_delete:
        print(f"  {ssid}")
    confirm = input(f"Delete {len(to_delete)} networks? (y/n): ")
    if confirm.lower() != 'y':
        print("Cancelled.")
        return
    for ssid in to_delete:
        try:
            subprocess.run(f'netsh wlan delete profile name="{ssid}"', check=True, shell=True)
            print(f"Deleted: {ssid}")
        except subprocess.CalledProcessError as e:
            print(f"Error deleting {ssid}: {e}")