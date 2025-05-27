import requests
from Bio import SeqIO

def get_protein_sequence_from_fasta(plik, DNA=True):
    pdb = ""
    with open(plik, "r") as handle:
      for i in SeqIO.parse(handle, "fasta"):
        uniprot_id = str(i.id)
        if DNA:
          sequence = str(i.seq.translate(to_stop=True))
        else:
          sequence = str(i.seq)
        response = requests.post("https://api.esmatlas.com/foldSequence/v1/pdb/",data=sequence)
        if response.ok:
          pdb+=f"{uniprot_id}\n{response.text}\n"
        else:
          print("For sequence:", uniprot_id, "Failed to get structure:", response.text)
      with open("predicted_structure.pdb", "w") as f:
        f.write(pdb)
      print("Structure saved to predicted_structure.pdb")

      

def get_protein_sequence_from_sequence(sequence, DNA=True):
    if DNA:
        sequence = str(sequence.translate(to_stop=True))
    else:
        sequence = str(sequence)

    response = requests.post(
        "https://api.esmatlas.com/foldSequence/v1/pdb/",
        data=sequence
    
    )
    if response.ok:
        pdb = response.text
        with open("predicted_structure.pdb", "w") as f:
            f.write(pdb)
        print("Structure saved to predicted_structure.pdb")
    else:
        print("Failed to get structure:", response.text)

#get_protein_sequence_from_fasta("plik.fasta")
get_protein_sequence_from_sequence("MSEQNNTEMTFQIQRIYTKDISFEAPNAPHVFQKDWLDLASWDN", False)
