from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import json
import sys
from Bio import SeqIO
import re
import subprocess

##################################__VARIABLES__##############################

ALPHAFOLD_SIZE_THRESHOLD = 5000
DEFAULT_WAIT_TIMEOUT = 30
ALLOWED_AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"
ALPHAFOLD_URL = "https://alphafoldserver.com/"

REMAINING_JOBS_ELEMENT_CSS_SELECTOR = "span.remaining-jobs"
REMAINING_JOBS_SPINNER_ELEMENT_CSS_SELECTOR = "span.remaining-jobs mat-spinner"
CLEAR_BUTTON_CSS_SELECTOR = "button.clear-button"
JOB_TABLE_CSS_SELECTOR = "table.cdk-table"
JOB_TABLE_ROW_CSS_SELECTOR = "table.cdk-table tr.mat-mdc-row"
JOB_ROW_NAME_CELL_CSS_SELECTOR = "td.cdk-column-name"
JOB_ROW_STATUS_CELL_CSS_SELECTOR = "td.cdk-column-status"
CONTINUE_BUTTON_CSS_SELECTOR = "button.create-request"
JOB_CREATE_FORM_FIELD_NAME_CSS_SELECTOR = "gdm-af-preview-dialog mat-form-field.name input"
SUBMIT_JOB_BUTTON_CSS_SELECTOR = "gdm-af-preview-dialog footer button.confirm"
TEXT_AREA_CSS_SELECTION = "textarea.sequence-input"
MORE_BUTTON_XPATH = ".//mat-icon[contains(text(), 'more_vert')]/ancestor::button"
DOWNLOAD_BUTTON_XPATH = "//a[.//span[text()='Download ']]"
STATUS_CELL_TAG_NAME = "mat-spinner"

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

def open_browser(debug_port=9222, user_data_dir="C:/chrome-bot-profile"):
    chrome_path = find_chrome_path()

    # Launch Chrome
    cmd = f'"{chrome_path}" --remote-debugging-port={debug_port} --user-data-dir="{user_data_dir}"'
    subprocess.Popen(cmd)

    # Wait briefly to let Chrome start
    time.sleep(3)

    options = Options()
    options.add_argument(f"user-data-dir={user_data_dir}")
    options.add_experimental_option("debuggerAddress", f"localhost:{debug_port}")
    return webdriver.Chrome(options)

def login_to_alphafold():
    driver.get(ALPHAFOLD_URL)

    while True:
        user_input = input("Input 'y' if you logged into your google account: ").strip()
        if user_input == 'y':
            break

######################################__ALPHA_FOLD__###################################

def open_aphafold(driver):
    driver.get(ALPHAFOLD_URL)

    wait = WebDriverWait(driver, DEFAULT_WAIT_TIMEOUT)

    # remaining jobs element appeared on the page
    wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, REMAINING_JOBS_ELEMENT_CSS_SELECTOR))
    )

    # remaining jobs element fully loaded
    wait.until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, REMAINING_JOBS_SPINNER_ELEMENT_CSS_SELECTOR))
    )

def submit_records_to_prediction(driver, records):
    wait = WebDriverWait(driver, DEFAULT_WAIT_TIMEOUT)
    submitted_jobs = set()

    remaining_jobs_element = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, REMAINING_JOBS_ELEMENT_CSS_SELECTOR))
    )
    if int(remaining_jobs_element.text) < len(records):
        print(f"Not enough remaining jobs({ int(remaining_jobs_element.text)}) for your {len(records)} long request")
        return None
    
    already_finished_jobs = get_already_predicted_record_names(driver)

    for sequence_name, sequence in records.items():
        if sequence_name in already_finished_jobs:
            continue
        
        # retry 5 times if any errors
        for _attempt in range(5): 
            try:
                clear_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, CLEAR_BUTTON_CSS_SELECTOR)))
                clear_button.click()
                textarea = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, TEXT_AREA_CSS_SELECTION)))
                textarea.send_keys(sequence)

                continue_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, CONTINUE_BUTTON_CSS_SELECTOR)))
                continue_btn.click()

                name_input = wait.until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, JOB_CREATE_FORM_FIELD_NAME_CSS_SELECTOR)
                ))
                name_input.clear()
                name_input.send_keys(sequence_name)

                confirm_btn = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, SUBMIT_JOB_BUTTON_CSS_SELECTOR)
                ))
                confirm_btn.click()

                submitted_jobs.add(sequence_name)
                # if success stop retrying
                break
            except Exception as e:
                print(e)
                open_aphafold(driver)

            wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, JOB_TABLE_CSS_SELECTOR), sequence_name))

def download_records_predictions(driver, records):
    wait = WebDriverWait(driver, 30)
    records_names_to_download = set(records.keys())
    # get already downloaded from the folder
    already_downloaded = set()
    downloaded_json = "downloaded_jobs.json"

    if os.path.exists(downloaded_json):
        with open(downloaded_json, "r") as f:
            already_downloaded = set(json.load(f))

    while not records_names_to_download.issubset(already_downloaded):
        for row in driver.find_elements(By.CSS_SELECTOR, JOB_TABLE_ROW_CSS_SELECTOR):
            try:
                name_cell = row.find_element(By.CSS_SELECTOR, JOB_ROW_NAME_CELL_CSS_SELECTOR)
                job_name = name_cell.text.strip()

                if job_name not in records_names_to_download:
                    continue
                if job_name in already_downloaded:
                    continue
                
                more_btn = row.find_element(By.XPATH, MORE_BUTTON_XPATH)
                more_btn.click()

                download_btn = wait.until(EC.element_to_be_clickable((
                    By.XPATH, DOWNLOAD_BUTTON_XPATH
                )))
                href = download_btn.get_attribute("href")
                print(f"Downloading: {job_name} from {href}")
                driver.execute_script("arguments[0].click();", download_btn)

                # Mark as downloaded
                already_downloaded.add(job_name)
                save_downloaded(downloaded_json, already_downloaded)
                time.sleep(5)
            except:
                open_aphafold(driver)
                continue

    print("All jobs downloaded. Exiting loop.")

def save_downloaded(downloaded_json, downloaded):
    with open(downloaded_json, "w") as f:
        json.dump(list(downloaded), f)

def get_already_predicted_record_names(driver):
    all_rows = driver.find_elements(By.CSS_SELECTOR, JOB_TABLE_ROW_CSS_SELECTOR)
    already_finished_jobs = set()

    for row in all_rows:
        status_cell = row.find_element(By.CSS_SELECTOR, JOB_ROW_STATUS_CELL_CSS_SELECTOR)
        if status_cell.find_elements(By.TAG_NAME, STATUS_CELL_TAG_NAME):
            continue

        name_cell = row.find_element(By.CSS_SELECTOR, JOB_ROW_NAME_CELL_CSS_SELECTOR)
        already_finished_jobs.add(name_cell.text.strip())
    
    return already_finished_jobs

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
                print(f"[{uniprot_id}] Protein is too big for AlphaFold server ({len(sequence)} residues)")
            else:
                sequence = disallowed_char_pattern.sub('A', sequence)
                records[uniprot_id] = sequence
    return records

def run_alphafold_predictions(driver, file):
    open_aphafold(driver)
    records = get_protein_sequence_from_fasta(file)
    submit_records_to_prediction(driver, records)
    download_records_predictions(driver, records)

if __name__ == "__main__":
    path_to_fasta_file = input("Enter input fasta file path: ").strip().strip('"')
    chrome_user_data_dir = input("Enter user data dir path (or press Enter for default): ").strip()

    if chrome_user_data_dir:
        user_data_dir = os.path.normpath(os.path.join(chrome_user_data_dir, "alphafold_session"))
    else:
        user_data_dir = "C:/chrome-bot-profile"

    driver = open_browser(user_data_dir = user_data_dir)
    open_aphafold(driver)
    login_to_alphafold()

    file = os.path.normpath(path_to_fasta_file)

    run_alphafold_predictions(driver, file)

