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