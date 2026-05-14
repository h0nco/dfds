import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from dfds.config_loader import load_config
from dfds.utils import ensure_admin, check_windows

config = load_config()
executor = ThreadPoolExecutor(max_workers=4)

def _find_system_tool(tool_name: str, fallback_path: str = None) -> str | None:
    path = shutil.which(tool_name)
    if path:
        return path
    if fallback_path and os.path.exists(fallback_path):
        return fallback_path
    return None

def _get_process_info(pid: int):
    try:
        cmd = [
            'powershell', '-Command',
            f'Get-Process -Id {pid} | Select-Object -ExpandProperty Name, Path'
        ]
        out = subprocess.check_output(cmd, shell=False, text=True, errors='ignore', timeout=5)
        lines = out.strip().splitlines()
        name = lines[0] if lines else "?"
        path = lines[1] if len(lines) > 1 else ""
        return name, path
    except subprocess.CalledProcessError:
        return "?", "?"
    except subprocess.TimeoutExpired:
        return "?", "?"
    except Exception:
        return "?", "?"

def _get_open_ports():
    netstat_path = _find_system_tool('netstat', r'C:\Windows\System32\netstat.exe')
    if not netstat_path:
        print("netstat not found. Cannot list ports.")
        return []
    try:
        out = subprocess.check_output(f'"{netstat_path}" -ano', shell=True, text=True, encoding='cp866', errors='ignore', timeout=config['timeouts']['netstat'])
    except subprocess.CalledProcessError as e:
        print(f"Failed to run netstat: {e}")
        return []
    except subprocess.TimeoutExpired:
        print("netstat timed out")
        return []
    ports = []
    for line in out.splitlines():
        m = re.match(r'(TCP|UDP)\s+\S+:(\d+)\s+\S+:\d+\s+(\S+)\s+(\d+)', line.strip())
        if m:
            proto, port, state, pid = m.group(1), int(m.group(2)), m.group(3), int(m.group(4))
            if proto == 'TCP' and state != 'LISTENING':
                continue
            if any(p['port'] == port and p['protocol'] == proto for p in ports):
                continue
            name, path = _get_process_info(pid)
            ports.append({
                'port': port,
                'protocol': proto,
                'pid': pid,
                'name': name or "?",
                'path': path or "?"
            })
    return ports

def _is_system(pid, name, path):
    if pid in (0, 4):
        return True
    if name.lower() in ('svchost.exe', 'services.exe', 'lsass.exe', 'wininit.exe', 'csrss.exe', 'winlogon.exe'):
        return True
    if path and path.lower().startswith(('c:\\windows\\system32\\', 'c:\\windows\\syswow64\\')):
        return True
    return False

def cmd_port_list():
    if not check_windows():
        return
    ports = _get_open_ports()
    if not ports:
        print("No open listening ports.")
        return
    print(f"{'Port':<8} {'Protocol':<8} {'PID':<8} {'Process':<20} {'Path':<50}")
    print("-" * 100)
    for p in ports:
        marker = ""
        if p['port'] > 1024:
            marker += " [non-standard]"
        if p['path'] and not p['path'].lower().startswith(('c:\\windows', 'c:\\program files')):
            marker += " [outside system dir]"
        print(f"{p['port']:<8} {p['protocol']:<8} {p['pid']:<8} {(p['name'])[:20]:<20} {(p['path'])[:50]:<50}{marker}")

def cmd_port_close(port: int):
    if not check_windows():
        return
    ensure_admin("Closing a port requires administrator rights.")
    ports = _get_open_ports()
    target = next((p for p in ports if p['port'] == port), None)
    if not target:
        print(f"Port {port} not found.")
        return
    print(f"Found process using port {port}:")
    print(f"  PID: {target['pid']}")
    print(f"  Process: {target['name']}")
    print(f"  Path: {target['path']}")
    if _is_system(target['pid'], target['name'], target['path']):
        print("This is a system process. Termination prohibited.")
        return
    confirm = input(f"Terminate {target['name']} (PID {target['pid']})? (y/n): ")
    if confirm.lower() != 'y':
        print("Cancelled.")
        return
    try:
        subprocess.run(f'taskkill /F /PID {target["pid"]}', check=True, shell=True, timeout=config['timeouts']['taskkill'])
        print(f"Process {target['name']} (PID {target['pid']}) terminated. Port {port} freed.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to terminate process: {e}")
    except subprocess.TimeoutExpired:
        print("Termination command timed out.")

def cmd_port_clean():
    if not check_windows():
        return
    ensure_admin("Cleaning non-standard ports requires administrator rights.")
    ports = _get_open_ports()
    whitelist = set(config['whitelist_ports'])
    to_close = [p for p in ports if p['port'] > 1024 and p['port'] not in whitelist and not _is_system(p['pid'], p['name'], p['path'])]
    if not to_close:
        print("No non-standard ports (except whitelist) to close.")
        return
    print("The following ports will be closed:")
    for p in to_close:
        print(f"  Port {p['port']} ({p['protocol']}) - {p['name']} (PID {p['pid']})")
    confirm = input(f"Terminate {len(to_close)} processes? (y/n): ")
    if confirm.lower() != 'y':
        print("Cancelled.")
        return
    def kill_one(p):
        try:
            subprocess.run(f'taskkill /F /PID {p["pid"]}', check=True, shell=True, timeout=config['timeouts']['taskkill'])
            print(f"Terminated {p['name']} (PID {p['pid']}) on port {p['port']}")
        except Exception as e:
            print(f"Failed to terminate PID {p['pid']}: {e}")
    with ThreadPoolExecutor(max_workers=4) as ex:
        ex.map(kill_one, to_close)