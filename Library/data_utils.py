"""
data_utils.py

This module processes COVID-19 data from CSV files and loads it into a MySQL database.
It supports table creation, data loading, cleaning, and insertion for selected countries.
"""

import os
import configparser
from datetime import datetime
import mysql.connector
import pandas as pd

# --- Constants ---
TARGET_COUNTRIES = ["India", "Brazil", "Russia", "United Kingdom", "Egypt", "Italy", "South Africa"]
CSV_FOLDER_PATH = "../Data/csse_covid_19_daily_reports/"

# --- Utilities ---

def connect_to_database():
    """Establish and return a connection to the MySQL database."""
    db = config['mysql']
    user = db['user']
    pwd = db['password']
    host = db['host']
    name = db['database']

    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=pwd,
        database=name
    )
    return connection

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

def ensure_columns_exist_in_db(conn):
    """
    Create the covid_data table with required columns if it doesn't exist.
    
    Args:
        conn: A MySQL connection object.
    """
    cursor = conn.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS covid_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        country VARCHAR(100),
        province VARCHAR(100),
        date DATE,
        confirmed_cases INT,
        deaths_cases INT,
        recovered_cases INT,
        latitude FLOAT,
        longitude FLOAT
    )
    """
    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    print("✅ Table structure ensured in database.")

def load_all_csvs(folder_path):
    """
    Load and combine CSV files from a given folder path.

    Args:
        folder_path (str): Path to the folder containing CSV files.

    Returns:
        DataFrame: Cleaned and combined data from all CSV files.
    """
    all_data = []

    for filename in os.listdir(folder_path):
        if not filename.endswith(".csv"):
            continue

        report_date = datetime.strptime(filename[:-4], "%m-%d-%Y").date()

        if report_date.year < 2021 or report_date.year > 2023:
            continue

        df = pd.read_csv(os.path.join(folder_path, filename))
        df.columns = [c.strip().replace('/', '_').replace(' ', '_') for c in df.columns]

        if 'Lat' not in df.columns:
            df['Lat'] = 0
        if 'Long_' not in df.columns:
            df['Long_'] = 0

        df = df[
            ['Province_State', 'Country_Region', 'Confirmed', 'Deaths', 'Recovered', 'Lat', 'Long_']
        ]
        df = df[df['Country_Region'].isin(TARGET_COUNTRIES)].copy()
        df['report_date'] = report_date

        all_data.append(df)

    full_data = pd.concat(all_data, ignore_index=True)
    return full_data

def clean_data(df):
    """
    Clean the given DataFrame by handling missing values and sorting.

    Args:
        df (DataFrame): The data to clean.

    Returns:
        DataFrame: Cleaned data.
    """
    df['Province_State'] = df['Province_State'].fillna('Unknown')
    df['Confirmed'] = df['Confirmed'].fillna(0).astype(int)
    df['Deaths'] = df['Deaths'].fillna(0).astype(int)
    df['Recovered'] = df['Recovered'].fillna(0).astype(int)
    df['Lat'] = df['Lat'].fillna(0)
    df['Long_'] = df['Long_'].fillna(0)
    df = df.sort_values(['Country_Region','report_date'], ascending=[True,True])
    return df

def insert_data_into_db(df):
    """
    Insert the given DataFrame into the covid_data table.

    Args:
        df (DataFrame): The data to insert into the database.
    """
    conn = connect_to_database()
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO covid_data (country, province, date, confirmed_cases, deaths_cases, 
                            recovered_cases, latitude, longitude)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    for _, row in df.iterrows():
        cursor.execute(insert_query, (
            row['Country_Region'],
            row['Province_State'],
            row['report_date'],
            row['Confirmed'],
            row['Deaths'],
            row['Recovered'],
            row['Lat'],
            row['Long_']
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Inserted {len(df)} records into the database.")

def load_data_from_db():
    """
    Load all records from the covid_data table.

    Returns:
        DataFrame: Data loaded from the database.
    """
    conn = connect_to_database()
    query = """
    SELECT country, province, date, confirmed_cases, deaths_cases, 
           recovered_cases, latitude, longitude
    FROM covid_data
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def truncate_covid_data_table():
    """
    Truncate the covid_data table, removing all records but keeping the schema.
    """
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("TRUNCATE TABLE covid_data")
    conn.commit()
    cursor.close()
    conn.close()
    print("⚠️ All records deleted from covid_data (schema preserved).")
