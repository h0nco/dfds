import typer

from dfds import ip, crypto, convert, timer, passwords, ports, wifi
from dfds.utils import ensure_admin

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

@app.command("pass")
def cmd_pass():
    typer.echo("Use subcommands: generate, get, list, clear")
    typer.echo("  dfds pass generate [service]")
    typer.echo("  dfds pass get <key>")
    typer.echo("  dfds pass list")
    typer.echo("  dfds pass clear")

@app.command("pass-generate")
def cmd_pass_generate(service: str = None):
    passwords.cmd_pass_generate(service)

@app.command("pass-get")
def cmd_pass_get(key: str):
    passwords.cmd_pass_get(key)

@app.command("pass-list")
def cmd_pass_list():
    passwords.cmd_pass_list()

@app.command("pass-clear")
def cmd_pass_clear():
    passwords.cmd_pass_clear()

@app.command("port")
def cmd_port_list():
    ports.cmd_port_list()

@app.command("port-close")
def cmd_port_close(port: int):
    ports.cmd_port_close(port)

@app.command("port-clean")
def cmd_port_clean():
    ports.cmd_port_clean()

@app.command("wifi")
def cmd_wifi_list():
    wifi.cmd_wifi_list()

@app.command("wifi-remove")
def cmd_wifi_remove(ssid: str):
    wifi.cmd_wifi_remove(ssid)

@app.command("wifi-clean")
def cmd_wifi_clean():
    wifi.cmd_wifi_clean()

@app.command("lock")
def cmd_lock():
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

@app.command("crypto")
def cmd_crypto(coin: str):
    if coin.lower() in ("btc", "bitcoin"):
        crypto.show_crypto("btc")
    elif coin.lower() in ("eth", "ethereum"):
        crypto.show_crypto("eth")
    else:
        print("Supported: btc, eth")