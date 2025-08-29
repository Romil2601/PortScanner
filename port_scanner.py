import socket
import time

# Target can be localhost or another device on your network
target = input("Enter IP address to scan: ")
# Common ports or full range
ports = [
    21, 22, 23, 25, 53, 80, 443, 445, 8080,   # FTP, SSH, Telnet, HTTP, HTTPS, SMB, HTTP Alt
    135, 3389, 3306, 1433, 110, 161, 162, 514, # MS RPC, RDP, MySQL, MSSQL, POP3, SNMP, Syslog
    6660, 6661, 6662, 6663, 6664, 6665, 6666,  # IRC
    27017, 5000, 8000, 9090, 10000            # MongoDB, UPnP, HTTP, Webmin
]

print(f"\nScanning {target}...\n")

start_time = time.time()

for port in ports:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)  # Timeout in seconds
    
    result = sock.connect_ex((target, port))
    if result == 0:
        print(f"Port {port}: OPEN ✅")
    else:
        print(f"Port {port}: CLOSED ❌")
    
    sock.close()

end_time = time.time()
print(f"\nScan completed in {round(end_time - start_time, 2)} seconds.")