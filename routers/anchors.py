from services.get import GetValues
from fastapi import APIRouter, HTTPException, Depends

router = APIRouter(
    prefix="/anchor", 
    tags=["Anchors"]
)

@router.get('/')
async def get_anchors(
        email : str, 
        folder_path : str,
        values : GetValues = Depends(GetValues)
    ):
    try:
        user_id = values.get_user_id(email)

        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        profile_id = values.get_profile_id(folder_path, user_id)

        if not profile_id:
            raise HTTPException(status_code=404, detail="Profile Not found")
        
        anchor = values.get_anchors(profile_id)

        if not anchor:
            raise HTTPException(status_code=404, detail="Anchor not found")
        else:
            return anchor
    except HTTPException as he:
        raise he
    except Exception as error:
        print(f"Error to get Anchor: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")