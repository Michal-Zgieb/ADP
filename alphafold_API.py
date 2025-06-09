from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = None  # globalna zmienna driver

def alphafold_open():
    global driver
    options = Options()
    driver = webdriver.Chrome(options=options)
    driver.get("https://alphafoldserver.com/")

    wait = WebDriverWait(driver, 30)
    log_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[.//span[contains(text(),'Continue with Google')]]")))
    log_btn.click()

    print("Masz 30 sekund na ręczne zalogowanie się...")
    time.sleep(30)

def alphafold_submit(sequence, sequence_name):
    global driver
    wait = WebDriverWait(driver, 20)

    # Spróbuj znaleźć <textarea>, jeśli nie ma – kliknij "Clear"
    try:
        textarea = driver.find_element(By.CSS_SELECTOR, "textarea.sequence-input")
    except:
        clear_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Clear ']]")))
        clear_button.click()
        print("Kliknięto 'Clear', czekam na pojawienie się pola...")
        textarea = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.sequence-input")))

    # Wprowadź sekwencję
    textarea.click()
    textarea.clear()
    textarea.send_keys(sequence)

    # Kliknij "Continue and preview job"
    continue_btn = driver.find_element(By.XPATH, "//button[.//span[contains(text(),'Continue and preview job')]]")
    continue_btn.click()
    time.sleep(1)

    # Wpisz nazwę sekwencji
    name_input = driver.find_element(By.XPATH, "//input[@pattern='/^[\\-:\\w ]{1,200}$/i']")
    name_input.clear()
    name_input.send_keys(sequence_name)

    # Kliknij "Confirm and submit job"
    confirm_btn = driver.find_element(By.XPATH, "//button[.//span[contains(text(),'Confirm and submit job')]]")
    confirm_btn.click()
    time.sleep(1)

    print("Kliknięto 'Confirm and submit job', teraz czekam na wyniki...")

def alphafold_download(sequence_name):
    print(f"Czekam na zakończenie przetwarzania sekwencji: {sequence_name}")
    while True:
        pass

def alphafold(sequence, sequence_name):
    alphafold_open()
    alphafold_submit(sequence, sequence_name)
    alphafold_submit(sequence, sequence_name)
    alphafold_submit(sequence, sequence_name)

    alphafold_download(sequence_name)

# Przykład użycia
alphafold(
    sequence="MSEQTKDDDISFEANNTEMMMTFQIQRIYTKDISLDLTTTKDISFEAASWN",
    sequence_name="SekwencjaTestowa"
)
