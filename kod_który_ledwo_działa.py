from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def alphafold_submit(sequence):
    options = Options()
    driver = webdriver.Chrome(options=options)
    driver.get("https://alphafoldserver.com/")

    print("Masz 30 sekund na ręczne zalogowanie się...")
    time.sleep(30)  # czas na login

    # Wpisz sekwencję w textarea
    textarea = driver.find_element(By.CSS_SELECTOR, "textarea.sequence-input")
    textarea.clear()
    textarea.send_keys(sequence)

    # Kliknij "Continue and preview job"
    continue_btn = driver.find_element(By.XPATH, "//button[.//span[contains(text(),'Continue and preview job')]]")
    continue_btn.click()

    print("Kliknięto 'Continue and preview job', czekam 5 sekund...")
    time.sleep(5)

    # Kliknij "Confirm and submit job"
    confirm_btn = driver.find_element(By.XPATH, "//button[.//span[contains(text(),'Confirm and submit job')]]")
    confirm_btn.click()

    print("Kliknięto 'Confirm and submit job', teraz czekam na wyniki...")

    # tutaj możesz dodać dalsze waity lub logikę oczekiwania

alphafold_submit("MSEQNNTEMTFQIQRIYTKDISFEAPNAPHVFQKDWLDLASWDN")
