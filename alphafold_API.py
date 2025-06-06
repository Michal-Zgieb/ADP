from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = None  # globalna zmienna driver

def alphafold_open():
    """
    tylko otwiera przeglądarkę i daje czas na logowanie
    :return: None
    """
    global driver
    options = Options()
    driver = webdriver.Chrome(options=options)
    driver.get("https://alphafoldserver.com/")

    # czekaj aż pojawi się możliwość kliknięcia przycisku "Continue with Google"
    wait = WebDriverWait(driver, 30)
    log_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[.//span[contains(text(),'Continue with Google')]]")))
    log_btn.click()

    print("Masz 30 sekund na ręczne zalogowanie się...")
    time.sleep(30)  # czas na login


def alphafold_submit(sequence, sequence_name):
    """
    pozwala wysłać sekwencję
    """
    global driver

    # Wpisz sekwencję
    textarea = driver.find_element(By.XPATH, '//textarea[@pattern="/^[ACDEFGHIKLMNPQRSTVWY]*$/i"]')
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

    print("Kliknięto 'Confirm and submit job', teraz czekam na wyniki...")


def alphafold_download(sequence_name):
    """
    pozwala na pobranie plików (możemy to zrobić jako osobną funkcję lub wrzucić do alphafold_submit)
    """
    print(f"Czekam na zakończenie przetwarzania sekwencji: {sequence_name}")
    while True:
        pass  # tylko po to by się nie zamykało pod koniec


def alphafold(sequence, sequence_name):
    """
    główna funkcja uruchamiająca proces
    """
    alphafold_open()
    alphafold_submit(sequence, sequence_name)
    alphafold_download(sequence_name)


# Przykład użycia
alphafold(
    sequence="MSEQNNTEMTFQIQRIYTKDISFEAPNAPHVFQKDWLDLASWDN",
    sequence_name="SekwencjaTestowa"
)
