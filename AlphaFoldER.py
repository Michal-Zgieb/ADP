from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import sys
import time
import os
import json
import subprocess
from Bio import SeqIO

ALPHAFOLD_SIZE_THRESHOLD = 5000
ALLOWED_AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"
##################################__OPENING_CHROME__##############################

def find_chrome_path():
    # Try common install locations
    possible_paths = []

    if sys.platform.startswith('win'): # Windows
        possible_paths.extend([
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        ])
    elif sys.platform.startswith('linux'): # Linux
        possible_paths.extend([
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium", 
            "/usr/bin/chromium-browser",
            "/opt/google/chrome/google-chrome",
            os.path.expanduser("~/.local/bin/google-chrome"), # May be in user's local bin directory
        ])
    elif sys.platform.startswith('darwin'):  # macOS
        possible_paths.extend([
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        ])
    else:
        raise FileNotFoundError(f"Unsupported operating system: {sys.platform}. Cannot find Chrome.")

    for path in possible_paths:
        if os.path.isfile(path):
            return path

def launch_chrome(debug_port=9222, user_data_dir="C:/chrome-bot-profile"):
    chrome_path = find_chrome_path()

    # Launch Chrome
    cmd = f'"{chrome_path}" --remote-debugging-port={debug_port} --user-data-dir="{user_data_dir}"'
    subprocess.Popen(cmd)

    # Wait briefly to let Chrome start
    time.sleep(3)


######################################__ALPHA_FOLD__###################################

driver = None  # Global variable driver

def alphafold_open():
    """
    Opens the browser and gives you time to log in to your Google account manually
    """
    global driver
    options = Options()

    # Tell Selenium to connect to the existing Chrome instance
    options.add_experimental_option("debuggerAddress", "localhost:9222")

    # Use the standard ChromeDriver
    driver = webdriver.Chrome(options=options)

    # Now Selenium can control the open Chrome
    driver.get("https://alphafoldserver.com/")

def alphafold_submit(records):
    """
    Sends the sequence to the AlphaFold server after logging into the Chrome instance.    
    """
    global driver

    # 1. Wait for the sequence textarea to appear and be interactable
    wait = WebDriverWait(driver, 60)
    
    remaining_jobs_element = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "span[class='remaining-jobs']"))
    )
    
    if int(remaining_jobs_element.text) < len(records):
        print(f"Not enough remaining jobs({ int(remaining_jobs_element.text)}) for your {len(records)} long request")
        return None

    submitted_jobs = set()

    for sequence_name, sequence in records.items():
    # Try to find <textarea>, if not – click "Clear"
        
        try:
            textarea = driver.find_element(By.CSS_SELECTOR, "textarea.sequence-input")
        except:
            clear_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.clear-button")))
            clear_button.click()
            print("Click 'Clear', waiting for button...")
            textarea = wait.until(EC.visibility_of_element_located((By.XPATH, '//textarea[@pattern="/^[ACDEFGHIKLMNPQRSTVWY]*$/i"]')))

        # Seq input
        textarea.click()
        
        textarea.send_keys(sequence)
        
        time.sleep(2)
        
        # 2. Wait until the "Continue and preview job" button is clickable
        continue_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Continue')]")
        ))
        continue_btn.click()

        # 3. Wait for the sequence name input field to be visible
        name_input = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//input[@pattern='/^[\\-:\\w ]{1,200}$/i']")
        ))
        name_input.clear()
        name_input.send_keys(sequence_name)

        # 4. Wait until the "Confirm and submit job" button is clickable
        confirm_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[.//span[contains(text(),'Confirm and submit job')]]")
        ))
        confirm_btn.click()

        submitted_jobs.add(sequence_name)

    print("Click 'Confirm and submit job', waiting fot results...")


# === Begin Monitoring For Completed Job ===
    downloaded_json = "downloaded_jobs.json"
    if os.path.exists(downloaded_json):
        with open(downloaded_json, "r") as f:
            downloaded = set(json.load(f))
    else:
        downloaded = set()

    def save_downloaded():
        with open(downloaded_json, "w") as f:
            json.dump(list(downloaded), f)

    # === Monitor job list ===
    while True:
        rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'mat-mdc-row')]")
        for row in rows:
            try:
                name_cell = row.find_element(By.XPATH, ".//td[contains(@class, 'cdk-column-name')]")
                job_name = name_cell.text.strip()

                if job_name in downloaded:
                    continue

                # Click the menu button in the same row
                more_btn = row.find_element(By.XPATH, ".//mat-icon[contains(text(), 'more_vert')]/ancestor::button")
                more_btn.click()

                # Wait and click "Download"
                download_btn = wait.until(EC.element_to_be_clickable((
                    By.XPATH, "//a[.//span[text()='Download ']]"
                )))
                href = download_btn.get_attribute("href")
                print(f"Downloading: {job_name} from {href}")
                driver.execute_script("arguments[0].click();", download_btn)

                # Mark as downloaded
                downloaded.add(job_name)
                save_downloaded()
                time.sleep(5)
            except Exception as e:
                continue
        
        if submitted_jobs.issubset(downloaded):
            print("All jobs downloaded. Exiting loop.")
            break
    
def get_protein_sequence_from_fasta(file, DNA=False):
    records = {}
    disallowed_char_pattern = re.compile(f"[^{re.escape(ALLOWED_AMINO_ACIDS)}]", re.IGNORECASE)
    with open(file, "r") as handle:
        for i in SeqIO.parse(handle, "fasta"):
            uniprot_id = str(i.id)
            uniprot_id = re.sub(r"[^a-zA-Z0-9 _:-]", "_", uniprot_id)
            if DNA:
                sequence = str(i.seq.translate(to_stop=True))
            else:
                sequence = str(i.seq)
            if len(sequence) > ALPHAFOLD_SIZE_THRESHOLD:
                print(f"[{uniprot_id}] is skiped: protein is too big for AlphaFold server ({len(sequence)} residues)")
            else:
                sequence = disallowed_char_pattern.sub('A', sequence)
                records[uniprot_id] = sequence
    return records


def run_alphafold_predictions(file):
    """
    Run the whole prediction proccess.
    """
    alphafold_open()
    records = get_protein_sequence_from_fasta(file)
    alphafold_submit(records)


if __name__ == "__main__":
    
    user_input = input("Enter user data dir path (or press Enter for default): ").strip()

    if user_input:
        user_data_dir = os.path.normpath(os.path.join(user_input, "alphafold_session"))
    else:
        user_data_dir = "C:/chrome-bot-profile"

    launch_chrome(user_data_dir=user_data_dir)

    while True:
        user_input = input("Input 'y' if you logged into your google account: ").strip()
        if user_input == 'y':
            break

    
    # Ask user for path and sanitize it
    file = input("Enter input fasta file path: ").strip().strip('"')

    # Normalize slashes (optional but helpful on Windows)
    file = os.path.normpath(file)

    run_alphafold_predictions(file)
