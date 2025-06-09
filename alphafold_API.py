from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import json

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




def alphafold_submit(sequence, sequence_name):
    """
    Wysyła sekwencję do AlphaFold Server po wcześniejszym zalogowaniu do instancji Chrome.
    """
    global driver
    wait = WebDriverWait(driver, 30)  # Wait up to 30 seconds for each element

    # 1. Wait for the sequence textarea to appear and be interactable
    textarea = wait.until(EC.visibility_of_element_located(
        (By.XPATH, '//textarea[@pattern="/^[ACDEFGHIKLMNPQRSTVWY]*$/i"]')
    ))
    textarea.clear()
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

        print("⏳ Waiting for more jobs to complete...")
        time.sleep(15)
    


def alphafold(sequence, sequence_name):
    """
    główna funkcja uruchamiająca proces
    """
    alphafold_open()
    alphafold_submit(sequence, sequence_name)


# Przykład użycia
alphafold(
    sequence="MSEQNNTEMTFQIQRIYTKDISFEAPNAPHVFQKDWLDLASWDN",
    sequence_name="SekwencjaTestowa"
)
