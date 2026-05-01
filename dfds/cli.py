import typer

from dfds import ip, crypto, convert, timer, passwords, ports, wifi
from dfds.utils import check_windows

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
def cmd_lock():
    if not check_windows():
        return
    import ctypes
    import subprocess
    print("Locking system...")
    try:
        ctypes.windll.user32.OpenClipboard(0)
        ctypes.windll.user32.EmptyClipboard()
        ctypes.windll.user32.CloseClipboard()
    except Exception as e:
        print(f"Clipboard error: {e}")
    try:
        subprocess.run('ipconfig /release', shell=True, check=False, capture_output=True)
        subprocess.run('netsh wlan disconnect', shell=True, check=False)
    except Exception as e:
        print(f"Network error: {e}")
    try:
        ctypes.windll.user32.LockWorkStation()
    except Exception as e:
        print(f"Lock error: {e}")
    print("System locked, network disconnected.")