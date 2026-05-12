import typer
import ctypes
import subprocess
import sys
import getpass
from pathlib import Path

from dfds import ip, crypto, convert, timer, passwords, ports, wifi
from dfds.utils import check_windows, kill_untrusted_processes, disable_network, clear_clipboard, lock_workstation
from dfds.lock import generate_key, save_key_to_usb, save_backup, run_usb_lock

app = typer.Typer(help="dfds – security & utility toolkit")

@app.command("ip")
def cmd_ip(address: str = None):
    if address:
        ip.ip_info(address)
    else:
        ip.ip_info()

@app.command("btc")
def cmd_btc():
    crypto.show_crypto("btc")

@app.command("eth")
def cmd_eth():
    crypto.show_crypto("eth")

@app.command("convert")
def cmd_convert(amount: float, from_curr: str, to_curr: str):
    convert.convert_currency(amount, from_curr, to_curr)

@app.command("timer")
def cmd_timer():
    timer.run_timer()

@app.command("weather")
def cmd_weather(city: str = None):
    from dfds.weather import get_weather
    get_weather(city)

pass_app = typer.Typer(help="Manage encrypted passwords")

@pass_app.command("generate")
def pass_generate(service: str = None):
    passwords.cmd_pass_generate(service)

@pass_app.command("get")
def pass_get(key: str):
    passwords.cmd_pass_get(key)

@pass_app.command("list")
def pass_list():
    passwords.cmd_pass_list()

@pass_app.command("clear")
def pass_clear():
    passwords.cmd_pass_clear()

app.add_typer(pass_app, name="pass")

@app.command("port")
def cmd_port_list():
    if not check_windows():
        return
    ports.cmd_port_list()

@app.command("port-close")
def cmd_port_close(port: int):
    if not check_windows():
        return
    ports.cmd_port_close(port)

@app.command("port-clean")
def cmd_port_clean():
    if not check_windows():
        return
    ports.cmd_port_clean()

@app.command("wifi")
def cmd_wifi_list():
    if not check_windows():
        return
    wifi.cmd_wifi_list()

@app.command("wifi-remove")
def cmd_wifi_remove(ssid: str):
    if not check_windows():
        return
    wifi.cmd_wifi_remove(ssid)

@app.command("wifi-clean")
def cmd_wifi_clean():
    if not check_windows():
        return
    wifi.cmd_wifi_clean()

@app.command("lock")
def cmd_lock(usb: bool = False, usb_drive: str = None):
    if not check_windows():
        return

    if usb:
        print("USB key mode enabled.")
        key = generate_key()
        if not usb_drive:
            usb_drive = input("Enter USB drive letter (e.g., D: or D:\\ ): ").strip()
            if not usb_drive.endswith(':\\'):
                usb_drive = usb_drive.rstrip('\\') + ':\\'
        try:
            save_key_to_usb(key, usb_drive)
        except Exception as e:
            print(f"Cannot write to USB: {e}")
            return
        backup = getpass.getpass("Create rescue password (store it safely): ")
        confirm = getpass.getpass("Confirm rescue password: ")
        if backup != confirm:
            print("Passwords do not match.")
            return
        save_backup(key, backup)
        print("USB key saved. Now locking system with USB protection.")
        disable_network()
        kill_untrusted_processes()
        clear_clipboard()
        monitor_script = Path(__file__).parent / "lock" / "lock_screen.py"
        subprocess.Popen([sys.executable, str(monitor_script), key, backup])
        print("System locked. Insert USB key with dfds.key to unlock.")
    else:
        lock_system()

def lock_system():
    print("Locking system...")
    clear_clipboard()
    disable_network()
    kill_untrusted_processes()
    lock_workstation()
    print("System locked.")

if __name__ == "__main__":
    app()