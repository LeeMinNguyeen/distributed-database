import pyodbc
import numpy as np
import pandas as pd

class database:
    def __init__(self, server, database):
        self.server = server
        self.database = database
        
    def conn_info(self):
        # Define the connection string using Windows Authentication
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            "Trusted_Connection=yes;"
        )
        return conn_str

    def connect(self):
        """Connect to the database"""
        try:
            self.conn = pyodbc.connect(self.conn_info())
            print("Connection successful")
            return self.conn
        except Exception as e:
            print(f"Error: {e}")

    def close(self):
        self.conn.close()
        print("Connection closed")
        
    def sql(self, query, type):
        self.query = query
        cursor = self.conn.cursor()
        cursor.execute(self.query)
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        
        match type:
            case "table":
                return columns, rows
            case "array":
                return np.array(rows, dtype=object)
            case "dataframe":
                flattened_rows = [list(row) for row in rows]
                return pd.DataFrame(flattened_rows, columns=columns)
            case "json":
                return [dict(zip(columns, row)) for row in rows]

if __name__ == "__main__":
    connn = database("NGUYIN\\NGUYIN", "PROJECT")
    connn.connect()
    
    connn.close()