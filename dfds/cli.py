import typer
import ctypes
import subprocess
import sys
import getpass
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import signal
import shutil

from dfds import ip, crypto, convert, timer, passwords, ports, wifi
from dfds.utils import check_windows, kill_untrusted_processes, disable_network, clear_clipboard, lock_workstation
from dfds.lock import generate_key, save_key_to_usb, save_backup, run_usb_lock
from dfds.usb_detector import list_usb_drives
from dfds.config_loader import load_config
from dfds.logger_setup import logger

app = typer.Typer(help="dfds – security & utility toolkit")
config = load_config()
executor = ThreadPoolExecutor(max_workers=4)

def signal_handler(sig, frame):
    logger.info("Received termination signal, cleaning up")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

async def fetch_async(url, params=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=config['timeouts']['api_requests']) as resp:
            return await resp.json()

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
def cmd_lock(usb: bool = False):
    if not check_windows():
        return
    if usb:
        logger.info("USB lock mode initiated")
        key = generate_key()
        drives = list_usb_drives()
        if not drives:
            print("No USB drives found. Please insert a USB drive and try again.")
            logger.error("No USB drives available")
            return
        print("Available USB drives:")
        for i, d in enumerate(drives):
            print(f"{i+1}: {d}")
        choice = input("Select drive number: ")
        try:
            idx = int(choice) - 1
            usb_path = drives[idx]
        except (ValueError, IndexError):
            print("Invalid choice")
            return
        try:
            save_key_to_usb(key, usb_path)
        except Exception as e:
            print(f"Cannot write to USB: {e}")
            logger.error(f"USB write failed: {e}")
            return
        backup = getpass.getpass("Create rescue password: ")
        confirm = getpass.getpass("Confirm: ")
        if backup != confirm:
            print("Passwords do not match")
            return
        save_backup(key, backup)
        print("USB key saved. Locking with USB protection.")
        logger.info("USB key saved, locking system")
        disable_network()
        executor.submit(kill_untrusted_processes)
        clear_clipboard()
        monitor_script = Path(__file__).parent / "lock" / "usb_lock_screen_pyqt.py"
        subprocess.Popen([sys.executable, str(monitor_script), key, backup])
        print("System locked. Insert USB key to unlock.")
    else:
        lock_system()

def lock_system():
    logger.info("Normal lock initiated")
    clear_clipboard()
    disable_network()
    executor.submit(kill_untrusted_processes)
    lock_workstation()
    print("System locked.")

@app.command("uninstall")
def cmd_uninstall():
    confirm = input("This will delete all dfds data (passwords, config, logs). Continue? (yes/no): ")
    if confirm.lower() != "yes":
        print("Cancelled.")
        return
    appdata = Path(os.getenv('APPDATA')) / 'dfds'
    if appdata.exists():
        shutil.rmtree(appdata)
        print(f"Removed {appdata}")
    passwords_file = Path(os.getenv('APPDATA')) / 'dfds' / 'passwords.enc'
    if passwords_file.exists():
        passwords_file.unlink()
    log_file = Path(os.getenv('APPDATA')) / 'dfds' / 'dfds.log'
    if log_file.exists():
        log_file.unlink()
    print("dfds data removed. Program files remain. To fully remove, delete the dfds package folder.")
    logger.info("Uninstall completed")

if __name__ == "__main__":
    app()