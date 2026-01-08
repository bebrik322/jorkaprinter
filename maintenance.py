import os
import datetime
import subprocess
import re
import sys
import argparse
import random

PRINTER_NAME = "DeskJet_3630"
LOG_FILE = "/var/log/cups/page_log"
THRESHOLD_DAYS = 7

def get_last_print_time(printer_name, log_file):
    last_print_time = None
    
    try:
        if not os.path.exists(log_file):
            return None

        with open(log_file, 'r') as f:
            for line in f:
                parts = line.split()
                if not parts:
                    continue
                
                if parts[0] == printer_name:
                    match = re.search(r'\[(.*?)]', line)
                    if match:
                        timestamp_str = match.group(1)
                        try:
                            dt = datetime.datetime.strptime(timestamp_str, "%d/%b/%Y:%H:%M:%S %z")
                            last_print_time = dt
                        except ValueError:
                            continue

    except PermissionError:
        print(f"Permission denied reading {log_file}. Run as root or user with log access.")
        sys.exit(1)
        
    return last_print_time

def get_default_printer():
    try:
        result = subprocess.run(["lpstat", "-d"], capture_output=True, text=True, check=True)
        line = result.stdout.strip()
        prefix = "system default destination:"
        if prefix in line:
            return line.split(prefix)[1].strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return None

def generate_test_page_image(output_path):
    width = 595
    height = 842
    
    pat_w = 300
    pat_h = 50
    
    max_x = width - pat_w - 20
    max_y = height - pat_h - 20
    pos_x = random.randint(20, max_x)
    pos_y = random.randint(20, max_y)
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    label = f"Maintenance: {timestamp}"

    cmd = [
        "convert",
        "-size", f"{width}x{height}", "xc:white", 
        "(", 
            "-size", f"{pat_w//4}x{pat_h}", "xc:cyan", "xc:magenta", "xc:yellow", "xc:black", "+append",
            "+size", "-background", "white", "-fill", "black", "-pointsize", "12", 
            f"label:{label}", "-append",
        ")",
        "-geometry", f"+{pos_x}+{pos_y}", 
        "-composite",
        output_path
    ]
    
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error generating image: {e}")
        return False
    except FileNotFoundError:
        print("Error: 'convert' command (ImageMagick) not found.")
        return False

def print_test_page():
    temp_file = os.path.join(os.getcwd(), "jorka_temp_test.png")
    
    print("Generating dynamic test page...")
    if generate_test_page_image(temp_file):
        print(f"Printing test page: {temp_file}")
        try:
            result = subprocess.run(
                ["lp", "-d", PRINTER_NAME, "-o", "media=A4", temp_file], 
                check=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            
            job_id = "Unknown"
            match = re.search(r"request id is ([\w_-]+)", result.stdout)
            if match:
                job_id = match.group(1)
            
            print(f"✔ Test page sent successfully (Job ID: {job_id})")
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to print: {e.stderr.strip()}")
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    else:
        print("Failed to generate test page. Aborting.")

def main():
    parser = argparse.ArgumentParser(description="Printer maintenance script.")
    parser.add_argument("--force", action="store_true", help="Force print test page ignoring history.")
    parser.add_argument("--printer", type=str, help="CUPS Printer Name (Auto-detects default if omitted)")
    parser.add_argument("--days", type=int, default=THRESHOLD_DAYS, help="Days threshold")
    
    args = parser.parse_args()
    
    global PRINTER_NAME
    PRINTER_NAME = args.printer or get_default_printer() or PRINTER_NAME
    threshold = args.days

    if not PRINTER_NAME:
        print("Error: Could not detect a default printer. Please specify one with --printer.")
        sys.exit(1)

    print(f"Checking printer activity for: {PRINTER_NAME}")
    
    if args.force:
        print("Force mode enabled.")
        print_test_page()
        return

    last_print = get_last_print_time(PRINTER_NAME, LOG_FILE)
    
    if last_print:
        now = datetime.datetime.now(last_print.tzinfo)
        delta = now - last_print
        print(f"Last print was on: {last_print} ({delta.days} days ago)")
        
        if delta.days >= threshold:
            print(f"Printer not used for {delta.days} days. Initiating maintenance print.")
            print_test_page()
        else:
            print("Printer used recently. No maintenance needed.")
    else:
        print("No print history found. Initiating maintenance print.")
        print_test_page()

if __name__ == "__main__":
    main()
