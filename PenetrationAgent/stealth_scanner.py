import subprocess
import time
import logging
import os
from typing import List, Optional, Dict
from datetime import datetime

class VulnerabilityScanner:
    def __init__(self):
        self.results_dir = "scans"
        self.logs_dir = "logs"
        self.scan_logs: Dict[str, List[str]] = {}
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.logs_dir, 'stealth_scan.log')),
                logging.StreamHandler()
            ]
        )

    def log_scan(self, ip: str, message: str) -> None:
        """Log a message for a specific IP scan"""
        if ip not in self.scan_logs:
            self.scan_logs[ip] = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.scan_logs[ip].append(log_message)
        logging.info(f"{ip}: {message}")

    def get_recent_logs(self, ip: str) -> List[str]:
        """Get recent logs for a specific IP"""
        return self.scan_logs.get(ip, [])

    def run_command(self, command: str) -> Optional[str]:
        """Run a command using subprocess and handle errors"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed with error: {e.stderr}"
            logging.error(error_msg)
            return None
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logging.error(error_msg)
            return None

    def perform_stealth_scan(self, ip: str) -> bool:
        """Perform a stealthy full-port TCP scan on the given IP"""
        self.log_scan(ip, f"Starting stealth full-port scan for {ip}")
        
        # Construct the nmap command with stealth parameters
        cmd = (
            f"nmap -sS -T1 -Pn --max-retries 2 "
            f"--scan-delay 500ms --source-port 53 "
            f"--min-rate 100 -p- {ip} "
            f"-oA {os.path.join(self.results_dir, f'{ip}_stealth_full')}"
        )
        
        # Run the scan
        output = self.run_command(cmd)
        
        if output:
            self.log_scan(ip, "Completed stealth scan successfully")
            return True
        else:
            self.log_scan(ip, "Failed to complete stealth scan")
            return False

    def scan_targets(self, ip_list: List[str]) -> Dict:
        """Scan multiple IP addresses"""
        results = {}
        for ip in ip_list:
            ip = ip.strip()
            if ip:
                results[ip] = {
                    'success': self.perform_stealth_scan(ip),
                    'logs': self.get_recent_logs(ip),
                    'timestamp': datetime.now().isoformat()
                }
                time.sleep(2)  # 2-second delay between scans
        return results

def main():
    """Main function to run stealth scans on a list of IPs"""
    scanner = VulnerabilityScanner()
    
    # Read IPs from file
    try:
        with open('target_ips.txt', 'r') as f:
            ip_list = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logging.error("target_ips.txt not found")
        return
    
    if not ip_list:
        logging.error("No IP addresses found in target_ips.txt")
        return
    
    logging.info(f"Starting stealth scanning session with {len(ip_list)} targets")
    results = scanner.scan_targets(ip_list)
    
    # Log completion
    logging.info("Completed all stealth scans")

if __name__ == "__main__":
    main() 