from services.get import GetValues
from services.update import UpdateData
from services.creation import CreateData
from fastapi import APIRouter, HTTPException, Depends, status
from models.sql_models import CreateFolderRequest, UpdateFolderStatus

router = APIRouter(
    prefix="/folders", 
    tags=["Folders"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_folders(
    request: CreateFolderRequest, 
    values : GetValues = Depends(GetValues), 
    process : CreateData = Depends(CreateData)
):
    
    try:
        user_id = values.get_user_id(request.Email)
        if not user_id: 
            raise HTTPException(status_code=404, detail="User not found")
        
        validate_folder = values.get_folder_id(request.Folder.Path, user_id)
        if validate_folder: 
            raise HTTPException(status_code=409, detail=f"The user already create this folder {request.Folder.Path}")
        
        new_folder = process.create_folder(request.Folder, user_id)

        if new_folder:
            return {"message": "Folder created successfully", "folder_id": new_folder}
        else:
            raise HTTPException(status_code=500, detail="Failed to create folder in database")

    except HTTPException as he:
        raise he  # Re-lanza las excepciones HTTP que ya manejaste
    except Exception as e:
        print(f"Error to create folder: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.get("/")
async def get_folders(
    email: str, 
    values : GetValues = Depends(GetValues)
):
    try:
        user_id = values.get_user_id(email)
        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        folders = values.get_folders(user_id)
        if not folders:
            raise HTTPException(status_code=404, detail="Folders not found")
        else:
            return folders
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error to get Folders: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@router.patch("/status")
async def update_folder_status(
    request: UpdateFolderStatus, 
    values : GetValues = Depends(GetValues), 
    updating : UpdateData = Depends(UpdateData)
):
    try:
        user_id = values.get_user_id(request.Email)
        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        folder_id = values.get_folder_id(request.Folder_path, user_id)
        if not folder_id:
            raise HTTPException(status_code=404, detail="Folder not found")

        update = updating.update_folder_status(folder_id, request.New_status)
        if not update:
            raise HTTPException(status_code=500, detail="Unable to update Folder status")
        else:
            return update
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error to update folder status: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
