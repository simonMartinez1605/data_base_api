from pydantic import BaseModel
from datetime import datetime 
from typing import Optional, List

class User(BaseModel):
    Mail : str
    Password : bytes
    
class Folder(BaseModel):
    Path : str
    Status : str

class CreateFolderRequest(BaseModel):
    Folder : Folder
    Email : str

class Profile(BaseModel):
    Separation : int
    Name : str
    Base_document : str
    # Creation_date : datetime

class Anchor(BaseModel):
    Anchor_name : str
    Coord_x : float
    Coord_y : float
    Coord_w : float
    Coord_h : float

class Fields(BaseModel):
    Field_name : str
    Coord_x : float
    Coord_y : float
    Coord_w : float
    Coord_h : float

class CreateProfileRequest(BaseModel):
    Profile_data : Profile
    Anchor_data : Anchor
    Field_list : List[Fields]
    Email : str
    Folder_path : str


class SaveDocumentQueues(BaseModel):
    Email : str
    Folder_path : str
    Source_path : str
    Status : str