from services.get import GetValues
from services.creation import CreateData
from models.sql_models import SaveExtractedData
from fastapi import APIRouter, HTTPException, Depends, status

router = APIRouter(
    prefix="/extracted_data", 
    tags=["Extracted Data"]
)

@router.post('/', status_code=status.HTTP_201_CREATED)
async def save_data(
        request: SaveExtractedData, 
        values : GetValues = Depends(GetValues), 
        process : CreateData = Depends(CreateData)
    ):
    try:
        user_id = values.get_user_id(request.Email)
        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        new_data = process.save_extracted_data(request, user_id)

        if new_data:
            return {"message":"New data save successfully", "Data_id": new_data}
        else:
            raise HTTPException(status_code=500, detail="Failed to save Data in database")
    except HTTPException as he: 
        raise he
    except Exception as error:
        print(f"Error to save the extracted data: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")