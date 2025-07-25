# Python in Data Science: COVID-19 Statistics Analysis

A Python application for analyzing COVID-19 statistics across different countries, featuring a GUI built with `tkinter`, data processing with `pandas`, and visualization tools. The app connects to a MySQL database and allows for filtering, statistics, and report generation.

---

## 📦 Project Structure
Work/
├── Data/
├── Library/
├── Notes/
├── Scripts/
│ ├── covid_analysis.py
│ └── config.ini
├── requirements.txt

---

## ✅ Prerequisites

### Python 3.10+
- Check: `python --version`
- [Download Python](https://www.python.org/downloads/)

### Anaconda
- Check: `conda --version`
- [Download Anaconda](https://www.anaconda.com/download)

### MySQL + MySQL Workbench
- [Download MySQL](https://dev.mysql.com/downloads/)
- Choose "Full" install during setup
- Remember your username, password, and port

---

## 🛠 Setup Instructions

### 1. Create a Virtual Environment
```bash
cd path\to\Work\Work
conda create --name covid_analysis_env python=3.10
conda activate covid_analysis_env
pip install -r requirements.txt
2. Open Spyder in Anaconda Navigator
Set the environment to covid_analysis_env

Install and launch Spyder

Open covid_analysis.py and config.ini in the Scripts/ folder

3. Configure MySQL Database
Open MySQL Workbench

Create new schema: covid_analysis_db

Update config.ini with:

Database name

Username and password used during MySQL setup

4. Set Python Interpreter in Spyder
Tools > Preferences > Python Interpreter

Use: .../envs/covid_analysis_env/python.exe

Restart Spyder if necessary

🚀 Run the Application
In Spyder:
Run covid_analysis.py
A tkinter GUI will appear with the following pages:

🧭 App Guide
1. Loading & Preprocessing
Connect DB: creates the main table if not exists

Clear Table: delete all rows in DB

Load Data: load CSVs from Data/

Clean Data: handle missing values

Insert Data: save into DB

2. Data Filtering
Filter by year, country, month

Multiple filters can be combined

3. Statistics
Select type from dropdown

Export: saves to Output/exports/

Report: saves to Output/reports/

4. Visualization
Choose chart type from dropdown

Render graphs based on filtered data

5. Configuration
Customize fonts and colors

Saves settings and restarts app to apply

👨‍🎓 Authors
Student: Mohamed Abdelhafiz Salem Abdelhafiz Youssef
Supervisor: Polyakov Konstantin Lvovich
📧 abmokhamed@edu.hse.ru


