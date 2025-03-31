from flask import Flask, render_template, request, jsonify, send_file
from stealth_scanner import VulnerabilityScanner
import threading
import time
import os
from datetime import datetime

app = Flask(__name__)
scanner = VulnerabilityScanner()

# Global variables to track scan progress
scan_status = {
    'completed': False,
    'progress': 0,
    'status': 'Ready to scan',
    'results': {},
    'current_ip': None,
    'total_ips': 0
}

def run_scan_thread(ip_list):
    """Run the scan in a separate thread"""
    global scan_status
    
    scan_status['total_ips'] = len(ip_list)
    scan_status['completed'] = False
    scan_status['progress'] = 0
    scan_status['results'] = {}
    
    for i, ip in enumerate(ip_list):
        scan_status['current_ip'] = ip
        scan_status['status'] = f'Scanning {ip}...'
        
        # Perform the scan
        success = scanner.perform_stealth_scan(ip)
        
        # Update results
        scan_status['results'][ip] = {
            'success': success,
            'logs': scanner.get_recent_logs(ip),
            'timestamp': datetime.now().isoformat()
        }
        
        # Update progress
        progress = ((i + 1) / len(ip_list)) * 100
        scan_status['progress'] = progress
        
        # Add delay between scans
        time.sleep(2)
    
    scan_status['completed'] = True
    scan_status['status'] = 'Scan completed'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_scan', methods=['POST'])
def start_scan():
    try:
        data = request.get_json()
        ip_list = data.get('ip_list', [])
        
        if not ip_list:
            return jsonify({'error': 'No IP addresses provided'}), 400
        
        # Start scan in a separate thread
        thread = threading.Thread(target=run_scan_thread, args=(ip_list,))
        thread.daemon = True
        thread.start()
        
        return jsonify({'message': 'Scan started successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/scan_status')
def get_scan_status():
    return jsonify(scan_status)

@app.route('/download/<ip>')
def download_results(ip):
    try:
        # Get the most recent scan file for the IP
        scan_dir = 'scans'
        files = [f for f in os.listdir(scan_dir) if f.startswith(f"{ip}_stealth_full")]
        if not files:
            return jsonify({'error': 'No scan results found'}), 404
        
        latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(scan_dir, x)))
        return send_file(
            os.path.join(scan_dir, latest_file),
            as_attachment=True,
            download_name=f"{ip}_scan_results.txt"
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 