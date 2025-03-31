from flask import Flask, render_template, request, jsonify
from scanner import VulnerabilityScanner
import json

app = Flask(__name__)
scanner = VulnerabilityScanner()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    try:
        data = request.get_json()
        ip_list = data.get('ip_list', [])
        
        if not ip_list:
            return jsonify({'error': 'No IP addresses provided'}), 400
            
        results = scanner.scan_targets(ip_list)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 