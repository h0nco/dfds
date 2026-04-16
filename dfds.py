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
import re
from pathlib import Path
import xml.etree.ElementTree as ET

# ---------- ПРИНУДИТЕЛЬНАЯ UTF-8 В КОНСОЛИ ----------
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass
    os.system('chcp 65001 >nul')
# ----------------------------------------------------

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
         ,--------------------------------------.
         |  Close the world,                     |
         |  Open the nExt                        |
         '--------------------------------------'
               \    ,__,
                \  (oo)____
                   (__)    )\
                      ||--|| *
         ╔══════════════════════════════════════╗
         ║        W I R E D   L A I N            ║
         ╚══════════════════════════════════════╝
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
    """Возвращает курсы основных валют к USD."""
    try:
        url = "https://api.exchangerate.host/latest?base=USD&symbols=RUB,CNY,UAH,EUR,KZT"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("rates", {})
    except Exception as e:
        print(f"Ошибка получения курсов валют: {e}")
        return None

def show_fiat():
    rates = get_fiat_rates()
    if rates:
        print("\nКурсы валют (за 1 USD):")
        print(f"🇷🇺 RUB: {rates.get('RUB', 'N/A'):.2f}")
        print(f"🇨🇳 CNY: {rates.get('CNY', 'N/A'):.2f}")
        print(f"🇺🇦 UAH: {rates.get('UAH', 'N/A'):.2f}")
        print(f"🇪🇺 EUR: {rates.get('EUR', 'N/A'):.2f}")
        print(f"🇰🇿 KZT: {rates.get('KZT', 'N/A'):.2f}")
    else:
        print("Не удалось получить курсы валют.")

def convert_currency(amount, from_curr, to_curr):
    try:
        url = f"https://api.exchangerate.host/convert?from={from_curr.upper()}&to={to_curr.upper()}&amount={amount}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        result = data.get("result")
        if result is not None:
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

def get_programming_fact():
    """Получает факт о программировании (англ) и переводит на русский через бесплатный API."""
    try:
        # Английский факт
        url = "https://programming-quotes-api.herokuapp.com/quotes/random"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        fact_en = data.get("en", "")
        author = data.get("author", "")
        # Бесплатный перевод через MyMemory (без ключа)
        translate_url = "https://api.mymemory.translated.net/get"
        params = {"q": fact_en, "langpair": "en|ru"}
        trans_resp = requests.get(translate_url, params=params, timeout=10)
        trans_data = trans_resp.json()
        fact_ru = trans_data.get("responseData", {}).get("translatedText", fact_en)
        return f"{fact_ru} (— {author})"
    except Exception as e:
        # Локальный резерв
        facts = [
            "Первый компьютерный вирус появился в 1986 году и назывался Brain.",
            "Язык Python назван не в честь змеи, а в честь комедийного шоу 'Monty Python's Flying Circus'.",
            "Слово 'баг' (bug) в программировании пошло от реального насекомого, застрявшего в реле компьютера Mark II в 1947 году.",
            "Первая компьютерная мышь была сделана из дерева в 1964 году Дугласом Энгельбартом."
        ]
        return random.choice(facts)

def show_fact():
    print("\n💡 Факт о программировании:")
    print(get_programming_fact())

def show_system_info():
    try:
        import psutil
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq()
        # Память
        mem = psutil.virtual_memory()
        # Диски
        disk_usage = psutil.disk_usage('/')
        # Сеть
        net_io = psutil.net_io_counters()
        # Время работы
        uptime_seconds = time.time() - psutil.boot_time()
        uptime_str = time.strftime('%H:%M:%S', time.gmtime(uptime_seconds))
        # Температуры (если доступны)
        temps = ""
        if hasattr(psutil, "sensors_temperatures"):
            temps_dict = psutil.sensors_temperatures()
            if temps_dict:
                for name, entries in temps_dict.items():
                    for entry in entries:
                        temps += f"\n  {name}: {entry.current:.1f}°C"

        print("\n📊 Информация о системе:")
        print(f"CPU: {cpu_percent}% | Частота: {cpu_freq.current:.0f} МГц")
        print(f"Память: {mem.percent}% (исп. {mem.used/1024**3:.2f} / {mem.total/1024**3:.2f} ГБ)")
        print(f"Диск C: {disk_usage.percent}% (свободно {disk_usage.free/1024**3:.2f} ГБ)")
        print(f"Сеть: отправлено {net_io.bytes_sent/1024**2:.2f} МБ | получено {net_io.bytes_recv/1024**2:.2f} МБ")
        print(f"Время работы: {uptime_str}")
        if temps:
            print("Температуры:" + temps)
        # Топ-3 процесса по CPU
        processes = sorted(psutil.process_iter(['name', 'cpu_percent']), key=lambda p: p.info['cpu_percent'] or 0, reverse=True)[:3]
        print("\nТоп процессов по CPU:")
        for p in processes:
            print(f"  {p.info['name']}: {p.info['cpu_percent']:.1f}%")
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

def show_pull(coin):
    """Показывает объём транзакций за час, день, неделю, месяц."""
    try:
        coin_id = COIN_ALIASES.get(coin, coin)
        # Blockchair возвращает данные за 24h, оценим остальное
        url = f"https://api.blockchair.com/{coin_id}/stats"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", {})
        volume_24h = data.get("volume_24h", 0)
        tx_count_24h = data.get("transactions_24h", 0)

        # Конвертация объёма в USD (для Bitcoin значение в сатоши)
        if coin_id == "bitcoin":
            volume_24h_usd = volume_24h / 1e8
        else:
            volume_24h_usd = volume_24h  # для остальных может быть уже в USD? зависит от API

        print(f"\n📈 Статистика {coin_id.upper()} (оценочно):")
        print(f"За час:      ${volume_24h_usd / 24:,.2f} | {tx_count_24h / 24:.0f} tx")
        print(f"За день:     ${volume_24h_usd:,.2f} | {tx_count_24h:,} tx")
        print(f"За неделю:   ${volume_24h_usd * 7:,.2f} | {tx_count_24h * 7:,} tx")
        print(f"За месяц:    ${volume_24h_usd * 30:,.2f} | {tx_count_24h * 30:,} tx")
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
    """Показывает 8 новостей с корректной кодировкой."""
    try:
        url = "https://www.interfax.ru/rss.asp"
        resp = requests.get(url, timeout=10)
        resp.encoding = 'windows-1251'  # Важно!
        xml_text = resp.text
        root = ET.fromstring(xml_text)
        items = root.findall(".//item")[:8]
        print("\n📰 Последние новости (Интерфакс):")
        for i, item in enumerate(items, 1):
            title = item.find("title").text
            # Очистка от лишних пробелов
            title = re.sub(r'\s+', ' ', title).strip()
            print(f"{i}. {title}")
    except Exception as e:
        print(f"Ошибка получения новостей: {e}")

def print_help():
    print("""
Использование:
  dfds [команда/город] [аргументы]

Команды:
  btc, eth, sol, ...   - курс криптовалюты (псевдонимы: биток, эфир и т.д.)
  fiat                 - курсы фиатных валют (RUB, CNY, UAH, EUR, KZT)
  Москва, Лондон ...   - погода в городе (просто введите название)
  fact                 - случайный факт о программировании
  sys                  - подробная информация о системе
  cat                  - анимация большого котика
  lain                 - ASCII-арт Lain Iwakura
  convert [сумма] [из] [в] - конвертация валют (например, 100 usd rub)
  watch [монета] [сек] - мониторинг цены (по умолчанию 5 сек)
  pull [монета]        - объём транзакций за час/день/неделю/месяц
  news                 - 8 свежих новостей
  --install            - принудительная установка в систему
  --help               - эта справка
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
        show_pull(coin)
    elif arg == "news":
        show_news()
    else:
        # Всё остальное считаем городом
        city = " ".join(sys.argv[1:])
        show_weather(city)

if __name__ == "__main__":
    main()