import os
import sys
import shutil
import ctypes
import subprocess
import requests
import json
import datetime
from pathlib import Path

TARGET_DIR = Path("C:/Windows/System32")
APP_NAME = "dfds.exe"

BTC_ART = r"""
   ╔══════════════╗
   ║  ₿  Bitcoin  ║
   ╚══════════════╝
"""
ETH_ART = r"""
   ╔═══════════════╗
   ║  Ξ  Ethereum  ║
   ╚═══════════════╝
"""
SUN_ART = r"""
   \   /
    .-.
 ― (   ) ―
    `-'
   /   \
"""
CLOUD_ART = r"""
      .--.
   .-(    ).
  (___.__)__)
"""
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if getattr(sys, 'frozen', False):
        exe = sys.executable
    else:
        exe = sys.executable
        args = [exe] + sys.argv
    ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, " ".join(sys.argv[1:]), None, 1)
    sys.exit()

def is_installed():
    return (TARGET_DIR / APP_NAME).exists()

def install_self():
    if not is_admin():
        print("Для установки нужны права администратора. Запрашиваю...")
        run_as_admin()
        return False
    try:
        current_exe = Path(sys.executable)
        target = TARGET_DIR / APP_NAME
        shutil.copy2(current_exe, target)
        print(f" Программа успешно установлена в {target}")
        print("Теперь команда 'dfds' доступна из любой консоли.")
        return True
    except Exception as e:
        print(f" Ошибка установки: {e}")
        return False

def ensure_installed():
    if not is_installed():
        print("Программа не установлена. Выполняю автоматическую установку...")
        if install_self():
            print("Установка завершена. Перезапустите консоль для применения изменений.")
        else:
            print("Не удалось установить программу автоматически.")
        input("Нажмите Enter для выхода...")
        sys.exit(0)

def get_crypto_price(coin_id):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd,rub"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        usd = data[coin_id]["usd"]
        rub = data[coin_id]["rub"]
        return usd, rub
    except Exception as e:
        print(f"Ошибка получения курса {coin_id}: {e}")
        return None, None

def show_btc():
    print(BTC_ART)
    usd, rub = get_crypto_price("bitcoin")
    if usd:
        print(f"1 BTC = ${usd:,.2f} USD")
        print(f"1 BTC = {rub:,.2f} RUB")

def show_eth():
    print(ETH_ART)
    usd, rub = get_crypto_price("ethereum")
    if usd:
        print(f"1 ETH = ${usd:,.2f} USD")
        print(f"1 ETH = {rub:,.2f} RUB")

def get_weather_ascii(code):
    if code == 0:
        return SUN_ART
    elif code in (1, 2, 3):
        return CLOUD_ART
    elif code in (45, 48):
        return "   _ - _ - _ "
    elif 51 <= code <= 67 or 80 <= code <= 82:
        return "   ,,,,   "
    elif 71 <= code <= 77 or 85 <= code <= 86:
        return "   * * *   "
    elif 95 <= code <= 99:
        return "   ⚡ ⚡   "
    else:
        return CLOUD_ART

def show_weather(city):
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru&format=json"
        geo_resp = requests.get(geo_url, timeout=10)
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()
        if not geo_data.get("results"):
            print(f"Город '{city}' не найден.")
            return
        loc = geo_data["results"][0]
        lat, lon = loc["latitude"], loc["longitude"]
        name = loc.get("name", city)
        country = loc.get("country", "")

        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=relativehumidity_2m&timezone=auto"
        w_resp = requests.get(w_url, timeout=10)
        w_resp.raise_for_status()
        w_data = w_resp.json()
        cur = w_data["current_weather"]

        temp = cur["temperature"]
        wind = cur["windspeed"]
        wdir = cur["winddirection"]
        code = cur["weathercode"]

        humidity = "N/A"
        if "hourly" in w_data:
            now = datetime.datetime.now().strftime("%Y-%m-%dT%H:00")
            for i, t in enumerate(w_data["hourly"]["time"]):
                if t == now:
                    humidity = w_data["hourly"]["relativehumidity_2m"][i]
                    break

        desc = {0:"Ясно",1:"Преим. ясно",2:"Перем. облачность",3:"Пасмурно",
                45:"Туман",48:"Изморозь",51:"Морось",61:"Дождь",71:"Снег",
                80:"Ливень",95:"Гроза"}.get(code, "Неизвестно")

        print(f"\n{name}, {country}")
        print(get_weather_ascii(code))
        print(f"{desc}")
        print(f"Температура: {temp}°C")
        print(f"Влажность:   {humidity}%")
        print(f"Ветер:       {wind} км/ч, {wdir}°")
    except Exception as e:
        print(f"Ошибка погоды: {e}")

def print_help():
    print("Использование:")
    print("  dfds btc    - курс биткоина")
    print("  dfds eth    - курс эфириума")
    print("  dfds Город  - погода в городе (например: dfds Москва)")
    print("  dfds --install - принудительная установка в систему")
    print("  dfds --help - эта справка")

def main():
    if getattr(sys, 'frozen', False):
        ensure_installed()

    if len(sys.argv) == 1:
        print_help()
        if sys.stdin.isatty():
            input("\nНажмите Enter для выхода...")
        return

    arg = sys.argv[1].lower()

    if arg in ("--install",):
        if getattr(sys, 'frozen', False):
            install_self()
        else:
            print("Установка возможна только из .exe файла")
        return

    if arg in ("--help", "-h", "/?"):
        print_help()
        return

    if arg == "btc":
        show_btc()
    elif arg == "eth":
        show_eth()
    else:
        city = " ".join(sys.argv[1:])
        show_weather(city)

    if sys.stdin.isatty() and not sys.argv[1:]:
        input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()