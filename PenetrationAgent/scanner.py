import subprocess
import os
import json
from datetime import datetime
from typing import Dict, List, Optional

class VulnerabilityScanner:
    def __init__(self):
        self.results_dir = "results"
        os.makedirs(self.results_dir, exist_ok=True)
        
    def save_results(self, ip: str, data: Dict) -> str:
        """Save scan results to a file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{ip}-{timestamp}.txt"
        filepath = os.path.join(self.results_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return filepath

    def stage1_fast_discovery(self, ip: str) -> List[int]:
        """Stage 1: Fast port discovery using nmap"""
        try:
            # Use nmap for port discovery
            cmd = f"nmap -sS -T4 -Pn {ip} -p- --open"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            # Parse results to get open ports
            open_ports = []
            for line in result.stdout.split('\n'):
                if 'open' in line:
                    port = int(line.split('/')[0])
                    open_ports.append(port)
            
            return open_ports
        except Exception as e:
            print(f"Error in Stage 1 for {ip}: {str(e)}")
            return []

    def stage2_service_detection(self, ip: str, open_ports: List[int]) -> Dict:
        """Stage 2: Service detection and verification"""
        try:
            ports_str = ','.join(map(str, open_ports))
            cmd = f"nmap -sS -sV -p {ports_str} {ip} -Pn --reason --open -oA {os.path.join(self.results_dir, f'nmap_{ip}')}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            services = {}
            for line in result.stdout.split('\n'):
                if 'open' in line and 'tcp' in line:
                    parts = line.split()
                    port = parts[0].split('/')[0]
                    service = ' '.join(parts[2:])
                    services[port] = service
            
            return services
        except Exception as e:
            print(f"Error in Stage 2 for {ip}: {str(e)}")
            return {}

    def stage3_recommendations(self, services: Dict) -> List[str]:
        """Stage 3: Generate recommendations based on detected services"""
        recommendations = []
        
        for port, service in services.items():
            service_lower = service.lower()
            
            # Web services
            if any(web in service_lower for web in ['http', 'apache', 'nginx', 'iis']):
                recommendations.append(f"Run web enumeration tools (nikto, gobuster) on port {port}")
            
            # Remote access services
            if any(remote in service_lower for remote in ['ssh', 'telnet', 'rdp']):
                recommendations.append(f"Check for default credentials and known vulnerabilities on port {port}")
            
            # Database services
            if any(db in service_lower for db in ['mysql', 'postgresql', 'mssql']):
                recommendations.append(f"Attempt database enumeration on port {port}")
            
            # File sharing services
            if any(fs in service_lower for fs in ['smb', 'ftp']):
                recommendations.append(f"Run enumeration tools (enum4linux-ng, smbmap) on port {port}")
            
            # Directory services
            if any(ds in service_lower for ds in ['ldap', 'kerberos']):
                recommendations.append(f"Perform LDAP enumeration on port {port}")
        
        return recommendations

    def scan_target(self, ip: str) -> Dict:
        """Perform complete scan on a single target"""
        print(f"\n🛰️ Starting scan for {ip}")
        
        # Stage 1: Fast Discovery
        print("Stage 1: Fast Port Discovery")
        open_ports = self.stage1_fast_discovery(ip)
        if not open_ports:
            return {"error": "No open ports found"}
        
        # Stage 2: Service Detection
        print("Stage 2: Service Detection")
        services = self.stage2_service_detection(ip, open_ports)
        
        # Stage 3: Recommendations
        print("Stage 3: Generating Recommendations")
        recommendations = self.stage3_recommendations(services)
        
        # Prepare results
        results = {
            "target": ip,
            "open_ports": open_ports,
            "services": services,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save results
        filepath = self.save_results(ip, results)
        print(f"Results saved to: {filepath}")
        
        return results

    def scan_targets(self, ip_list: List[str]) -> Dict:
        """Scan multiple IP addresses"""
        results = {}
        for ip in ip_list:
            ip = ip.strip()
            if ip:
                results[ip] = self.scan_target(ip)
        return results 