from models.sql_models import User
from services.creation import CreateData
from fastapi import APIRouter, HTTPException, Depends, status

router = APIRouter(
    prefix="/user", 
    tags=["Users"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_users(
        request: User, 
        process : CreateData = Depends(CreateData)
    ):
    try:
        validation = process.validate_user(request.Mail)
        if validation == None:
            new_user = process.create_user(request)
            return {"message": "user created successfully", "User id": new_user}
        return {"message": "User already exists", "Email": request.Mail}
    except HTTPException as he:
        raise he
    except Exception as error: 
        print(f"Error to create User: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.get("/")
async def validate(
        email: str, 
        process : CreateData = Depends(CreateData)
    ):    
    try:
        validation = process.validate_password(email)
        if not validation:
            raise HTTPException(status_code=404, detail="User not found")
        else:
            return validation
    except HTTPException as error:
        raise error
    except Exception as e:
        print(f"Error to validate user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    