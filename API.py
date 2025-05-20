import requests

sequence = "MSEQNNTEMTFQIQRIYTKDISFEAPNAPHVFQKDWLDLASWDN"

response = requests.post(
    "https://api.esmatlas.com/foldSequence/v1/pdb/",
    data={"sequence": sequence},
    headers={"Content-Type": "application/x-www-form-urlencoded"},
)

if response.ok:
    pdb = response.text
    with open("predicted_structure.pdb", "w") as f:
        f.write(pdb)
    print("Structure saved to predicted_structure.pdb")
else:
    print("Failed to get structure:", response.text)