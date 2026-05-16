import psutil
import platform
import datetime
import os

def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor
    return f"{bytes:.2f}PB{suffix}"

def get_sysinfo():
    uname = platform.uname()
    print("=" * 60)
    print("System Information")
    print("=" * 60)
    print(f"System: {uname.system}")
    print(f"Node Name: {uname.node}")
    print(f"Release: {uname.release}")
    print(f"Version: {uname.version}")
    print(f"Machine: {uname.machine}")
    print(f"Processor: {uname.processor}")
    print()

    print("=" * 60)
    print("CPU Information")
    print("=" * 60)
    print(f"Physical cores: {psutil.cpu_count(logical=False)}")
    print(f"Total cores: {psutil.cpu_count(logical=True)}")
    cpufreq = psutil.cpu_freq()
    if cpufreq:
        print(f"Max Frequency: {cpufreq.max:.2f} MHz")
        print(f"Min Frequency: {cpufreq.min:.2f} MHz")
        print(f"Current Frequency: {cpufreq.current:.2f} MHz")
    cpu_usage = psutil.cpu_percent(interval=1)
    print(f"CPU Usage: {cpu_usage}%")
    print()

    print("=" * 60)
    print("Memory Information")
    print("=" * 60)
    svmem = psutil.virtual_memory()
    print(f"Total: {get_size(svmem.total)}")
    print(f"Available: {get_size(svmem.available)}")
    print(f"Used: {get_size(svmem.used)}")
    print(f"Percentage: {svmem.percent}%")
    swap = psutil.swap_memory()
    print(f"Swap Total: {get_size(swap.total)}")
    print(f"Swap Used: {get_size(swap.used)}")
    print(f"Swap Free: {get_size(swap.free)}")
    print(f"Swap Percentage: {swap.percent}%")
    print()

    print("=" * 60)
    print("Disk Information")
    print("=" * 60)
    partitions = psutil.disk_partitions()
    for partition in partitions:
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            continue
        print(f"Device: {partition.device}")
        print(f"  Mountpoint: {partition.mountpoint}")
        print(f"  File system: {partition.fstype}")
        print(f"  Total: {get_size(partition_usage.total)}")
        print(f"  Used: {get_size(partition_usage.used)}")
        print(f"  Free: {get_size(partition_usage.free)}")
        print(f"  Percentage: {partition_usage.percent}%")
        print()
    disk_io = psutil.disk_io_counters()
    if disk_io:
        print(f"Total read: {get_size(disk_io.read_bytes)}")
        print(f"Total write: {get_size(disk_io.write_bytes)}")
        print()

    print("=" * 60)
    print("Network Information")
    print("=" * 60)
    if_addrs = psutil.net_if_addrs()
    for interface_name, interface_addresses in if_addrs.items():
        for address in interface_addresses:
            if str(address.family) == 'AddressFamily.AF_INET':
                print(f"Interface: {interface_name}")
                print(f"  IP Address: {address.address}")
                print(f"  Netmask: {address.netmask}")
                print(f"  Broadcast: {address.broadcast}")
                print()
    net_io = psutil.net_io_counters()
    print(f"Total Bytes Sent: {get_size(net_io.bytes_sent)}")
    print(f"Total Bytes Received: {get_size(net_io.bytes_recv)}")
    print()

    print("=" * 60)
    print("System Uptime")
    print("=" * 60)
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    now = datetime.datetime.now()
    uptime = now - boot_time
    print(f"Boot Time: {boot_time}")
    print(f"Uptime: {uptime}")