import os
import pyodbc
from models.users import User
from dotenv import load_dotenv

load_dotenv()

class UsersFunctions():
    def __init__(self):
        self.sql_connection_str = os.getenv('CONNECTION_STRING_SQL')

    def create_user(self, req:User):
        try:
            cnxn = pyodbc.connect(self.sql_connection_str)
            password_hash_string = req.Password.decode('utf-8')
            
            sql_query = "INSERT INTO Users (Mail, Password) VALUES (?, ?)"
            
            params_tuple = (req.Mail, password_hash_string)
            
            cursor = cnxn.cursor()
            cursor.execute(sql_query, params_tuple)
            
            cnxn.commit()
            return 201
            
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error in SQL connection to create User: {sqlstate}")
            # Print the full error message from the database for more details
            print(f"Full error message: {ex}") 
            return 403

    def create_sp_keys(self, fields:User):
        
        try:
            cnxn = pyodbc.connect(self.sql_connection_str)
            sql_query = "INSERT INTO Sharepoint (Mail, Url, List_name, Client_ID, Client_Secret) VALUES (?, ?, ?, ?, ?)"
            params_tuple = (fields.Mail, fields.Sharepoint_Url, fields.List_Name, fields.Client_ID, fields.Client_Secret)

            cursor = cnxn.cursor()
            cursor.execute(sql_query, params_tuple)
            cnxn.commit()
            return 201
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error in SQL connection to create Sharepoint data: {sqlstate}")
            # Print the full error message from the database for more details
            print(f"Full error message: {ex}") 
            return 403

    def create_server_keys(self, fields : User):
        try:
            cnxn = pyodbc.connect(self.sql_connection_str)
            sql_query = "INSERT INTO Server (Mail, Server_User, Password, Path_Share_Folder, Server_IP) VALUES (?, ?, ?, ?, ?)"
            params_tuple = (fields.Mail, fields.Server_User, fields.Server_Password, fields.Path_Share_Folder, fields.Server_IP)

            cursor = cnxn.cursor()
            cursor.execute(sql_query, params_tuple)
            cnxn.commit()
            return 201
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error in SQL connection to create Server data: {sqlstate}")
            print(f"Full error message: {ex}") 
            return 403

    def validate_user(self, email):
        try:
            cnxn = pyodbc.connect(self.sql_connection_str)
            cursor = cnxn.cursor()
            cursor.execute("SELECT Mail From Users Where Mail = ?", email)
            row = cursor.fetchone()
            if row == None:
                return 404
            return 200
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error to get information in QSL: {sqlstate}")
            return 404

    def validate_password(self, email):
        try:
            cnxn = pyodbc.connect(self.sql_connection_str)
            cursor = cnxn.cursor()
            cursor.execute("SELECT Password From Users Where Mail = ? ", email)
            row = cursor.fetchone()
            return row[0].strip()
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error to validate password: {sqlstate}")
            return 401