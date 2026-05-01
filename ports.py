import re
import subprocess

from dfds.config import WHITELIST_PORTS
from dfds.utils import ensure_admin

def _get_process_info(pid: int):
    try:
        cmd = f'tasklist /FI "PID eq {pid}" /FO CSV'
        out = subprocess.check_output(cmd, shell=True, text=True, encoding='cp866', errors='ignore')
        lines = out.strip().splitlines()
        if len(lines) >= 2:
            parts = lines[1].split('","')
            name = parts[0].strip('"')
            return name, ""
    except:
        pass
    return None, None

def _get_open_ports():
    ports = []
    out = subprocess.check_output('netstat -ano', shell=True, text=True, encoding='cp866', errors='ignore')
    for line in out.splitlines():
        m = re.match(r'(TCP|UDP)\s+\S+:(\d+)\s+\S+:\d+\s+(\S+)\s+(\d+)', line.strip())
        if m:
            proto, port, state, pid = m.group(1), int(m.group(2)), m.group(3), int(m.group(4))
            if proto == 'TCP' and state != 'LISTENING':
                continue
            if any(p['port'] == port and p['protocol'] == proto for p in ports):
                continue
            name, path = _get_process_info(pid)
            ports.append({'port': port, 'protocol': proto, 'pid': pid, 'name': name, 'path': path})
    return ports

def _is_system(pid, name, path):
    if pid in (0, 4):
        return True
    if name and name.lower() in ('svchost.exe', 'services.exe', 'lsass.exe', 'wininit.exe', 'csrss.exe', 'winlogon.exe'):
        return True
    if path and path.lower().startswith(('c:\\windows\\system32\\', 'c:\\windows\\syswow64\\')):
        return True
    return False

def cmd_port_list():
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
        print(f"{p['port']:<8} {p['protocol']:<8} {p['pid']:<8} {(p['name'] or '?')[:20]:<20} {(p['path'] or '?')[:50]:<50}{marker}")

def cmd_port_close(port: int):
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
    subprocess.run(f'taskkill /F /PID {target["pid"]}', check=True, shell=True)
    print(f"Process {target['name']} (PID {target['pid']}) terminated. Port {port} freed.")

def cmd_port_clean():
    ensure_admin("Cleaning non-standard ports requires administrator rights.")
    ports = _get_open_ports()
    to_close = [p for p in ports if p['port'] > 1024 and p['port'] not in WHITELIST_PORTS and not _is_system(p['pid'], p['name'], p['path'])]
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
    for p in to_close:
        try:
            subprocess.run(f'taskkill /F /PID {p["pid"]}', check=True, shell=True)
            print(f"Terminated {p['name']} (PID {p['pid']}) on port {p['port']}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to terminate PID {p['pid']}: {e}")