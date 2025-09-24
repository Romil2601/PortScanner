import socket
import threading
import time
import subprocess
import sys

# Function to install a package if missing
def install_package(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

# Try to import colorama, install if missing
try:
    from colorama import init, Fore, Style
except ModuleNotFoundError:
    print("colorama not found. Installing...")
    install_package("colorama")
    from colorama import init, Fore, Style

# Try to import tqdm, install if missing
try:
    from tqdm import tqdm
except ModuleNotFoundError:
    print("tqdm not found. Installing...")
    install_package("tqdm")
    from tqdm import tqdm

# Initialize colorama
init(autoreset=True)

# Predefined common services
services = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 135: "MS RPC", 1433: "MSSQL",
    161: "SNMP", 162: "SNMP Trap", 443: "HTTPS", 445: "SMB",
    3389: "RDP", 3306: "MySQL", 27017: "MongoDB", 8080: "HTTP Alt",
    5000: "UPnP", 8000: "HTTP", 9090: "HTTP", 10000: "Webmin"
}

# Input multiple targets
targets_input = input("Enter IP addresses separated by commas (e.g., 192.168.1.1,192.168.1.2): ")
targets = [t.strip() for t in targets_input.split(",")]

# Input port range
port_input = input("Enter port range (e.g., 1-1000) or leave blank for default ports: ")
if port_input:
    start_port, end_port = map(int, port_input.split("-"))
    ports = list(range(start_port, end_port + 1))
else:
    ports = list(services.keys())

# Lock for thread-safe print
print_lock = threading.Lock()

def scan_port(target, port, open_ports, progress):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex((target, port))
        with print_lock:
            if result == 0:
                service = services.get(port, "Unknown")
                print(f"{Fore.GREEN}[{target}] Port {port}: OPEN ✅ ({service})")
                open_ports.append(f"{target} - {port}: {service}")
            else:
                print(f"{Fore.RED}[{target}] Port {port}: CLOSED ❌")
    except:
        with print_lock:
            print(f"{Fore.YELLOW}[{target}] Port {port}: ERROR ⚠️")
    finally:
        sock.close()
        with print_lock:
            progress["scanned"] += 1

for target in targets:
    print(f"\nScanning {target}...\n")
    open_ports = []
    progress = {"scanned": 0}

    threads = []
    for port in ports:
        t = threading.Thread(target=scan_port, args=(target, port, open_ports, progress))
        threads.append(t)
        t.start()

    # Progress bar
    with tqdm(total=len(ports), desc=f"Scanning {target}", ncols=100) as pbar:
        last_count = 0
        while any(t.is_alive() for t in threads):
            scanned_now = progress["scanned"]
            pbar.update(scanned_now - last_count)
            last_count = scanned_now
            time.sleep(0.1)
        # Update remaining
        pbar.update(progress["scanned"] - last_count)

    for t in threads:
        t.join()

    # Save results to file
    if open_ports:
        filename = f"{target}_open_ports.txt"
        with open(filename, "w") as f:
            f.write(f"Open ports for {target}:\n")
            for port_info in open_ports:
                f.write(f"{port_info}\n")
        print(f"\nOpen ports for {target} saved to {filename}")
    else:
        print(f"\nNo open ports found for {target}")

print("\nAll scans completed.")