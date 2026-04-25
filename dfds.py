
import os
import sys
import shutil
import ctypes
import subprocess
import requests
import json
import datetime
import time
import secrets
import string
import base64
import hashlib
from pathlib import Path
from getpass import getpass
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

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
PASSWORDS_FILE = PASSWORDS_DIR / 'passwords.enc'
SALT_FILE = PASSWORDS_DIR / '.salt'

COIN_ALIASES = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "биток": "bitcoin",
    "эфир": "ethereum",
}

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
        print(f"Программа успешно установлена в {target}")
        print("Теперь команда 'dfds' доступна из любой консоли.")
        return True
    except Exception as e:
        print(f"Ошибка установки: {e}")
        return False

def ensure_installed():
    if not is_installed():
        print("Программа не установлена в системный PATH.")
        if getattr(sys, 'frozen', False):
            if install_self():
                print("Установка завершена. Перезапустите консоль для применения изменений.")
            else:
                print("Не удалось установить программу автоматически.")
            input("Нажмите Enter для выхода...")
            sys.exit(0)
        else:
            print("Запустите 'python dfds.py --install' для установки (требуются права администратора).")
            sys.exit(1)

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
            print("Не удалось определить ваш публичный IP.")
            return
    try:
        url = f'http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,zip,lat,lon,isp,org,as,query,timezone'
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get('status') == 'fail':
            print(f"Ошибка: {data.get('message', 'неизвестная')}")
            return
        print(f"\nИнформация об IP: {data['query']}")
        print(f"Страна: {data.get('country', 'Н/Д')}")
        print(f"Регион: {data.get('regionName', 'Н/Д')}")
        print(f"Город: {data.get('city', 'Н/Д')}")
        print(f"Почтовый индекс: {data.get('zip', 'Н/Д')}")
        print(f"Координаты: {data.get('lat', 'Н/Д')}, {data.get('lon', 'Н/Д')}")
        print(f"Провайдер: {data.get('isp', 'Н/Д')}")
        print(f"Организация: {data.get('org', 'Н/Д')}")
        print(f"AS: {data.get('as', 'Н/Д')}")
        print(f"Часовой пояс: {data.get('timezone', 'Н/Д')}")
    except Exception as e:
        print(f"Ошибка получения IP-информации: {e}")

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
    coin_id = COIN_ALIASES.get(coin_input.lower(), coin_input.lower())
    usd, rub = get_crypto_price(coin_id)
    if usd is not None:
        print(f"\n{coin_id.upper()}:")
        print(f"  ${usd:,.2f} USD")
        print(f"  {rub:,.2f} RUB")
    else:
        print(f"Не удалось получить данные для {coin_input}")

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

def run_timer():
    print(" Секундомер запущен. Нажмите Ctrl+C для остановки.")
    start = time.time()
    try:
        while True:
            elapsed = time.time() - start
            sys.stdout.write(f"\rПрошло: {elapsed:.2f} секунд")
            sys.stdout.flush()
            time.sleep(0.1)
    except KeyboardInterrupt:
        elapsed = time.time() - start
        print(f"\nСекундомер остановлен. Прошло: {elapsed:.2f} секунд.")

def _derive_key(master_password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(master_password.encode()))

def _get_cipher(master_password: str):
    PASSWORDS_DIR.mkdir(parents=True, exist_ok=True)
    if not SALT_FILE.exists():
        salt = os.urandom(16)
        with open(SALT_FILE, 'wb') as f:
            f.write(salt)
    else:
        with open(SALT_FILE, 'rb') as f:
            salt = f.read()
    key = _derive_key(master_password, salt)
    return Fernet(key)

def _load_encrypted_data():
    if not PASSWORDS_FILE.exists():
        return {}
    with open(PASSWORDS_FILE, 'rb') as f:
        encrypted = f.read()
    return encrypted

def _save_encrypted_data(encrypted):
    with open(PASSWORDS_FILE, 'wb') as f:
        f.write(encrypted)

def init_master_password():
    print("Инициализация защищённого хранилища паролей.")
    master = getpass("Придумайте мастер-пароль (не будет отображаться): ")
    confirm = getpass("Повторите мастер-пароль: ")
    if master != confirm:
        print("Пароли не совпадают.")
        sys.exit(1)
    cipher = _get_cipher(master)
    empty_data = {}
    encrypted = cipher.encrypt(json.dumps(empty_data).encode('utf-8'))
    _save_encrypted_data(encrypted)
    print("Хранилище успешно создано.")
    print(f"Файл: {PASSWORDS_FILE}")

def load_passwords(master_password: str):
    encrypted = _load_encrypted_data()
    if not encrypted:
        return {}
    try:
        cipher = _get_cipher(master_password)
        decrypted = cipher.decrypt(encrypted)
        return json.loads(decrypted.decode('utf-8'))
    except InvalidToken:
        print("Неверный мастер-пароль или повреждён файл хранилища.")
        sys.exit(1)

def save_passwords(data, master_password: str):
    cipher = _get_cipher(master_password)
    encrypted = cipher.encrypt(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    _save_encrypted_data(encrypted)

def generate_password(length=16):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def cmd_pass(args):
    if not PASSWORDS_FILE.exists():
        print("Хранилище паролей не найдено.")
        init_master_password()
        return

    master = getpass("Введите мастер-пароль: ")
    passwords = load_passwords(master)

    if not args:
        max_num = 0
        for key in passwords:
            if key.isdigit():
                max_num = max(max_num, int(key))
        next_num = max_num + 1
        pwd = generate_password()
        passwords[str(next_num)] = pwd
        save_passwords(passwords, master)
        print(f"Сгенерирован пароль №{next_num}: {pwd}")
        print(f"(сохранён в {PASSWORDS_FILE})")
    elif len(args) == 1 and args[0] == "clear":
        confirm = input("Вы уверены, что хотите удалить ВСЕ пароли? (yes/no): ")
        if confirm.lower() == "yes":
            PASSWORDS_FILE.unlink(missing_ok=True)
            SALT_FILE.unlink(missing_ok=True)
            print("Все пароли удалены. Хранилище уничтожено.")
        else:
            print("Операция отменена.")
    elif len(args) == 1 and args[0].isdigit():
        num = args[0]
        if num in passwords:
            print(f"Пароль №{num}: {passwords[num]}")
        else:
            print(f"Пароль с номером {num} не найден.")
    else:
        service = args[0]
        if len(args) > 1 and args[1] == "--gen":
            pwd = generate_password()
            passwords[service] = pwd
            save_passwords(passwords, master)
            print(f"Сгенерирован пароль для '{service}': {pwd}")
        elif service in passwords:
            print(f"Пароль для {service}: {passwords[service]}")
        else:
            ans = input(f"Пароль для '{service}' не найден. Сгенерировать новый? (y/n): ")
            if ans.lower() == 'y':
                pwd = generate_password()
                passwords[service] = pwd
                save_passwords(passwords, master)
                print(f"Сгенерирован пароль для '{service}': {pwd}")
            else:
                print("Отмена.")

def cmd_get_password(service):
    if not PASSWORDS_FILE.exists():
        print("Хранилище не инициализировано. Сначала выполните 'dfds pass'.")
        return
    master = getpass("Введите мастер-пароль: ")
    passwords = load_passwords(master)
    if service in passwords:
        print(passwords[service])
    else:
        print(f"Пароль для '{service}' не найден.")

def print_help():
    help_text = """

  dfds <команда> [аргументы]

  ip [адрес]               – информация об IP (если без аргумента – ваш публичный IP)
  btc, eth                 – текущий курс Bitcoin или Ethereum в USD и RUB
  convert <сумма> <из> <в> – конвертация валют (например, dfds convert 100 USD RUB)
  timer                    – секундомер (остановка Ctrl+C)
  pass [сервис|номер]      – управление паролями (шифрованное хранилище)
  -p <сервис>              – быстрое получение пароля для сервиса (вывод только пароля)

  dfds ip
  dfds ip 8.8.8.8
  dfds btc
  dfds eth
  dfds convert 100 eur usd
  dfds timer
  dfds pass                     – сгенерировать новый пароль (с автонумерацией)
  dfds pass github.com          – показать пароль для github.com (если есть)
  dfds pass github.com --gen    – принудительно сгенерировать новый пароль
  dfds pass 1                   – показать пароль №1
  dfds pass clear               – удалить все пароли (с подтверждением)
  dfds -p github.com            – вывести только пароль (удобно для скриптов)
 
  dfds --install
  dfds --help | -h
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
            print("Установка возможна только из скомпилированного .exe файла")
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
    elif arg == "timer":
        run_timer()
    elif arg in COIN_ALIASES or arg in ("btc", "eth"):
        show_crypto(arg)
    elif arg == "convert":
        if len(sys.argv) == 5:
            try:
                amount = float(sys.argv[2])
                convert_currency(amount, sys.argv[3], sys.argv[4])
            except ValueError:
                print("Сумма должна быть числом.")
        else:
            print("Использование: dfds convert [сумма] [из] [в]")
    else:
        print(f"Неизвестная команда: {arg}")
        print("Введите 'dfds --help' для справки.")

if __name__ == "__main__":
    main()