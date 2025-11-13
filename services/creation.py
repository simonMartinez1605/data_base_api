import os
import json
import pyodbc
from dotenv import load_dotenv
from services.get import GetValues
from models.sql_models import User, Folder, Profile, Anchor, SaveDocumentQueues, SaveExtractedData, ErrorData

load_dotenv()

class CreateData():
    def __init__(self):
        self.sql_connection_str = os.getenv('CONNECTION_STRING_SQL')
        self.get_values = GetValues()

    def create_user(self, user:User):
        sql_query = """
            INSERT INTO Users (email, password)
            OUTPUT INSERTED.user_id
            VALUES (?, ?)
        """
        try:
            with pyodbc.connect(self.sql_connection_str) as cnxn:
                password_hash_string = user.Password.decode('utf-8')
                
                params_tuple = (user.Mail, password_hash_string)
                
                cursor = cnxn.cursor()
                cursor.execute(sql_query, params_tuple)
                
                user_id = cursor.fetchone()[0]
                cnxn.commit()
                return user_id
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error in SQL connection to create User (SQLSTATE : {sqlstate}) Error: {ex}")
            return None
        
    def create_folder(self, folder:Folder, user_id):
        sql_query = """
            INSERT INTO Folders (user_id, path, status)
            OUTPUT INSERTED.folder_id
            VALUES (?, ?, ?)
        """
        try:
            with pyodbc.connect(self.sql_connection_str) as cnxn:
                params_tuple = (user_id, folder.Path, folder.Status)

                cursor = cnxn.cursor()
                cursor.execute(sql_query, params_tuple)

                folder_id = cursor.fetchone()[0]
                cnxn.commit()
                return folder_id
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error in SQL connnection to save Queue (SQLSTATUS: {sqlstate}) Error: {ex}")
            return None

    def create_profile(self, profile: Profile, anchor: Anchor, fields_list, folder_path, user_id):
        sql_insert_profile = """
            INSERT INTO Profiles (user_id, separation, name, base_document, creation_date)
            OUTPUT INSERTED.profile_id
            VALUES (?, ?, ?, ?, GETDATE())
        """

        sql_insert_anchor = """
            INSERT INTO Anchors (profile_id, anchor_name, coord_x, coord_y, coord_w, coord_h)
            OUTPUT INSERTED.anchor_id
            VALUES (?, ?, ?, ?, ?, ?)
        """

        sql_insert_fields = """
            INSERT INTO fields (anchor_id, field_name, coord_x, coord_y, coord_w, coord_h)
            VALUES (?, ?, ?, ?, ?, ?)
        """

        sql_folder_profile_link = """
            INSERT INTO FolderProfileLink (folder_id, profile_id)
            OUTPUT INSERTED.link_id
            VALUES (?, ?)
        """

        new_profile_id = None
        new_anchor_id = None

        try:
            folder_id = self.get_values.get_folder_id(folder_path, user_id)

            # 1. Validación de lógica de negocio (antes de la transacción)
            if not folder_id: 
                print(f"Error: No se encontró el folder_id para la ruta {folder_path} y usuario {user_id}")
                return None # Devolvemos None, no un raise
            
            # 2. El 'with' maneja la transacción (COMMIT/ROLLBACK)
            with pyodbc.connect(self.sql_connection_str) as cnxn:
                cursor = cnxn.cursor()

                # --- Perfil ---
                profile_params = (user_id, profile.Separation, profile.Name, profile.Base_document)
                cursor.execute(sql_insert_profile, profile_params)
                
                # 3. Forma segura de obtener el ID
                row = cursor.fetchone()
                if not row:
                    raise Exception (f"Fallo al crear el Perfil {profile.Name}, no se retornó ID.")
                new_profile_id = row[0]

                # --- Ancla ---
                anchor_params = (new_profile_id, anchor.Anchor_name, anchor.Coord_x, anchor.Coord_y, anchor.Coord_w, anchor.Coord_h)
                cursor.execute(sql_insert_anchor, anchor_params)
                
                row = cursor.fetchone()
                if not row:
                    raise Exception (f"Fallo al crear el Ancla {anchor.Anchor_name}, no se retornó ID.")
                new_anchor_id = row[0]

                # --- Campos ---
                fields_params_list = [
                    (new_anchor_id, field.Field_name, field.Coord_x, field.Coord_y, field.Coord_w, field.Coord_h)
                    for field in fields_list
                ]
                cursor.executemany(sql_insert_fields, fields_params_list)
                print(f"Fields inserted {len(fields_params_list)}")

                # --- Link ---
                folder_profile_link_params = (folder_id, new_profile_id)
                cursor.execute(sql_folder_profile_link, folder_profile_link_params)

                row = cursor.fetchone()
                if not row:
                    raise Exception ("Fallo al crear la conexión entre Perfil y Folder.")
                link_id = row[0]
                
                print("Transacción completada exitosamente.")
                # 4. Devolvemos el ID como señal de éxito
                return link_id

        # 5. Múltiples bloques 'except'
        except pyodbc.Error as ex:
            # Error específico de la base de datos (ej. violación de constraint)
            sqlstate = ex.args[0]
            print(f"Error de SQL al crear el perfil (SQLSTATE: {sqlstate}): {ex} ")
            return None # Devolvemos None
        except Exception as e:
            # Captura todo lo demás (ej. 'TypeError: NoneType is not subscriptable' o tus 'raise Exception')
            print(f"Error inesperado al crear el perfil: {e}")
            return None # Devolvemos None

    def create_queue(self, user_id, profile_id, folder_id, DocumentQueue: SaveDocumentQueues):
        sql_query = """
            INSERT INTO DocumentQueue (user_id, profile_id, folder_id, source_path, status, creation_timestamp)
            OUTPUT INSERTED.document_id
            VALUES (?, ?, ?, ?, ?, GETDATE())
        """
        try:
            with pyodbc.connect(self.sql_connection_str) as cnxn:
                
                queue_params = (user_id, profile_id, folder_id, DocumentQueue.Source_path, DocumentQueue.Status)

                cursor = cnxn.cursor()
                cursor.execute(sql_query, queue_params)

                queue_id = cursor.fetchone()[0]
                cnxn.commit()

                return queue_id
        except pyodbc.Error as ex: 
            sqlstate = ex.args[0]
            print(f"Error in SQL connnection to save Queue (SQLSTATUS: {sqlstate}) Error: {ex}")
            return None
    
    def save_extracted_data(self, DataToSave: SaveExtractedData, user_id):
        sql_query = """
            INSERT INTO ExtractedData (document_id, page_start, page_end, extracted_json, is_approved, qa_user_id, qa_timestamp)
            OUTPUT INSERTED.data_id
            VALUES (?, ?, ?, ?, ?, ?, GETDATE())
        """

        try:
            with pyodbc.connect(self.sql_connection_str) as cnxn: 
                json_string = json.dumps(DataToSave.Extracted_json)
                data_params = (DataToSave.Document_id, DataToSave.Page_start, DataToSave.Page_end, json_string, DataToSave.Is_approved, user_id)
                
                cursor = cnxn.cursor()
                cursor.execute(sql_query, data_params)

                data_id = cursor.fetchone()[0]
                cnxn.commit()

                return data_id
        except pyodbc.Error as ex: 
            sqlstate = ex.args[0]
            print(f"Error in SQL connnection to save Data (SQLSTATUS: {sqlstate}) Error: {ex}")
            return None

    def save_errors(self, ErrorData: ErrorData, user_id, folder_id):
        sql_query = """
            INSERT INTO Errors (folder_id, user_id, error_msg, document_path, status, error_date)
            OUTPUT INSERTED.error_id
            VALUES (?, ?, ?, ?, ?, GETDATE())
        """
        try:
            with pyodbc.connect(self.sql_connection_str) as cnxn:
                errors_params = (folder_id, user_id, ErrorData.Error_msg, ErrorData.Document_path, ErrorData.Status)

                cursor = cnxn.cursor()
                cursor.execute(sql_query, errors_params)

                error_id = cursor.fetchone()[0]
                cnxn.commit()

                return error_id
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error to save Errros data (SQLSTATE: {sqlstate}): {ex}")
            return None 

    def validate_user(self, email):
        try:
            with pyodbc.connect(self.sql_connection_str) as cnxn:
                cursor = cnxn.cursor()
                cursor.execute("SELECT email From Users Where email = ?", email)
                row = cursor.fetchone()[0]
                if row == None:
                    return None
                return row
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error to get user information in QSL: {sqlstate}")
            return None

    def validate_password(self, email):
        try:
            cnxn = pyodbc.connect(self.sql_connection_str)
            cursor = cnxn.cursor()
            cursor.execute("SELECT password From Users Where email = ? ", email)
            row = cursor.fetchone()
            return row[0].strip()
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error to validate password: {sqlstate}")
            return 401
        