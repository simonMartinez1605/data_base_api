from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    Mail: str
    Password : bytes
    Server_User : str
    Server_Password : str
    Path_Share_Folder : str
    Server_IP : str
    Sharepoint_Url : str
    List_Name : str
    Client_ID : str
    Client_Secret : str