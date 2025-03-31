# Vulnerability Scanner

A web-based vulnerability scanner that uses nmap to scan multiple IP addresses for open ports and potential vulnerabilities.

## Prerequisites

- Python 3.7 or higher
- nmap installed on your system
- sudo privileges (for running nmap with specific options)

## Installation

1. Clone this repository
2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to `http://localhost:5000`

3. Enter the IP addresses you want to scan (one per line) in the text area

4. Click "Start Scan" to begin the scanning process

## Features

- Web interface for easy IP address input
- Two types of scans for each IP:
  - Port scan to identify open ports
  - Detailed scan with specific nmap options
- Results displayed in a clean, organized format
- Support for multiple IP addresses
- Progress indication during scanning

## Note

This tool requires sudo privileges to run certain nmap commands. Make sure you have the necessary permissions before running the application. 