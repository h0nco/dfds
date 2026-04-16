#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import ctypes
import subprocess
import requests
import json
import datetime
import time
import random
import math
from pathlib import Path
import xml.etree.ElementTree as ET

# ---------- НАСТРОЙКИ ----------
TARGET_DIR = Path("C:/Windows/System32")
APP_NAME = "dfds.exe"
# --------------------------------

# ---------- КОНСТАНТЫ И ПСЕВДОНИМЫ ----------
COIN_ALIASES = {
    "btc": "bitcoin", "eth": "ethereum", "sol": "solana", "doge": "dogecoin",
    "ton": "toncoin", "xrp": "ripple", "ada": "cardano", "avax": "avalanche-2",
    "matic": "matic-network", "dot": "polkadot", "link": "chainlink",
    "биток": "bitcoin", "эфир": "ethereum", "солана": "solana", "доге": "dogecoin",
    "тон": "toncoin", "рипл": "ripple", "кардано": "cardano",
}
# ---------------------------------------------

# ---------- ASCII-арты ----------
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
BIG_CAT_FRAMES = [
    r"""
      /\_/\
     ( o.o )
      > ^ <
     /     \
    |       |
    """,
    r"""
      /\_/\
     ( -.- )
      > ~ <
     /     \
    |       |
    """,
    r"""
      /\_/\
     ( ^.^ )
      > o <
     /     \
    |       |
    """
]
LAIN_ART = r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣤⣤⣤⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣸⣿⣿⣿⣿⣿⣿⣿⣿⠁⠈⣿⠾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⣿⠃⣿⣿⣿⣿⢿⣿⣿⣿⣿⣿⣿⣿⡿⣧⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠸⣿⣿⣿⣿⣿⣻⣿⣼⠤⣤⠼⠵⣿⠟⠻⢿⢾⡿⠧⢽⣿⣿⣿⣿⡇⠙⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢿⣿⡟⣿⡏⢳⠴⣦⣤⣤⠔⠀⠀⠀⠀⠺⢿⣶⣶⡞⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣌⣇⠀⠀⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠰⠻⣿⣿⣿⣄⠀⠀⠀⠀⠀⠀⠒⢀⡔⠀⠀⠀⠀⢠⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⡿⢿⡿⢧⡀⠀⠀⠀⢀⣀⣀⡀⠀⠀⢀⡼⠛⣿⣿⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠁⠀⠁⢰⣿⣶⣦⣄⣀⠀⠀⡀⣠⣼⣾⣷⠄⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠴⣾⣿⣿⣿⣿⣿⣶⣯⣷⣿⣿⣿⣿⣿⡗⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣀⠔⣫⠦⣹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡷⣿⣿⡣⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⡠⠒⠉⠀⠀⢹⡜⡥⣚⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡙⣿⣿⠏⠀⠉⠢⢄⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⡸⠤⠤⢤⣀⣀⡸⢎⡵⣘⠮⣝⣿⣿⣿⣿⣿⣿⣿⣿⡿⢥⢛⣼⡏⠀⢀⣠⠴⠊⠙⢄⠀⠀⠀⠀
⠀⠀⢀⠎⠀⠰⣆⠀⠀⠈⠉⠚⡦⢷⢾⣔⣭⣿⣿⣿⣿⣿⣿⣟⣬⠷⢮⢾⠓⠊⠉⠀⠀⢠⠆⠘⡆⠀⠀⠀
⠀⠀⡎⠀⠀⡀⠘⢆⠀⠀⠀⠄⠻⣜⠲⣎⢼⣿⣿⣿⣿⣿⣿⣾⣥⢛⡜⡾⠀⢀⠐⠀⠀⡞⠀⠀⢷⠀⠀⠀
⠀⠀⡇⠀⠠⠀⠀⠈⢷⡀⠀⢀⠀⠹⡗⡜⣎⠶⣹⣿⣿⣿⣿⢎⡱⣋⡼⠃⠀⢀⠀⠀⣰⠃⢀⠠⢸⡄⠀⠀
⠀⠀⡇⠀⠀⠄⠂⠀⠀⢳⠀⠀⠀⠀⠘⢷⡘⢮⣽⣿⣿⣿⣿⣌⢧⡝⠁⠀⠀⠄⠀⢠⠏⠀⠀⡀⠀⡇⠀⠀
⠀⠀⡇⠀⠂⡀⠐⢀⠀⠘⡆⠀⠁⠀⠄⠀⠙⠛⠻⣿⣿⣿⠋⠛⠋⠀⠀⠈⠀⢀⠀⡞⠀⠀⠠⠀⠀⢳⠀⠀
⠀⠀⡇⠀⠠⠀⢠⡀⠀⠀⢻⠀⠀⠁⡀⠌⠀⠀⠀⢿⣿⡟⠀⠀⠠⠀⠐⠀⠁⠀⡼⠁⠀⠠⠁⠀⠀⣹⠀⠀
⠀⢠⠇⠀⠠⠀⠀⢣⡐⠀⠘⡇⠀⠐⠀⠀⠄⠀⠾⢿⣿⡇⢠⣤⠀⠀⠂⠀⡀⣸⠁⠀⠀⠂⠀⠁⠀⡜⠀⠀
⠀⢸⠀⠀⠐⢀⠀⠈⣧⠀⠀⢻⡀⠀⠐⠀⠠⢀⠀⢸⣿⡇⠈⠁⠀⢀⠂⠀⢠⠏⠀⠠⠐⠀⠈⢠⠆⣛⠀⠀
⠀⢸⠀⠈⢀⠀⠠⠀⠸⣆⠀⠈⣧⠐⠀⢈⠀⠀⡀⢼⣿⡇⣠⣀⠀⢀⠠⠀⡟⠀⠀⠠⠀⠠⢠⠎⡗⢸⠀⠀
⠀⣼⠀⢁⠂⡀⠂⠠⠀⢻⡄⠀⠸⡇⠀⠀⠀⠻⠟⣿⣿⣿⠈⠋⠀⠀⡀⣼⢡⡇⠀⠀⠀⢤⠏⢸⠃⢸⡀⠀
⠀⣯⠀⢂⠲⣄⠂⡁⠂⢈⣧⠀⢀⢻⡀⠂⢁⠠⢸⣿⣿⣿⣷⡀⣠⣁⠀⢻⣼⠀⠠⠀⣬⠏⢠⠏⠀⡈⡇⠀
⠀⡇⡐⢀⠂⠌⢷⠀⠡⢀⠘⣇⠠⢸⡇⠈⠄⠠⣹⣿⣿⣿⣿⣷⣉⠡⠀⢢⠏⠀⢠⡼⠃⢀⡞⢀⠐⡀⢷⠀
⠠⡗⡈⠷⣈⠰⢈⠻⣆⠂⠌⠹⣆⢼⢋⠐⡘⢛⣿⣿⣿⣿⣿⣿⣿⠠⠁⣾⠀⣼⠋⠄⡐⣸⠃⠄⠂⠌⢸⠀
⠀⣷⡈⡔⠩⠳⣦⢈⠹⢿⣬⡐⠙⣾⢀⠣⠠⢭⣿⣿⣿⣿⣿⣿⣿⠻⢃⣧⠟⢡⠈⡐⣰⠏⡐⣈⠐⡨⣼⡀
⠀⠸⡇⠬⣁⠣⡐⠢⢌⠢⡙⢿⣔⡹⣇⠴⠿⣿⣿⣿⣿⣿⣿⣿⣿⢡⣿⠁⢎⠠⡑⢠⡯⠐⡰⠀⠎⣡⣿⡇
⠀⠀⠹⣦⡑⠢⢅⠣⡘⢦⣕⡊⠩⣷⣿⡆⡱⣿⣿⣿⣿⣿⣿⣿⣿⠣⣼⠃⡌⢒⣨⣽⢀⠣⢐⠩⣰⣿⣿⡇
"""
# --------------------------------

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
        print(f"✅ Программа успешно установлена в {target}")
        print("Теперь команда 'dfds' доступна из любой консоли.")
        return True
    except Exception as e:
        print(f"❌ Ошибка установки: {e}")
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

def show_crypto(coin_input):
    coin_id = COIN_ALIASES.get(coin_input, coin_input)
    art = f"""
   ╔════════════════╗
   ║  {coin_id.upper():^12}  ║
   ╚════════════════╝
"""
    print(art)
    usd, rub = get_crypto_price(coin_id)
    if usd:
        print(f"1 {coin_id.upper()} = ${usd:,.4f} USD")
        print(f"1 {coin_id.upper()} = {rub:,.4f} RUB")

def get_fiat_rates():
    try:
        url = "https://api.exchangerate.host/latest?base=RUB&symbols=USD,CNY,UAH,EUR,KZT"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        rates = data.get("rates", {})
        result = {}
        if rates:
            rub_to_usd = rates.get("USD")
            if rub_to_usd:
                result["USD"] = 1 / rub_to_usd
            for curr in ["CNY", "UAH", "EUR", "KZT"]:
                rate = rates.get(curr)
                if rate and rub_to_usd:
                    result[curr] = rate / rub_to_usd
        return result
    except Exception as e:
        print(f"Ошибка получения курсов валют: {e}")
        return None

def show_fiat():
    rates = get_fiat_rates()
    if rates:
        print("\nКурсы валют к 1 USD (расчётные):")
        print(f"🇷🇺 RUB: {rates.get('USD', 'N/A'):.2f}" if rates.get('USD') else "🇷🇺 RUB: N/A")
        print(f"🇨🇳 CNY: {rates.get('CNY', 'N/A'):.2f}" if rates.get('CNY') else "🇨🇳 CNY: N/A")
        print(f"🇺🇦 UAH: {rates.get('UAH', 'N/A'):.2f}" if rates.get('UAH') else "🇺🇦 UAH: N/A")
        print(f"🇪🇺 EUR: {rates.get('EUR', 'N/A'):.2f}" if rates.get('EUR') else "🇪🇺 EUR: N/A")
        print(f"🇰🇿 KZT: {rates.get('KZT', 'N/A'):.2f}" if rates.get('KZT') else "🇰🇿 KZT: N/A")
    else:
        print("Не удалось получить курсы валют.")

def convert_currency(amount, from_curr, to_curr):
    try:
        url = f"https://api.exchangerate.host/convert?from={from_curr.upper()}&to={to_curr.upper()}&amount={amount}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        result = data.get("result")
        if result:
            print(f"{amount} {from_curr.upper()} = {result:.4f} {to_curr.upper()}")
        else:
            print("Не удалось выполнить конвертацию.")
    except Exception as e:
        print(f"Ошибка конвертации: {e}")

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

def get_random_fact_ru():
    try:
        url = "https://randstuff.ru/fact/generate/"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("fact", {}).get("text", "Не удалось получить факт.")
    except:
        facts = [
            "Самая высокая температура на Земле зафиксирована в Долине Смерти, США — +56,7°C.",
            "В среднем человек за жизнь проходит расстояние, равное трём оборотам вокруг Земли.",
            "Сердце синего кита бьётся всего 5-6 раз в минуту.",
            "Бананы слегка радиоактивны из-за содержания калия-40.",
            "В космосе нельзя плакать — слёзы не текут, а собираются в шарики."
        ]
        return random.choice(facts)

def show_fact():
    print("\nСлучайный факт:")
    print(get_random_fact_ru())

def show_system_info():
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        uptime_seconds = time.time() - psutil.boot_time()
        uptime_str = time.strftime('%H:%M:%S', time.gmtime(uptime_seconds))
        print("\nИнформация о системе:")
        print(f"Загрузка CPU: {cpu_percent}%")
        print(f"Использование памяти: {mem.percent}% ({mem.used / (1024**3):.2f} / {mem.total / (1024**3):.2f} ГБ)")
        print(f"Время работы: {uptime_str}")
    except ImportError:
        print("Модуль psutil не установлен. Выполните 'pip install psutil'")
    except Exception as e:
        print(f"Ошибка получения системной информации: {e}")

def show_cat():
    print("Нажмите Ctrl+C для выхода.")
    try:
        while True:
            for frame in BIG_CAT_FRAMES:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(frame)
                time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nКотик убежал!")

def show_lain():
    print(LAIN_ART)

def show_pull(coin, days):
    try:
        coin_id = COIN_ALIASES.get(coin, coin)
        url = f"https://api.blockchair.com/{coin_id}/stats"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", {})
        volume_24h = data.get("volume_24h", 0)
        tx_count_24h = data.get("transactions_24h", 0)
        volume_usd = volume_24h / 1e8 if coin_id == "bitcoin" else volume_24h
        print(f"\nСтатистика {coin_id.upper()} за последние 24 часа:")
        print(f"Объём транзакций: ${volume_usd:,.2f} USD")
        print(f"Количество транзакций: {tx_count_24h:,}")
        if days > 1:
            print(f"Приблизительный объём за {days} дней: ${volume_usd * days:,.2f} USD")
    except Exception as e:
        print(f"Ошибка получения данных pull: {e}")

def watch_price(coin, interval):
    coin_id = COIN_ALIASES.get(coin, coin)
    print(f"Мониторинг {coin_id.upper()} каждые {interval} сек. Нажмите Ctrl+C для выхода.")
    try:
        while True:
            usd, rub = get_crypto_price(coin_id)
            if usd:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f"{datetime.datetime.now().strftime('%H:%M:%S')} - {coin_id.upper()}: ${usd:,.2f} USD / {rub:,.2f} RUB")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nМониторинг остановлен.")

def show_news():
    """Показывает 8 последних новостей на русском языке с корректной кодировкой."""
    try:
        url = "https://www.interfax.ru/rss.asp"
        resp = requests.get(url, timeout=10)
        # Интерфакс отдаёт в windows-1251, конвертируем в UTF-8
        resp.encoding = 'windows-1251'
        xml_text = resp.text
        # Парсим XML
        root = ET.fromstring(xml_text)
        items = root.findall(".//item")[:8]  # 8 новостей
        print("\nПоследние новости (Интерфакс):")
        for i, item in enumerate(items, 1):
            title = item.find("title").text
            print(f"{i}. {title}")
    except Exception as e:
        print(f"Ошибка получения новостей: {e}")

def show_joke():
    """Показывает случайную шутку на русском языке."""
    try:
        # Используем API rzhunemogu (бесплатно, без ключа)
        url = "http://rzhunemogu.ru/RandJSON.aspx?CType=1"
        resp = requests.get(url, timeout=10)
        resp.encoding = 'windows-1251'
        # Ответ в формате JSONP, нужно вырезать JSON
        text = resp.text
        json_str = text[text.find('{'):text.rfind('}')+1]
        data = json.loads(json_str)
        joke = data.get("content", "Шутка не загрузилась :(")
        # Убираем HTML-теги
        import re
        joke = re.sub(r'<.*?>', '', joke)
        print("\nСлучайная шутка:")
        print(joke)
    except Exception as e:
        # Локальный запасной вариант
        jokes = [
            "Почему программисты путают Хэллоуин и Рождество? Потому что 31 OCT = 25 DEC.",
            "— Чем отличается программист от обычного человека? — Программист думает, что килограмм — это 1024 грамма.",
            "Жена отправляет мужа-программиста в магазин: — Купи батон, если будут яйца — возьми десяток. Муж возвращается с десятью батонами. — Ты зачем столько батонов купил? — Так яйца были!",
            "Программист ставит себе на тумбочку перед сном два стакана: один с водой — на случай, если ночью захочет пить, второй пустой — на случай, если не захочет.",
            "Идёт программист по улице, видит — лягушка. — Ты кто? — спрашивает программист. — Я Василиса Прекрасная! — отвечает лягушка. — А почему такая маленькая? — Так это я в масштабе 1:100."
        ]
        print("\nСлучайная шутка:")
        print(random.choice(jokes))

def print_help():
    print("""
Использование:
  dfds [команда] [аргументы]

Команды:
  btc, eth, sol, doge ...  - курс криптовалюты
  fiat                     - курсы фиатных валют (RUB, CNY, UAH, EUR, KZT)
  weather [город]          - погода в городе
  fact                     - случайный факт (на русском)
  sys                      - информация о системе
  cat                      - анимация большого котика
  lain                     - фраза Lain Iwakura
  convert [сумма] [из] [в] - конвертация валют (например, 100 usd rub)
  watch [монета] [сек]     - мониторинг цены (по умолчанию 5 сек)
  pull [монета] [дни]      - статистика транзакций за дни
  news                     - последние 8 новостей
  joke                     - случайная шутка (на русском)
  --install                - принудительная установка
  --help                   - эта справка
""")

def main():
    if getattr(sys, 'frozen', False):
        ensure_installed()

    if len(sys.argv) == 1:
        print_help()
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

    if arg in COIN_ALIASES or arg in COIN_ALIASES.values():
        show_crypto(arg)
    elif arg == "fiat":
        show_fiat()
    elif arg == "weather":
        city = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Москва"
        show_weather(city)
    elif arg == "fact":
        show_fact()
    elif arg == "sys":
        show_system_info()
    elif arg == "cat":
        show_cat()
    elif arg == "lain":
        show_lain()
    elif arg == "convert":
        if len(sys.argv) == 5:
            try:
                amount = float(sys.argv[2])
                convert_currency(amount, sys.argv[3], sys.argv[4])
            except ValueError:
                print("Сумма должна быть числом.")
        else:
            print("Использование: dfds convert [сумма] [из] [в]")
    elif arg == "watch":
        coin = sys.argv[2] if len(sys.argv) > 2 else "btc"
        interval = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        watch_price(coin, interval)
    elif arg == "pull":
        coin = sys.argv[2] if len(sys.argv) > 2 else "btc"
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        show_pull(coin, days)
    elif arg == "news":
        show_news()
    elif arg == "joke":
        show_joke()
    else:
        city = " ".join(sys.argv[1:])
        show_weather(city)

if __name__ == "__main__":
    main()