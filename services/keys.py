import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

class UserDataRepository:
    """
    Clase responsable de obtener los datos de configuración del usuario
    desde la base de datos SQL.
    """
    def __init__(self):
        self.connection_string = os.getenv('CONNECTION_STRING_SQL')
        if not self.connection_string:
            raise ValueError("La variable de entorno 'CONNECTION_STRING_SQL' no está definida.")

    def get_all_user_data(self, mail):
        """
        Obtiene toda la configuración del usuario (Sharepoint y Servidor)
        en una sola consulta a la base de datos.
        """
        # La consulta SQL que une las dos tablas por la columna 'Mail'
        sql_query = """
            SELECT
                sp.Url, sp.List_name, sp.Client_ID, sp.Client_Secret,
                sv.Server_User, sv.Password, sv.Path_Share_Folder, sv.Server_IP, 
                tk.Tokens
            FROM
                Sharepoint AS sp
            INNER JOIN
                Server AS sv ON sp.Mail = sv.Mail
            INNER JOIN
                Tokens AS tk ON sp.Mail = tk.Mail
            WHERE
                sp.Mail = ?
        """
        
        try:
            # El 'with' se encarga de abrir y cerrar la conexión de forma segura
            with pyodbc.connect(self.connection_string) as cnxn:
                cursor = cnxn.cursor()
                cursor.execute(sql_query, mail)
                row = cursor.fetchone()

                if row:
                    # Construimos el diccionario con todos los datos
                    user_data = {
                        "Url": row.Url,
                        "List_name": row.List_name,
                        "Client_ID": row.Client_ID,
                        "Client_Secret": row.Client_Secret,
                        "Server_User": row.Server_User,
                        "Server_Password": row.Password,
                        "Path_Share_Folder": row.Path_Share_Folder,
                        "Server_IP": row.Server_IP, 
                        "Tokens" : row.Tokens, 
                        "Email" : mail
                    }
                    return user_data
                else:
                    # El usuario no fue encontrado en la base de datos
                    print(f"Don't found data for the user: {mail}")
                    return None

        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error to search data (SQLSTATE: {sqlstate}): {ex}")
            return None
        
    def tokens(self, email):
        sql_query = f"SELECT Tokens From Tokens WHERE Mail = ?"
        try:
            with pyodbc.connect(self.connection_string) as cnxn:
                cursor = cnxn.cursor()
                cursor.execute(sql_query, email)
                row = cursor.fetchone()

                if row:
                    return row[0]
                return None
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error to get tokens (SQLSTATE: {sqlstate}): {ex}")
            return None
        
    def update_tokens_in_db(self, mail, tokens_used):

        tokens_in_db = self.tokens(mail)

        if tokens_in_db != None and tokens_in_db > 0:
            try:
                with pyodbc.connect(self.connection_string) as cnxn:
                    cursor = cnxn.cursor()
                    total_tokens = tokens_in_db - tokens_used
                    sql_query_update = f"""
                    UPDATE Tokens
                    SET Tokens = ?
                    WHERE Mail = ?
                    """
                    cursor.execute(sql_query_update, total_tokens, mail)
                    cnxn.commit()
                    return total_tokens
            except pyodbc.Error as ex:
                sqlstate = ex.args[0]
                print(f"Error to update tokens (SQLSTATE: {sqlstate}): {ex}")
                return None
        else:
            return None