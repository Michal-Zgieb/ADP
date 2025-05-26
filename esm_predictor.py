#API

import requests

sequence = "TTGLKDGFAIGLPQQTFSGGVVLTLTVDGMEYSVTIPANKLSTFVRGTKYIVSLAVKGGKLTLMSDKILIDKDWAEVQTGTGGSGDDYDTSFN"

url = "https://api.esmatlas.com/foldSequence/v1/pdb/"
response = requests.post(url, data=sequence)

# Sprawdź status i zawartość
if response.ok:
    print("✅ Sukces")
    print(response.text)  
else:
    print("❌ Błąd:", response.status_code)
    print(response.text)

