import mysql.connector
import pandas as pd


def fetch_data(query, params=None):
    cnx = None
    try:
        cnx = mysql.connector.connect(
            user='root',
            password='test_root',  # replace with your actual password
            host='127.0.0.1',
            database='academicworld'
        )
        df = pd.read_sql(query, cnx, params=params)
        return df
    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return pd.DataFrame()
    finally:
        if cnx and cnx.is_connected():
            cnx.close()