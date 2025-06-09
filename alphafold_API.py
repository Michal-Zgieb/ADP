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


def alphafold_download(sequence_name):
    """
    pozwala na pobranie plików (możemy to zrobić jako osobną funkcję lub wrzucić do alphafold_submit)
    """
    print(f"Czekam na zakończenie przetwarzania sekwencji: {sequence_name}")
    


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
