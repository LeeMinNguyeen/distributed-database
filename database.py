import pyodbc

def conn_info(server, database):
    # Define the connection string using Windows Authentication
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=NGUYIN\\NGUYIN;"
        "DATABASE=PROJECT;"
        "Trusted_Connection=yes;"
    )
    return conn_str

def connect(server, database):
    """Connect to the database
    
    Args:
        server (str): The server name
        database (str): The database name
    """
    try:
        conn = pyodbc.connect(conn_info(server, database))
        print("Connection successful")
        return conn
    except Exception as e:
        print(f"Error: {e}")

def close(conn):
    if 'conn' in locals():
        conn.close()
        print("Connection closed")
        
if __name__ == "__main__":
    conn = connect("NGUYIN\\NGUYIN", "PROJECT")
    close(conn)