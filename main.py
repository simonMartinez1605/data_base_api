import os
import uvicorn
from dotenv import load_dotenv
from services.get import GetValues
from services.keys import UserDataRepository
from services.creation import UsersFunctions
from fastapi import FastAPI, HTTPException, exceptions
from models.sql_models import User, CreateFolderRequest, CreateProfileRequest, SaveDocumentQueues, SaveExtractedData

load_dotenv()

connection_string = os.getenv('CONNECTION_STRING_SQL')

app = FastAPI()
process = UsersFunctions()
keys = UserDataRepository()
values = GetValues()

@app.post('/create_user')
async def create_users(User: User):
    try:
        validation = process.validate_user(User.Mail)
        if validation == None:
            new_user = process.create_user(User)
            return {"message": "user created successfully", "folder_id": new_user}
        return {"message": "User already exists", "Email": User.Mail}
    except exceptions.FastAPIError as error: 
        print(f"Error to create User: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post('/create_folder')
async def create_folders(request: CreateFolderRequest):
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

    except exceptions.FastAPIError as error:
        print(f"Error to create folder: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post('/create_profile')
async def create_profiles(request: CreateProfileRequest):
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
    except exceptions.FastAPIError as error:
        print(f"Error to create profile: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@app.post('/save_queue')
async def save_queues(request: SaveDocumentQueues):
    try:
        user_id = values.get_user_id(request.Email)
        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        validate_folder = values.get_folder_id(request.Folder_path, user_id)
        if validate_folder: 
            raise HTTPException(status_code=409, detail=f"The user already create this Folder {request.Folder_path}")
        
        validate_profile = values.get_profile_id(request.Folder_path, user_id)
        if validate_profile: 
            raise HTTPException(status_code=409, detail=f"The user already create this profile {request.Folder_path}")
        
        new_queue = process.create_queue(user_id, validate_profile, validate_folder, request)
        if new_queue:
            return {"message":"Queue saved successfully", "Queue_id":new_queue}
        else:
            raise HTTPException(status_code=500, detail="Failed to create Queue in database")
    except exceptions.FastAPIError as error:
        print(f"Error to create profile: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
        
@app.post('/save_extracted_data')
async def save_data(request: SaveExtractedData):
    try:
        user_id = values.get_user_id(request.Email)
        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        new_data = process.save_extracted_data(request, user_id)

        if new_data:
            return {"message":"New data save successfully", "Data_id": new_data}
    except exceptions.FastAPIError as error:
        print(f"Error to save the extracted data: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/validate_password")
async def validate(email: str):    
    try:
        return process.validate_password(email)
    except exceptions.FastAPIError as error:
        print(f"Error to validate password: {error}")
        return 401


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=7000,
        reload=True,
        log_level="info"
    )