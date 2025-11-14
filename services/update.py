import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

class UpdateData:
    def __init__(self):
        self.sql_connection_str = os.getenv('CONNECTION_STRING_SQL')

    def update_folder_status(self, folder_id, status):
        sql_query = """
            UPDATE Folders
            SET status = ?
            OUTPUT INSERTED.status
            WHERE folder_id = ?
        """

        try:
            with pyodbc.connect(self.sql_connection_str) as cnxn:
                query_params = (status, folder_id)
                
                cursor = cnxn.cursor()
                cursor.execute(sql_query, query_params)

                new_status = cursor.fetchone()[0]
                cnxn.commit()

                return new_status
        except pyodbc.Error as ex:
            sqlstate =ex.args[0]
            print(f"Error to update folder status (SQLSTATE: {sqlstate}): {ex}")
            return None
        
    def update_error_status(self, error_id, status):
        sql_query = """
            UPDATE Errors
            SET status = ?
            OUTPUT INSERTED.status
            WHERE error_id = ?
        """

        try:
            with pyodbc.connect(self.sql_connection_str) as cnxn: 
                query_params = (status, error_id)

                cursor = cnxn.cursor()
                cursor.execute(sql_query, query_params)

                new_status = cursor.fetchone()[0]
                cnxn.commit()

                return new_status
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error to update error status (SQLSTATE: {sqlstate}) {ex}")
            return None