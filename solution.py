import sqlite3
import csv

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


def load_data(csv_file_path, db_name='outlets_transactions.db'):
    """Load data into the database"""


def create_view(db_name='outlets_transactions.db'):
    """Create a view which customer required"""

#Execute here
setup_database()