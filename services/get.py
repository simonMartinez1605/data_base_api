import os
import json
import pyodbc
from dotenv import load_dotenv

load_dotenv()

class GetValues:
    def __init__(self):
        self.connection_string = os.getenv('CONNECTION_STRING_SQL')
        if not self.connection_string:
            raise ValueError("The env variable does not exits: 'CONNECTION_STRING_SQL'")
        
    def get_user_id(self, email):
        sql_query = """
            SELECT user_id FROM Users WHERE email = ?
        """
        try:
            with pyodbc.connect(self.connection_string) as cnxn:
                cursor = cnxn.cursor()
                cursor.execute(sql_query, email)
                row = cursor.fetchone()

                if row:
                    return row.user_id
                else:
                    print(f"Don't found data for the user: {email}")
                    return None
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error to get user id (SQLSTATE: {sqlstate}): {ex}")
            return None
        
    def get_folders(self, user_id):
        sql_query = """
            SELECT 
                f.path, 
                f.status
            FROM Folders AS f
            WHERE f.user_id = ?
        """

        folders_data = []

        try:
            with pyodbc.connect(self.connection_string) as cnxn:
                cursor = cnxn.cursor()
                cursor.execute(sql_query, user_id)
                rows = cursor.fetchall()

                if rows:
                    for row in rows:
                        data = {
                            "Path" : row.path, 
                            "Status" : row.status
                        }
                        folders_data.append(data)
                    return folders_data
                else:
                    print(f"Any Folder associate with this user")
                    return None
                
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error to get folders (SQLSTATE: {sqlstate}): {ex}")
            return None      
    
    def get_folder_id(self, folder_path, user_id):
        sql_query = """
            SELECT
                folder_id 
            FROM Folders 
            WHERE path = ? 
            AND user_id = ?
        """

        try:
            with pyodbc.connect(self.connection_string) as cnxn:
                cursor = cnxn.cursor()
                cursor.execute(sql_query, folder_path, user_id)
                row = cursor.fetchone()
                if row:
                    return row.folder_id
                else:
                    print(f"This folder does not exists or the user does not have the acces to this folder: {folder_path}")
                    return None
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error to get folder id (SQLSTATE: {sqlstate}): {ex}")
            return None
        
    def get_queue_data(self, user_id):
        sql_query = """
            SELECT 
                d.source_path, 
                e.data_id, 
                e.extracted_json, 
                e.page_start, 
                e.page_end
            FROM ExtractedData AS e
            INNER JOIN 
                DocumentQueue AS d ON e.document_id = d.document_id
            WHERE 
                d.status = 'Pending' AND e.qa_user_id = ?
        """
        queue_data = []
        try:
            with pyodbc.connect(self.connection_string) as cnxn:
                cursor = cnxn.cursor()
                cursor.execute(sql_query, user_id)
                rows = cursor.fetchall()
                if rows:
                    for row in rows:
                        parsed_json = None

                        if row.extracted_json:
                            try:
                                parsed_json = json.loads(row.extracted_json)
                            except json.JSONDecodeError:
                                print(f"Warning: JSON Format invalid for data id {row.data_id}")
                        
                        data = {
                            "path" : row.source_path,
                            "data_id": row.data_id,
                            "json": parsed_json,
                            "page_start" : row.page_start,
                            "page_end" : row.page_end
                        }
                        queue_data.append(data)
                    return queue_data
                else:
                    print(f"This user does not have any data pending")
                    return None
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error to get queue data (SQLSTATE: {sqlstate}): {ex}")
            return None
    
    def get_profile_id(self, folder_path, user_id):
        sql_query_profile_id = """
            SELECT profile_id FROM FolderProfileLink WHERE folder_id = ?
        """

        folder_id = self.get_folder_id(folder_path, user_id)

        try:
            with pyodbc.connect(self.connection_string) as cnxn:
                cursor = cnxn.cursor()
                cursor.execute(sql_query_profile_id, folder_id)
                row = cursor.fetchone()
                if row:
                    return row.profile_id
                else:
                    print(f"This folder does not link with any profile: {folder_path}")
                    return None
        except pyodbc.Error as ex: 
            sqlstate = ex.args[0]
            print(f"Error to get profile id (SQLSTATE: {sqlstate}): {ex}")
            return None
        
    def get_anchors(self, profile_id):
        sql_query = """
            SELECT
                a.anchor_name, 
                a.anchor_id,
                a.coord_x, 
                a.coord_y, 
                a.coord_w, 
                a.coord_h
            FROM Anchors AS a
            WHERE a.profile_id = ?
        """
        anchor_data = []

        try:
            with pyodbc.connect(self.connection_string) as cnxn:
                cursor = cnxn.cursor()
                cursor.execute(sql_query, profile_id)
                rows = cursor.fetchall()

                if rows:
                    for row in rows:
                        data = {
                            "anchor_name": row.anchor_name, 
                            "anchor_id" : row.anchor_id,
                            "coord_x" : row.coord_x, 
                            "coord_y" : row.coord_y, 
                            "coord_w"  : row.coord_w, 
                            "coord_h" : row.coord_h
                        }
                        anchor_data.append(data)
                    return anchor_data
                else:
                    print(f"Error to get anchors")
                    return None
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error to get Anchors (SQLSTATE: {sqlstate}): {ex}")
            return None
        
    def get_fields(self, anchor_id):
        sql_query = """
            SELECT
                fe.field_name, 
                fe.coord_x, 
                fe.coord_y, 
                fe.coord_w, 
                fe.coord_h
            FROM Fields AS fe
            WHERE fe.anchor_id = ?
        """

        fields_data = []
        try:
            with pyodbc.connect(self.connection_string) as cnxn:
                cursor = cnxn.cursor()
                cursor.execute(sql_query, anchor_id)
                rows = cursor.fetchall()
                if rows:
                    for row in rows:
                        data = {
                            "field_name" : row.field_name, 
                            "coord_x" : row.coord_x, 
                            "coord_y" : row.coord_y, 
                            "coord_w"  : row.coord_w, 
                            "coord_h" : row.coord_h
                        }
                        fields_data.append(data)
                    return fields_data
                else:
                    print(f"The anchor is no associate with any fields")
                    return None
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error to get fields (SQLSTATE: {sqlstate}): {ex}")
            return None

    def get_profiles(self, user_id):
        profile_sql_query = """
            SELECT
                p.profile_id, 
                p.separation, 
                p.name, 
                p.base_document, 
                p.creation_date
            FROM Profiles AS p
            WHERE user_id = ?
        """

        profile_data = []

        try:
            with pyodbc.connect(self.connection_string) as cnxn:
                cursor = cnxn.cursor()
                cursor.execute(profile_sql_query, user_id)

                profile_rows = cursor.fetchall()

                if profile_rows:
                    for row in profile_rows:
                        anchors = self.get_anchors(row.profile_id)
                        anchor_id = anchors[0]['anchor_id']
                        fields = self.get_fields(anchor_id)
                        data = {
                            "profile_id" : row.profile_id,
                            "name" : row.name, 
                            "separation" : row.separation, 
                            "base_document" : row.base_document, 
                            "creation_date" : row.creation_date, 
                            "anchors" : anchors, 
                            "fields" : fields
                        }
                        profile_data.append(data)
                    return profile_data
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error to get Profiles (SQLSTATE: {sqlstate}) {ex}")
            return None

    def get_errors(self, user_id):
        sql_query = """
            SELECT
                err.error_id,
                f.path,
                err.document_path, 
                err.error_msg,
                err.status, 
                err.error_date
            FROM Errors AS err
            JOIN Folders as f ON err.folder_id = f.folder_id
            WHERE err.status = 'Pending' AND err.user_id = ?
        """

        error_data = []
        try:
            with pyodbc.connect(self.connection_string) as cnxn:
                cursor = cnxn.cursor()
                cursor.execute(sql_query, user_id)
                rows = cursor.fetchall()
                if rows: 
                    for row in rows:
                        data = {
                            "error_id": row.error_id,
                            "folder_path" : row.path,
                            "document_path" : row.document_path, 
                            "error_msg" : row.error_msg, 
                            "status" : row.status, 
                            "error_date" : row.error_date 
                        }
                        error_data.append(data)
                        print(data)
                    return error_data
                else:
                    print("This user does not have errors... yet")
                    return None
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error to get Errors (SQLSTATE: {sqlstate}): {ex}")
            return None