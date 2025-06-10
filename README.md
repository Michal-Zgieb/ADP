# ADP_2025: AlphaFoldER  Automating Tool 
=======
AlphaFold3 (AF3) automating tool

The AlphaFold3 (AF3) Automating Tool is a Python script designed to automate sending queries to a server providing protein structure prediction services. It allows for parsing FASTA files and communicating with the AF3 server to obtain and save results on your local machine.

## Table of Contents 
* [Requirements](#requirements)
* [Installation](#installation)
* [Usage](#usage)
* [Authors](#authors)

---

## Requirements 

To ensure the tool runs correctly, you'll need:

* **Python 3.x** (version 3.8 or newer is recommended).
* **Google Chrome browser** installed on your system.
* **Chrome Driver** compatible with your Chrome browser version. The script attempts to automatically download and configure ChromeDriver, but manual intervention might be needed if issues arise.
* **Python Libraries:** All necessary libraries are listed in the `requirements.txt` file.

---

## Installation 

Follow these steps to set up your environment and install dependencies:

1.  **Clone the Repository:**
    Open your terminal or command prompt and clone the GitHub repository:
    ```bash
    git clone [https://github.com/YourUsername/YourRepositoryName.git](https://github.com/YourUsername/YourRepositoryName.git)
    cd YourRepositoryName # Navigate to the project directory
    ```
    *(Replace `YourUsername` and `YourRepositoryName` with your actual GitHub username and repository name.)*

2.  **Create and Activate a Virtual Environment (Recommended):**
    Using a virtual environment helps isolate project dependencies from your global Python packages.
    ```bash
    python -m venv venv
    ```
    * **Activate the virtual environment:**
        * **Windows:**
            ```bash
            .\venv\Scripts\activate
            ```
        * **macOS/Linux:**
            ```bash
            source venv/bin/activate
            ```

3.  **Install Python Dependencies:**
    Once the virtual environment is activated, install all required libraries from the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

---

## Usage 

To run the `AlphaFoldER.py` script and use the tool, follow these instructions:

1.  **Run the Script:**
    Ensure you are in the main project directory in your terminal (where `AlphaFoldER.py` is located) and your virtual environment is active.
    ```bash
    python AlphaFoldER.py
    ```

2.  **Provide User Data Directory Path:**
    The first time you run the script, it will ask for a directory path where Google account information (e.g., session cookies) will be saved.
    ```
    Enter user data dir path (or press Enter for default): "C:\Users\kacpe\ADP"
    ```
    If you don't provide a path, a default location will be used (usually the directory where the script was run, or a special temporary/application directory).

3.  **Initial Google Account Login (One-Time):**
    During the first use of the tool, the script will open the Chrome browser (via `subprocess`) and prompt you to **manually log in to your Google account**. This is required to gain access to the AlphaFold3 server.

    After logging in through the browser, return to your terminal and confirm that the login process is complete by typing `y`:
    ```
    Input 'y' if you logged into your google account: y
    ```

4.  **Enter FASTA File Path:**
    Next, the script will ask for the path to your FASTA file containing the protein sequences for prediction.
    ```
    Enter input fasta file path: "C:\Users\kacpe\ADP\sample.fasta"
    ```

5.  **Confirm "Clear" on AF3 Website:**
    Before job submission begins, you must **manually click the "Clear" button** on the AlphaFold3 website. This button is typically located above the job submission field on the right side of the AF3 interface. The script will wait for this confirmation.

6.  **Monitor Progress:**
    The script will automatically begin submitting jobs and monitoring the remaining number of available predictions for your Google account.
    ```
    remaining available job number: 7
    ...
    All jobs downloaded. Exiting loop.
    ```

### Subsequent Tool Usage 

For subsequent sessions, if you provide the same user data directory path, the script will automatically log you into your Google account using the saved session information. This significantly streamlines the process and eliminates the need for repeated manual logins. The script will also continue to monitor your remaining job quota.

---

## Authors 

* Katsiaryna Dubrouskaya
* Veranika Kananovich
* Kacper Pietrzyk
* Michał Zgieb

*(Project developed as part of "Architecture of large projects in bioinformatics", 2025)*
