import os
import uvicorn
from dotenv import load_dotenv
from services.get import GetValues
from services.update import UpdateData
from services.creation import CreateData
from services.keys import UserDataRepository
from fastapi import FastAPI, HTTPException, exceptions
from models.sql_models import User, CreateFolderRequest, CreateProfileRequest, SaveDocumentQueues, SaveExtractedData, ErrorData

load_dotenv()

connection_string = os.getenv('CONNECTION_STRING_SQL')

app = FastAPI()
values = GetValues()
process = CreateData()
updating = UpdateData()
keys = UserDataRepository()

#--------------------------------  Creations ------------------------------
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
async def create_anchor(request: CreateProfileRequest):
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
    
@app.post('/create_queue')
async def save_queues(request: SaveDocumentQueues):
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
        else:
            raise HTTPException(status_code=500, detail="Failed to save Data in database")
    except exceptions.FastAPIError as error:
        print(f"Error to save the extracted data: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post('/save_error')
async def save_errors(request: ErrorData):
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
    except exceptions.FastAPIError as error:
        print(f"Error to save Errors: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

#-------------------------------- Get ------------------------------

@app.get('/folders')
async def get_folders(email):
    try:
        user_id = values.get_user_id(email)

        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        folders = values.get_folders(user_id)
        if not folders:
            raise HTTPException(status_code=404, detail="Folders not found")
        else:
            return folders
    except exceptions.FastAPIError as error:
        print(f"Error to save Errors: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@app.get('/queue_data')
async def get_queue_data(email): 
    try:
        user_id = values.get_user_id(email)

        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        data = values.get_queue_data(user_id)
        if not data:
            raise HTTPException(status_code=404, detail="Queue not found")
        else:
            return data
    except exceptions.FastAPIError as error:
        print(f"Error to get Queues: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get('/anchors')
async def get_anchors(email, folder_path):
    try:
        user_id = values.get_user_id(email)

        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        anchor = values.get_anchors(folder_path, user_id)

        if not anchor:
            raise HTTPException(status_code=404, detail="Anchor not found")
        else:
            return anchor
    except exceptions.FastAPIError as error:
        print(f"Error to get Anchor: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get('/fields')
async def get_fields(anchor_id):
    try:
        fields = values.get_fields(anchor_id)
        if not fields:
            raise HTTPException(status_code=404, detail="Fields not found")
        else:
            return fields
    except exceptions.FastAPIError as error:
        print(f"Error to get Fields: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get('get_errors')
async def get_errors(email):
    try:
        user_id = values.get_user_id(email)

        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        errors = values.get_errors(user_id)

        if not errors:
            raise HTTPException(status_code=404, detail="Errors not found")
        else:
            return errors
    except exceptions.FastAPIError as error:
        print(f"Error to get Errors: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/validate_password")
async def validate(email: str):    
    try:
        return process.validate_password(email)
    except exceptions.FastAPIError as error:
        print(f"Error to validate password: {error}")
        return 401


app.patch('/update_folder_status')
async def update_folder_status(email, folder_path, new_status):
    try:
        user_id = values.get_user_id(email)
        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        folder_id = values.get_folder_id(folder_path, user_id)
        if not folder_id:
            raise HTTPException(status_code=404, detail="Folder not found")

        update = updating.update_folder_status(folder_id, new_status)
        if not update:
            raise HTTPException(status_code=500, detail="Unable to update Folder Status")
        else:
            return update
    except exceptions.FastAPIError as error:
        print(f"Error to get Errors: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=7000,
        reload=True,
        log_level="info"
    )