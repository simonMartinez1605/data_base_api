from models.sql_models import User
from services.get import GetValues
from services.creation import CreateData
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, Depends, status
from auth.auth import create_access_token, get_password_hash, verify_password

router = APIRouter(
    prefix="/user", 
    tags=["Users"]
)

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_users(
        request: User, 
        process : CreateData = Depends(CreateData)
    ):
    try:
        validation = process.validate_user(request.Mail)
        if validation == None:
            
            hashed_password = get_password_hash(request.Password)

            user_model_with_hashed_pass = request.copy(update={"Password":hashed_password})

            new_user = process.create_user(user_model_with_hashed_pass)
            return {"message": "user created successfully", "User id": new_user}
        return {"message": "User already exists", "Email": request.Mail}
    except HTTPException as he:
        raise he
    except Exception as error: 
        print(f"Error to create User: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.get("/token")
async def login_for_access_token(
        form_data : OAuth2PasswordRequestForm = Depends(),
        values : GetValues = Depends(GetValues),
        process : CreateData = Depends(CreateData)
    ):
    try:
        email = form_data.username
        password = form_data.password

        hashed_password_from_db = process.validate_password(email)

        if not hashed_password_from_db:
            raise HTTPException(status_code=404, detail="User not found")
        
        is_password_correct = verify_password(password, hashed_password_from_db)

        if not is_password_correct:
            raise HTTPException(status_code=404, detail="Incorrect Email or Password")

        access_token = create_access_token(data={"sub":email})

        return {"access_token": access_token, "token_type":"bearer"}

    except HTTPException as error:
        raise error
    except Exception as e:
        print(f"Error to validate user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    