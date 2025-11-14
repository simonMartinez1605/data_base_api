from services.get import GetValues
from services.update import UpdateData
from services.creation import CreateData
from models.sql_models import ErrorData, UpdateErrorStatus
from fastapi import APIRouter, HTTPException, Depends, status

router = APIRouter(
    prefix="/errors", 
    tags=["Errors"]
)

@router.post('/', status_code=status.HTTP_201_CREATED)
async def save_errors(
        request: ErrorData, 
        values : GetValues = Depends(GetValues), 
        process : CreateData = Depends(CreateData)
    ):
    try:
        user_id = values.get_user_id(request.Email)
        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        folder_id = values.get_folder_id(request.Folder_path, user_id)
        if not folder_id:
            raise HTTPException(status_code=404, detail="Folder not found")
        
        save_error = process.save_errors(request, user_id, folder_id)

        if save_error:
            return{"message":"New error saved successfully", "Error_id":save_error}
        else:
            raise HTTPException(status_code=500, detail="Failed to save Error")
    except HTTPException as he:
        raise he
    except Exception as error:
        print(f"Error to save Errors: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.get('/')
async def get_errors(
        email : str, 
        values : GetValues = Depends(GetValues),
    ):
    try:
        user_id = values.get_user_id(email)

        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        errors = values.get_errors(user_id)

        if not errors:
            raise HTTPException(status_code=404, detail="Errors not found")
        else:
            return errors
    except HTTPException as he:
        raise he
    except Exception as error:
        print(f"Error to get Errors: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.patch('/status')
async def update_error_status(
        request: UpdateErrorStatus, 
        updating : UpdateData = Depends(UpdateData)
    ):
    try:
        update = updating.update_error_status(request.Error_id, request.New_status)
        if not update:
            raise HTTPException(status_code=500, detail="Unable to update Errors status")
        return update
    except HTTPException as he: 
        raise he
    except Exception as error:
        print(f"Error to get Errors: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
