from services.get import GetValues
from services.creation import CreateData
from models.sql_models import SaveDocumentQueues
from fastapi import APIRouter, HTTPException, Depends, status

router = APIRouter(
    prefix="/queue", 
    tags=["Queues"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def save_queues(
        request: SaveDocumentQueues, 
        values : GetValues = Depends(GetValues), 
        process : CreateData = Depends(CreateData)
    ):
    try:
        user_id = values.get_user_id(request.Email)
        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        validate_folder = values.get_folder_id(request.Folder_path, user_id)
        if validate_folder == None: 
            raise HTTPException(status_code=409, detail=f"The user does not have this folder: {request.Folder_path}")
        
        validate_profile = values.get_profile_id(request.Folder_path, user_id)
        print(validate_profile)
        if not validate_profile: 
            raise HTTPException(status_code=409, detail=f"The user does not have anchor in this folder: {request.Folder_path}")
        
        new_queue = process.create_queue(user_id, validate_profile, validate_folder, request)
        if new_queue:
            return {"message":"Queue saved successfully", "Queue_id":new_queue}
        else:
            raise HTTPException(status_code=500, detail="Failed to save Queue in database")
    except HTTPException as he: 
        raise he
    except Exception as error:
        print(f"Error to create profile: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.get("/")
async def get_queue_data(
        email : str, 
        values : GetValues = Depends(GetValues), 
    ): 
    try:
        user_id = values.get_user_id(email)

        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        data = values.get_queue_data(user_id)
        if not data:
            raise HTTPException(status_code=404, detail="Queue not found")
        else:
            return data
    except HTTPException as he:
        raise he
    except Exception as error:
        print(f"Error to get Queues: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")