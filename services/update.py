import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

class UpdateData:
    def __init__(self):
        self.sql_connection_str = os.getenv('CONNECTION_STRING_SQL')
