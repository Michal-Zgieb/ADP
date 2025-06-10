# AlphaFoldER
AlphaFold3 (AF3) automating tool

The aim of the project is to create a tool allowing for query sending automation to server providing protein prediction service. It allows for parsing a fasta and communicating with AF3 server to obtain and save results on local machine.

The python script AlphaFoldER.py should be run in terminal with pthon interpreter. First it asks for directory to save the Google account informations in. In first usage user has to manually log into their Google account in Chrome browser opened by the subprocess. After logging in the user is asked to confirm it by pressing 'y' to proceed. Then the fasta file path needs to be input. The only step left is to press "Clear" button on the AF3 website, which is located over the job submittion field on the right. 
In the following tool using sessions, by providing the same Google account informations directory, user will be logged in automatically. The script controlls also the quota of jobs remaining for the user (Google account).

Sample usage:

C:\Users\kacpe\ADP>python alphafold_API.py
Enter user data dir path (or press Enter for default): "C:\Users\kacpe\ADP                  
Input 'y' if you logged into your google account: y
Enter input fasta file path: "C:\Users\kacpe\ADP\sample.fasta"
remaining available job number: 7
...
All jobs downloaded. Exiting loop.

Architecture of large projects in bioinformatics (2025)
Katsiaryna Dubrouskaya, Veranika Kananovich, Kacper Pietrzyk, Michał Zgieb 
