import sqlite3
from src.utils.logger import logging

def get_db_connection(db_path:str):
    """
    Open (and return) a connection to the sqlite database at db_path.
    """
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        logging.error(f"An error occurred while connecting to the Database :- {e}")


def create_weather_table(conn):
    """
    Use the open connection to create the weather_raw table using your schema, if it doesn't already exist.
    """
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_raw (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_name TEXT NOT NULL,
            city_id TEXT NOT NULL,
            country TEXT NOT NULL,
            ts_utc INTEGER NOT NULL,
            date_str TEXT NOT NULL,
            captured_at_utc TEXT NOT NULL,
            temp_c REAL NOT NULL,
            feels_like_c REAL NOT NULL,
            humidity REAL NOT NULL,
            pressure REAL NOT NULL,
            wind_speed REAL NOT NULL,
            wind_deg REAL NOT NULL,
            weather_main TEXT,
            weather_desc TEXT,
            UNIQUE(city_id, ts_utc)
            )
        ''')
        conn.commit()
        logging.info("Weather table created successfully.")
    except sqlite3.Error as e:
        logging.error(f"An error occurred while creating the table: {e}")
    finally:
        cursor.close()


def create_metrics_table(conn):
    """
    Use the open connection to create the metrics table using your schema, if it doesn't already exist.
    """
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_metrics (
            city_name TEXT NOT NULL,
            date_utc TEXT NOT NULL, -- 'YYYY-MM-DD' in UTC
            avg_temp REAL,
            min_temp REAL,
            max_temp REAL,
            avg_humidity REAL,
            samples INTEGER,
            PRIMARY KEY (city_name, date_utc)
            );  
        ''')
        # Commit the changes to the database
        conn.commit()
        logging.info("Metrics table created successfully.")
    except sqlite3.Error as e:
        logging.error(f"An error occurred while creating the metrics table: {e}")
    finally:
        cursor.close()

