import os
import subprocess
import time
import shutil

def find_chrome_path():
    # Try common install locations
    possible_paths = [
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
    ]
    for path in possible_paths:
        if os.path.isfile(path):
            return path
    raise FileNotFoundError("Could not find chrome.exe.")

def launch_chrome(debug_port=9222, user_data_dir="C:/chrome-bot-profile"):
    chrome_path = find_chrome_path()

    # Kill old debugging Chrome sessions if needed (optional cleanup)
    subprocess.call(["taskkill", "/f", "/im", "chrome.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Launch Chrome
    cmd = f'"{chrome_path}" --remote-debugging-port={debug_port} --user-data-dir="{user_data_dir}"'
    subprocess.Popen(cmd)

    # Wait briefly to let Chrome start
    time.sleep(3)


if __name__ == "__main__":
    user_input = input("Enter user data dir path (or press Enter for default): ").strip()

    if user_input:
        user_data_dir = os.path.normpath(os.path.join(user_input, "alphafold_session"))
    else:
        user_data_dir = "C:/chrome-bot-profile"

    launch_chrome(user_data_dir=user_data_dir)