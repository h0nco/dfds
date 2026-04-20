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
import secrets
import string
import socket
from pathlib import Path
import xml.etree.ElementTree as ET
import msvcrt

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass
    os.system('chcp 65001 >nul')

TARGET_DIR = Path("C:/Windows/System32")
APP_NAME = "dfds.exe"
PASSWORDS_DIR = Path(os.getenv('APPDATA', Path.home() / '.dfds')) / 'dfds'
PASSWORDS_FILE = PASSWORDS_DIR / 'passwords.json'

COIN_ALIASES = {
    "btc": "bitcoin", "eth": "ethereum", "sol": "solana", "doge": "dogecoin",
    "ton": "toncoin", "xrp": "ripple", "ada": "cardano", "avax": "avalanche-2",
    "matic": "matic-network", "dot": "polkadot", "link": "chainlink",
    "биток": "bitcoin", "эфир": "ethereum", "солана": "solana", "доге": "dogecoin",
    "тон": "toncoin", "рипл": "ripple", "кардано": "cardano",
}

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
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣶⣶⣤⡀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⡿⠿⠿⢿⣿⣷⣄
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⡟⠁⠀⠀⠀⠀⠈⢻⣿⡆
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⣀⣀⣀⠀⠀⢸⣿⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⢸⣿⣿⣿⡇⠀⢸⣿⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⡄⠀⠈⠉⠁⠀⢠⣿⡿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⢿⣦⣤⣤⣤⣴⡿⠟⠁

⠀⠀⠀L A I N   I S   W A T C H I N G

⠀⠀⠀> connected
⠀⠀⠀> wired://active
⠀⠀⠀> identity: fragmented
⠀⠀⠀> reality.exe has stopped working

⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀⣀⡀
⠀⠀⠀⠀⠀⢠⣾⣿⣿⣿⣿⣿⣿⣷⡄
⠀⠀⠀⠀⠀⣿⣿⡿⠟⠛⠻⠿⢿⣿⣷
⠀⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀⠀⠀⣿⣿
⠀⠀⠀⠀⠀⣿⣿⠀⢀⣤⣤⡀⠀⣿⣿
⠀⠀⠀⠀⠀⣿⣿⠀⠈⠛⠛⠁⠀⣿⣿
⠀⠀⠀⠀⠀⠻⣿⣦⣄⣀⣀⣠⣴⡿⠟

⠀⠀⠀> who are you?
⠀⠀⠀> present day, present time
⠀⠀⠀> hahaha...
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
    ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, " ".join(sys.argv[1:]), None, 1)
    sys.exit()

def is_installed():
    return (TARGET_DIR / APP_NAME).exists()

def install_self():
    if not is_admin():
        print("Dlya ustanovki nuzhny prava administratora. Zaprashivayu...")
        run_as_admin()
        return False
    try:
        current_exe = Path(sys.executable)
        target = TARGET_DIR / APP_NAME
        shutil.copy2(current_exe, target)
        print(f"Programma uspeshno ustanovlena v {target}")
        print("Teper komanda 'dfds' dostupna iz lyuboy konsoli.")
        return True
    except Exception as e:
        print(f"Oshibka ustanovki: {e}")
        return False

def ensure_installed():
    if not is_installed():
        print("Programma ne ustanovlena. Vypolnyayu avtomaticheskuyu ustanovku...")
        if install_self():
            print("Ustanovka zavershena. Perezagrustite konsol dlya primeneniya izmeneniy.")
        else:
            print("Ne udalos ustanovit programmu avtomaticheski.")
        input("Nagmite Enter dlya vyhoda...")
        sys.exit(0)

def get_public_ip():
    try:
        resp = requests.get('https://api.ipify.org?format=json', timeout=10)
        return resp.json()['ip']
    except:
        return None

def ip_info(ip=None):
    if ip is None:
        ip = get_public_ip()
        if not ip:
            print("Ne udalos opredelit vash publichny IP.")
            return
    try:
        url = f'http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,zip,lat,lon,isp,org,as,query,timezone'
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get('status') == 'fail':
            print(f"Oshibka: {data.get('message', 'neizvestnaya')}")
            return
        print(f"\nInformatsiya ob IP: {data['query']}")
        print(f"Strana: {data.get('country', 'N/A')}")
        print(f"Region: {data.get('regionName', 'N/A')}")
        print(f"Gorod: {data.get('city', 'N/A')}")
        print(f"Pochtovyy indeks: {data.get('zip', 'N/A')}")
        print(f"Koordinaty: {data.get('lat', 'N/A')}, {data.get('lon', 'N/A')}")
        print(f"Provider: {data.get('isp', 'N/A')}")
        print(f"Organizatsiya: {data.get('org', 'N/A')}")
        print(f"AS: {data.get('as', 'N/A')}")
        print(f"Chasovoy poyas: {data.get('timezone', 'N/A')}")
    except Exception as e:
        print(f"Oshibka polucheniya IP-informatsii: {e}")

def init_passwords_storage():
    PASSWORDS_DIR.mkdir(parents=True, exist_ok=True)
    if not PASSWORDS_FILE.exists():
        with open(PASSWORDS_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f)

def load_passwords():
    init_passwords_storage()
    with open(PASSWORDS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_passwords(data):
    with open(PASSWORDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def generate_password(length=16):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def cmd_pass_clear():
    if PASSWORDS_FILE.exists():
        PASSWORDS_FILE.unlink()
        print("Vse paroli udaleny.")
    else:
        print("Fayl s parolyami ne suschestvuet.")

def cmd_pass(args):
    if not args:
        passwords = load_passwords()
        max_num = 0
        for key in passwords:
            if key.isdigit():
                max_num = max(max_num, int(key))
        next_num = max_num + 1
        pwd = generate_password()
        passwords[str(next_num)] = pwd
        save_passwords(passwords)
        print(f"Generirovan parol No{next_num}: {pwd}")
        print(f"(sohranyon v {PASSWORDS_FILE})")
    elif len(args) == 1 and args[0].isdigit():
        num = args[0]
        passwords = load_passwords()
        if num in passwords:
            print(f"Parol No{num}: {passwords[num]}")
        else:
            print(f"Parol s nomerom {num} ne nayden.")
    elif len(args) == 1 and args[0] == "clear":
        cmd_pass_clear()
    else:
        service = args[0]
        passwords = load_passwords()
        pwd = generate_password()
        passwords[service] = pwd
        save_passwords(passwords)
        print(f"Generirovan parol dlya servisa '{service}': {pwd}")

def cmd_get_password(service):
    passwords = load_passwords()
    if service in passwords:
        print(f"Parol dlya {service}: {passwords[service]}")
    else:
        print(f"Parol dlya {service} ne nayden.")

def show_time():
    now = datetime.datetime.now()
    print(f"\n{now.strftime('%A, %d %B %Y')}")
    print(f"{now.strftime('%H:%M:%S')}")
    print(f"Nomera nedeli: {now.isocalendar()[1]}")
    print(f"Chasovoy poyas: {time.tzname[0] if time.daylight else time.tzname[1]}, UTC{time.strftime('%z')}")
    print(f"Den v godu: {now.timetuple().tm_yday}")
    print(f"UNIX timestamp: {int(now.timestamp())}")

def run_timer():
    print("Sekundomer zapuschen. Nagmite Ctrl+C dlya ostanovki.")
    start = time.time()
    try:
        while True:
            elapsed = time.time() - start
            if elapsed < 0:
                elapsed = 0
            sys.stdout.write(f"\rProshlo: {elapsed:.2f} sekund")
            sys.stdout.flush()
            time.sleep(0.1)
    except KeyboardInterrupt:
        elapsed = time.time() - start
        if elapsed < 0:
            elapsed = 0
        print(f"\nSekundomer ostanovlen. Proshlo: {elapsed:.2f} sekund.")

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
            print(f"Gorod '{city}' ne nayden.")
            return
        loc = geo_data["results"][0]
        lat, lon = loc["latitude"], loc["longitude"]
        name = loc.get("name", city)
        country = loc.get("country", "")

        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=relativehumidity_2m&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max,uv_index_max,sunrise,sunset&timezone=auto"
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

        uv_index = "N/A"
        if "daily" in w_data and "uv_index_max" in w_data["daily"]:
            uv_index = w_data["daily"]["uv_index_max"][0]

        sunrise = sunset = "N/A"
        if "daily" in w_data:
            sunrise = w_data["daily"]["sunrise"][0].split('T')[1] if w_data["daily"]["sunrise"] else "N/A"
            sunset = w_data["daily"]["sunset"][0].split('T')[1] if w_data["daily"]["sunset"] else "N/A"

        desc = {0:"Yasno",1:"Preim. yasno",2:"Perem. oblachnost",3:"Pasmurno",
                45:"Tuman",48:"Izmoroz",51:"Moros",61:"Dojdd",71:"Sneg",
                80:"Liven",95:"Groza"}.get(code, "Neizvestno")

        print(f"\n{name}, {country}")
        print(get_weather_ascii(code))
        print(f"{desc}")
        print(f"Temperatura: {temp}C")
        print(f"Vlazhnost:   {humidity}%")
        print(f"Veter:       {wind} km/h, {wdir}°")
        print(f"UF-indeks:   {uv_index}")
        print(f"Voshod:      {sunrise} | Zakat: {sunset}")

        if "daily" in w_data:
            print("\nPrognoz na blizhayshie dni:")
            for i in range(min(3, len(w_data["daily"]["time"]))):
                day = w_data["daily"]["time"][i]
                max_t = w_data["daily"]["temperature_2m_max"][i]
                min_t = w_data["daily"]["temperature_2m_min"][i]
                precip = w_data["daily"]["precipitation_probability_max"][i]
                print(f"{day}: {min_t}C ~ {max_t}C, osadki: {precip}%")
    except Exception as e:
        print(f"Oshibka pogody: {e}")

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
        print(f"Oshibka polucheniya kursa {coin_id}: {e}")
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
            print("Ne udalos vypolnit konvertatsiyu.")
    except Exception as e:
        print(f"Oshibka konvertatsii: {e}")

def get_programming_fact():
    try:
        url = "https://programming-quotes-api.herokuapp.com/quotes/random"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        fact_en = data.get("en", "")
        author = data.get("author", "")
        translate_url = "https://api.mymemory.translated.net/get"
        params = {"q": fact_en, "langpair": "en|ru"}
        trans_resp = requests.get(translate_url, params=params, timeout=10)
        trans_data = trans_resp.json()
        fact_ru = trans_data.get("responseData", {}).get("translatedText", fact_en)
        return f"{fact_ru} (— {author})"
    except Exception as e:
        facts = [
            "Pervyy kompyuternyy virus poyavilsya v 1986 godu i nazyvalsya Brain.",
            "Yazyk Python nazvan ne v chest zmei, a v chest komediynogo shou 'Monty Python's Flying Circus'.",
            "Slovo 'bag' (bug) v programmirovanii poshlo ot realnogo nasekomogo, zastryavshego v rele kompyutera Mark II v 1947 godu.",
            "Pervaya kompyuternaya mysh byla sdelana iz dereva v 1964 godu Duglasom Engelbartom."
        ]
        return random.choice(facts)

def show_fact():
    print("\nFakt o programmirovanii:")
    print(get_programming_fact())

def show_system_info():
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq()
        mem = psutil.virtual_memory()
        disk_usage = psutil.disk_usage('/')
        net_io = psutil.net_io_counters()
        uptime_seconds = time.time() - psutil.boot_time()
        uptime_str = time.strftime('%H:%M:%S', time.gmtime(uptime_seconds))
        temps = ""
        if hasattr(psutil, "sensors_temperatures"):
            temps_dict = psutil.sensors_temperatures()
            if temps_dict:
                for name, entries in temps_dict.items():
                    for entry in entries:
                        temps += f"\n  {name}: {entry.current:.1f}C"

        print("\nInformatsiya o sisteme:")
        print(f"CPU: {cpu_percent}% | Chastota: {cpu_freq.current:.0f} MHz")
        print(f"Pamyat: {mem.percent}% (isp. {mem.used/1024**3:.2f} / {mem.total/1024**3:.2f} GB)")
        print(f"Disk C: {disk_usage.percent}% (svobodno {disk_usage.free/1024**3:.2f} GB)")
        print(f"Set: otpravleno {net_io.bytes_sent/1024**2:.2f} MB | polucheno {net_io.bytes_recv/1024**2:.2f} MB")
        print(f"Vremya raboty: {uptime_str}")
        if temps:
            print("Temperatury:" + temps)
        processes = sorted(psutil.process_iter(['name', 'cpu_percent']), key=lambda p: p.info['cpu_percent'] or 0, reverse=True)[:3]
        print("\nTop protsessov po CPU:")
        for p in processes:
            print(f"  {p.info['name']}: {p.info['cpu_percent']:.1f}%")
    except ImportError:
        print("Modul psutil ne ustanovlen. Vypolnite 'pip install psutil'")
    except Exception as e:
        print(f"Oshibka polucheniya sistemnoy informatsii: {e}")

def show_cat():
    print("Nagmite Ctrl+C dlya vyhoda.")
    try:
        while True:
            for frame in BIG_CAT_FRAMES:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(frame)
                time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nKotik ubezhal!")

def show_lain():
    print(LAIN_ART)

def show_pull(coin):
    try:
        coin_id = COIN_ALIASES.get(coin, coin)
        url = f"https://api.blockchair.com/{coin_id}/stats"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", {})
        volume_24h = data.get("volume_24h", 0)
        tx_count_24h = data.get("transactions_24h", 0)
        if coin_id == "bitcoin":
            volume_24h_usd = volume_24h / 1e8
        else:
            volume_24h_usd = volume_24h
        print(f"\nStatistika {coin_id.upper()} (otsenochno):")
        print(f"Za chas:      ${volume_24h_usd / 24:,.2f} | {tx_count_24h / 24:.0f} tx")
        print(f"Za den:     ${volume_24h_usd:,.2f} | {tx_count_24h:,} tx")
        print(f"Za nedelyu:   ${volume_24h_usd * 7:,.2f} | {tx_count_24h * 7:,} tx")
        print(f"Za mesyats:    ${volume_24h_usd * 30:,.2f} | {tx_count_24h * 30:,} tx")
    except Exception as e:
        print(f"Oshibka polucheniya dannyh pull: {e}")

def watch_price(coin, interval):
    coin_id = COIN_ALIASES.get(coin, coin)
    print(f"Monitoring {coin_id.upper()} kazhdye {interval} sek. Nagmite Ctrl+C dlya vyhoda.")
    try:
        while True:
            usd, rub = get_crypto_price(coin_id)
            if usd:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f"{datetime.datetime.now().strftime('%H:%M:%S')} - {coin_id.upper()}: ${usd:,.2f} USD / {rub:,.2f} RUB")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nMonitoring ostanovlen.")

def show_news():
    try:
        url = "https://lenta.ru/rss/news"
        resp = requests.get(url, timeout=10)
        resp.encoding = 'utf-8'
        xml_text = resp.text
        root = ET.fromstring(xml_text)
        items = root.findall(".//item")[:8]
        print("\nPoslednie novosti (Lenta.ru):")
        for i, item in enumerate(items, 1):
            title = item.find("title").text
            if title:
                title = title.strip()
                print(f"{i}. {title}")
    except Exception as e:
        print(f"Oshibka polucheniya novostey: {e}")

def show_moon():
    try:
        new_moon_epoch = datetime.date(2020, 1, 1)
        today = datetime.date.today()
        days_since = (today - new_moon_epoch).days
        cycle = 29.53058867
        phase_index = (days_since % cycle) / cycle
        phases = ["Novaya luna", "Molodaya luna", "Pervaya chetvert", "Pribyvayuschaya", "Polnaya luna", "Ubyvayuschaya", "Poslednyaya chetvert", "Staraya luna"]
        idx = int(phase_index * 8) % 8
        print(f"\nFaza Luny segodnya: {phases[idx]}")
        print(f"Osveschennost: {phase_index*100:.1f}%")
    except Exception as e:
        print(f"Oshibka: {e}")

def show_holiday(country="RU"):
    try:
        year = datetime.datetime.now().year
        url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country.upper()}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        holidays = resp.json()
        today = datetime.datetime.now().date()
        upcoming = None
        for h in holidays:
            h_date = datetime.datetime.strptime(h['date'], '%Y-%m-%d').date()
            if h_date >= today:
                upcoming = h
                break
        if upcoming:
            print(f"\nBlizhayshiy prazdnik v {country.upper()}:")
            print(f"{upcoming['name']} - {upcoming['date']}")
        else:
            print(f"Prazdnikov v {country.upper()} na etot god ne naydeno.")
    except Exception as e:
        print(f"Oshibka polucheniya prazdnikov: {e}")

def show_number_fact(number):
    try:
        url = f"http://numbersapi.com/{number}/math?json"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        fact = data.get('text', '')
        translate_url = "https://api.mymemory.translated.net/get"
        params = {"q": fact, "langpair": "en|ru"}
        trans_resp = requests.get(translate_url, params=params, timeout=10)
        trans_data = trans_resp.json()
        fact_ru = trans_data.get("responseData", {}).get("translatedText", fact)
        print(f"\nFact o chisle {number}:")
        print(fact_ru)
    except Exception as e:
        print(f"Oshibka: {e}")

def show_json(filepath):
    try:
        path = Path(filepath)
        if not path.exists():
            print(f"Fayl {filepath} ne nayden.")
            return
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        print("Oshibka: fayl ne soderzhit validnyy JSON.")
    except Exception as e:
        print(f"Oshibka: {e}")

def show_netstat():
    try:
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"Oshibka vypolneniya netstat: {e}")

def show_clock():
    print("Tsifrovye chasy. Nagmite Ctrl+C dlya vyhoda.")
    try:
        while True:
            now = datetime.datetime.now()
            sys.stdout.write(f"\r{now.strftime('%Y-%m-%d %H:%M:%S')}")
            sys.stdout.flush()
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nChasy ostanovleny.")

def show_sketch():
    print("\n=== RISOVALKA ===")
    print("Upravlenie: WASD - dvizhenie, Space - stavit simvol, C - ochistit, Q - vyhod")
    width, height = 40, 20
    canvas = [[' ' for _ in range(width)] for _ in range(height)]
    x, y = width//2, height//2
    running = True
    os.system('cls' if os.name == 'nt' else 'clear')
    while running:
        os.system('cls' if os.name == 'nt' else 'clear')
        for i in range(height):
            print(''.join(canvas[i]))
        print(f"\nKurser: ({x},{y})  Simvol: @")
        key = msvcrt.getch().decode('ascii').lower() if sys.platform == 'win32' else input()[0].lower()
        if key == 'w' and y > 0: y -= 1
        elif key == 's' and y < height-1: y += 1
        elif key == 'a' and x > 0: x -= 1
        elif key == 'd' and x < width-1: x += 1
        elif key == ' ':
            canvas[y][x] = '@'
        elif key == 'c':
            canvas = [[' ' for _ in range(width)] for _ in range(height)]
        elif key == 'q':
            running = False
    print("Vyhod iz risovalki.")

def show_halving():
    try:
        url = "https://blockchain.info/q/getblockcount"
        current_block = int(requests.get(url, timeout=10).text)
        blocks_to_halving = 210000 - (current_block % 210000)
        approx_days = blocks_to_halving * 10 / 1440  # 10 минут на блок
        next_halving_block = current_block + blocks_to_halving
        print(f"\nTekushchiy blok Bitcoin: {current_block}")
        print(f"Do sleduyuschego khalvinga: {blocks_to_halving} blokov")
        print(f"Eto primerno {approx_days:.1f} dney (~{approx_days/365:.2f} let)")
        print(f"Sleduyuschiy khalving proizoydet na bloke {next_halving_block}")
    except Exception as e:
        print(f"Oshibka polucheniya dannyh o khalvinge: {e}")

def print_help():
    help_text = r"""
+==============================================================================+
|                              DFDS - COMMAND HELP                            |
+==============================================================================+

+-----------------------------+------------------------------------------------+
| Category                    | Commands                                       |
+-----------------------------+------------------------------------------------+
| CRYPTO & FINANCE            | btc, eth, sol, doge, ton, xrp, ada, avax,    |
|                             | matic, dot, link, and aliases (bitok, efir)  |
|                             | watch [coin] [sec]  - price monitoring       |
|                             | pull [coin]         - transaction volume     |
|                             | convert <sum> <from> <to>                    |
|                             | halving              - days to next Bitcoin  |
|                             |                        halving               |
+-----------------------------+------------------------------------------------+
| WEATHER                     | <city name>  - detailed weather (3 days)     |
|                             | e.g.: dfds Moscow, dfds London               |
+-----------------------------+------------------------------------------------+
| SYSTEM & INFO               | sys         - system info (CPU, RAM, disk)   |
|                             | time        - current date/time              |
|                             | timer       - stopwatch (Ctrl+C to stop)     |
|                             | fact        - programming fact               |
|                             | news        - latest news (Lenta.ru)         |
|                             | netstat     - active network connections     |
|                             | clock       - digital clock (Ctrl+C exit)    |
+-----------------------------+------------------------------------------------+
| NETWORK                     | ip [addr]   - your IP or info about any IP   |
+-----------------------------+------------------------------------------------+
| PASSWORDS                   | pass                  - generate new password |
|                             | pass <num>            - show by number       |
|                             | pass <service>        - generate for service |
|                             | pass clear            - delete all passwords |
|                             | -p <service>          - show password        |
+-----------------------------+------------------------------------------------+
| ENTERTAINMENT               | cat         - animated cat                    |
|                             | lain        - Lain Iwakura ASCII art         |
|                             | moon        - current moon phase             |
|                             | holiday [country] - upcoming public holiday  |
|                             | numberfact <num> - interesting math fact     |
|                             | sketch      - simple drawing tool (WASM)     |
+-----------------------------+------------------------------------------------+
| UTILITIES                   | json <file> - pretty print JSON file         |
+-----------------------------+------------------------------------------------+
| INSTALL & HELP              | --install   - install to C:\Windows\System32 |
|                             | --help, -h  - this help                      |
+-----------------------------+------------------------------------------------+

Examples:
  dfds btc
  dfds watch eth 3
  dfds "New York"
  dfds pass google.com
  dfds -p google.com
  dfds numberfact 42
  dfds holiday US
  dfds netstat
  dfds clock
  dfds sketch
  dfds halving
"""
    print(help_text)

def main():
    if getattr(sys, 'frozen', False):
        ensure_installed()

    if len(sys.argv) == 1:
        print_help()
        return

    if sys.argv[1] == '-p' and len(sys.argv) >= 3:
        cmd_get_password(sys.argv[2])
        return

    arg = sys.argv[1].lower()

    if arg in ("--install",):
        if getattr(sys, 'frozen', False):
            install_self()
        else:
            print("Ustanovka vozmozhna tolko iz .exe fayla")
        return

    if arg in ("--help", "-h", "/?"):
        print_help()
        return

    if arg == "ip":
        if len(sys.argv) >= 3:
            ip_info(sys.argv[2])
        else:
            ip_info()
    elif arg == "pass":
        cmd_pass(sys.argv[2:])
    elif arg == "time":
        show_time()
    elif arg == "timer":
        run_timer()
    elif arg == "moon":
        show_moon()
    elif arg == "holiday":
        country = sys.argv[2] if len(sys.argv) >= 3 else "RU"
        show_holiday(country)
    elif arg == "numberfact":
        if len(sys.argv) >= 3:
            try:
                num = int(sys.argv[2])
                show_number_fact(num)
            except ValueError:
                print("Vvedite chislo.")
        else:
            print("Ispolzovanie: dfds numberfact <chislo>")
    elif arg == "json":
        if len(sys.argv) >= 3:
            show_json(sys.argv[2])
        else:
            print("Ispolzovanie: dfds json <put_k_faylu.json>")
    elif arg == "netstat":
        show_netstat()
    elif arg == "clock":
        show_clock()
    elif arg == "sketch":
        show_sketch()
    elif arg == "halving":
        show_halving()
    elif arg in COIN_ALIASES or arg in COIN_ALIASES.values():
        show_crypto(arg)
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
                print("Summa dolzhna byt chislom.")
        else:
            print("Ispolzovanie: dfds convert [summa] [iz] [v]")
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
        city = " ".join(sys.argv[1:])
        show_weather(city)

if __name__ == "__main__":
    main()