from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import json
import subprocess
from Bio import SeqIO

##################################__OPENING_CHROME__##############################

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

    # Launch Chrome
    cmd = f'"{chrome_path}" --remote-debugging-port={debug_port} --user-data-dir="{user_data_dir}"'
    subprocess.Popen(cmd)

    # Wait briefly to let Chrome start
    time.sleep(3)



######################################__ALPHA_FOLD__###################################

driver = None  # globalna zmienna driver

def alphafold_open():
    """
    tylko otwiera przeglądarkę i daje czas na logowanie
    :return: None
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
    Wysyła sekwencję do AlphaFold Server po wcześniejszym zalogowaniu do instancji Chrome.
    """
    global driver

    # 1. Wait for the sequence textarea to appear and be interactable
    wait = WebDriverWait(driver, 30)
    
    submitted_jobs = set()
    print(records.keys())

    for sequence_name, sequence in records.items():
    # Spróbuj znaleźć <textarea>, jeśli nie ma – kliknij "Clear"
        try:
            textarea = driver.find_element(By.CSS_SELECTOR, "textarea.sequence-input")
        except:
            clear_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Clear ']]")))
            clear_button.click()
            print("Kliknięto 'Clear', czekam na pojawienie się pola...")
            textarea = wait.until(EC.visibility_of_element_located((By.XPATH, '//textarea[@pattern="/^[ACDEFGHIKLMNPQRSTVWY]*$/i"]')))

        # Wprowadź sekwencję
        textarea.click()
        textarea.send_keys(sequence)

        # 2. Wait until the "Continue and preview job" button is clickable
        continue_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[.//span[contains(text(),'Continue and preview job')]]")
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

        name_input.send_keys(sequence_name)
        submitted_jobs.add(sequence_name)


    print("Kliknięto 'Confirm and submit job', teraz czekam na wyniki...")


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

                # Check for check_circle
                status_icon = row.find_element(By.XPATH, ".//mat-icon[contains(text(), 'check_circle')]")

                # Click the menu button in the same row
                more_btn = row.find_element(By.XPATH, ".//mat-icon[contains(text(), 'more_vert')]/ancestor::button")
                more_btn.click()

                # Wait and click "Download"
                download_btn = wait.until(EC.element_to_be_clickable((
                    By.XPATH, "//a[.//span[text()='Download ']]"
                )))
                href = download_btn.get_attribute("href")
                print(f"⬇️ Downloading: {job_name} from {href}")
                driver.execute_script("arguments[0].click();", download_btn)

                # Mark as downloaded
                downloaded.add(job_name)
                save_downloaded()
                time.sleep(5)
            except Exception as e:
                continue
        
        if submitted_jobs.issubset(downloaded):
            print("✅ All jobs downloaded. Exiting loop.")
            break
    
def get_protein_sequence_from_fasta(plik, DNA=False):
    
    records = {}
    with open(file, "r") as handle:
        for i in SeqIO.parse(handle, "fasta"):
            uniprot_id = str(i.id)
            if DNA:
                sequence = str(i.seq.translate(to_stop=True))
            else:
                sequence = str(i.seq)
            records[uniprot_id] = sequence
        

    return records


def alphafold(file):
    """
    główna funkcja uruchamiająca proces
    """
    alphafold_open()
    records = get_protein_sequence_from_fasta(file)
    alphafold_submit(records)


if __name__ == "__main__":
    
    # user_input = input("Enter user data dir path (or press Enter for default): ").strip()

    # if user_input:
    #     user_data_dir = os.path.normpath(os.path.join(user_input, "alphafold_session"))
    # else:
    #     user_data_dir = "C:/chrome-bot-profile"

    # launch_chrome(user_data_dir=user_data_dir)

    permit = None
    while permit is None:
        user_input = input("Input 'y' if you logged into your google account: ").strip()
        if user_input == 'y':
            permit = 'y'

    
    # Ask user for path and sanitize it
    file = input("Enter input fasta file path: ").strip().strip('"')

    # Normalize slashes (optional but helpful on Windows)
    file = os.path.normpath(file)



    alphafold(file)
