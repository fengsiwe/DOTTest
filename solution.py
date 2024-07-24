import sqlite3
import csv
import os

def setup_database(db_name='outlets_transactions.db'):
    """Create the transactions table using SQLite database"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    #Create outlets transaction table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS transactions (
        shop_id INTEGER,
        date TEXT,
        n_trans INTEGER
    );
    """

    cursor.execute(create_table_query)
    conn.commit()
    conn.close()

def clean_data(row):
    """Clean data row by row. Convert to appropriate types and handle errors."""
    try:
        row[0] = int(row[0])  # shop_id
        row[2] = int(row[2])  # n_trans
        return row
    except ValueError:
        return None    


def load_data(csv_file_name, db_name='outlets_transactions.db'):
    """Load data into the database"""
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the full path to the CSV file
    csv_file_path = os.path.join(script_dir, csv_file_name)

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            clean_row = clean_data(row)
            if clean_row:
                cursor.execute("INSERT INTO transactions (shop_id, date, n_trans) VALUES (?, ?, ?)", clean_row)
    
    conn.commit()
    conn.close()


def create_view(db_name='outlets_transactions.db'):
    """Create a view which customer required"""

#Execute here
setup_database()
load_data('sample.csv')