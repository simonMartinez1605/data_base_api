from typing import List, Dict, Any
from pydantic import BaseModel

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

class SaveExtractedData (BaseModel):
    Document_id : int
    Page_start : int
    Page_end : int
    Extracted_json : Dict
    Is_approved : int
    Email : str

class ErrorData(BaseModel):
    Email : str
    Folder_path : str
    Error_msg : str
    Document_path : str

class UpdateFolderStatus(BaseModel):
    Email : str
    Folder_path : str
    New_status : str

class UpdateErrorStatus(BaseModel):
    Error_id : int
    New_status : str