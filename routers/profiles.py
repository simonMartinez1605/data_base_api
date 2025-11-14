from services.get import GetValues
from services.creation import CreateData
from models.sql_models import CreateProfileRequest
from fastapi import APIRouter, HTTPException, Depends, status

router = APIRouter(
    prefix="/profile", 
    tags=["Profiles"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_anchor(
        request: CreateProfileRequest, 
        values : GetValues = Depends(GetValues) ,
        process : CreateData = Depends(CreateData)
    ):
    try:
        user_id = values.get_user_id(request.Email)
        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        validate_profile = values.get_profile_id(request.Folder_path, user_id)

        if validate_profile: 
            raise HTTPException(status_code=409, detail=f"The user already create this profile {request.Profile_data.Name}")
        
        new_profile = process.create_profile(
            request.Profile_data, 
            request.Anchor_data, 
            request.Field_list, 
            request.Folder_path,
            user_id
        )
        
        if new_profile:
            return {"message": "Profile created successfully", "profile": new_profile}
        else:
            raise HTTPException(status_code=500, detail="Failed to create profile in database")
    except HTTPException as he:
        raise he
    except Exception as error:
        print(f"Error to create profile: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@router.get("/")
async def get_profile(
        email : str, 
        values : GetValues = Depends(GetValues)
    ):
    try:
        user_id = values.get_user_id(email)
        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        profile = values.get_profiles(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profiles no found")
        else:
            return profile
    except HTTPException as he:
        raise he
    except Exception as error:
        print(f"Error to get Queues: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")