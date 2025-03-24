# IPL Statistics Creator

This is a quick-and-dirty Python project for analyzing JSON data from IPL matches (from [Cricsheet](https://cricsheet.org/)) and outputting a color-coded Excel file for easier viewing.

---

## Getting Started

### Prerequisites

- Python 3.7 or higher
- [Pip](https://pip.pypa.io/en/stable/installation/)

### Installation

1. **Clone the Repository**:
```bash
git clone https://github.com/ImAdityaGupta/ipl-statistics
cd ipl-statistics
```

2. **Create a Virtual Environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

### Running the Code

1. **Data Management:**
   Match data should be in the `ipl_json/` folder. This folder should contain one json file for each match, in
the format provided by Cricsheet, alongside a `README.txt` file listing match information. The easiest way to get this folder is to visit [cricsheet.org/matches](https://cricsheet.org/matches/),
scroll down to Indian Premier League, download the JSON zip, and extract files to replace the `ipl_json` folder.

   
2. **Run with Default Parameters:**  
   By default, the program outputs the Excel file as `BallByBall.xlsx` and processes matches from all years. Note: any 
   old data contained in the Excel file will be written over **without warning**.

   To run with defaults, simply execute:
   
       python main.py

3. **Customizing Output and Year Filter:**  
   You can specify:
     - `--output` (or `-o`): the name of the Excel file to save.
     - `--years` (or `-y`): a comma-separated list of years to process.
   
   **Examples:**
   - To save to `CustomOutput.xlsx` and only process matches from 2023 and 2024:
     
         python main.py --output CustomOutput.xlsx --years 2023,2024

   - To save to `Results.xlsx` and process all years (omit the `--years` option):
     
         python main.py --output Results.xlsx

The script will parse the match data according to the specified parameters and generate a color-coded Excel file with player statistics.


---

## Project Structure

```
IPL-2025/
├── ipl_json/               # Folder for JSON match files + README.txt of match IDs; get from Cricsheet
├── main.py                 
├── requirements.txt        # Python dependencies
├── README.md               # This documentation
└── .gitignore              # Ignores unnecessary files (e.g., .idea/, __pycache__/)
```

---

## Notes

- The script removes old data (`Statistics.pkl`) each time it runs.
- It uses `pickle` to store intermediate player stats, then writes them to an Excel file via `xlsxwriter`.
- This is a quick hack for personal use, and it is possible this breaks eventually.


