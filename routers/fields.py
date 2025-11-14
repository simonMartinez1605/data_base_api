from services.get import GetValues
from fastapi import APIRouter, HTTPException, Depends

router = APIRouter(
    prefix="/fields",
    tags=["Fields"]
)

@router.get('/')
async def get_fields(
        anchor_id : str, 
        values : GetValues = Depends(GetValues)
    ):
    try:
        fields = values.get_fields(anchor_id)
        if not fields:
            raise HTTPException(status_code=404, detail="Fields not found")
        else:
            return fields
    except HTTPException as he:
        raise he
    except Exception as error:
        print(f"Error to get Fields: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
