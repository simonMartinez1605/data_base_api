import os
import uvicorn
from models.users import User
from dotenv import load_dotenv
from fastapi import FastAPI, exceptions
from services.keys import UserDataRepository
from services.create_user import UsersFunctions

load_dotenv()

connection_string = os.getenv('CONNECTION_STRING_SQL')

app = FastAPI()
process = UsersFunctions()
keys = UserDataRepository()

@app.post("/create_new_user")
async def creation(req:User):
    try:
        validation = process.validate_user(req.Mail)
        if validation == 404:
            try:
                process.create_sp_keys(req)
                process.create_server_keys(req)
                process.apply_tokens(req)
                return process.create_user(req)
            except exceptions.FastAPIError as e:
                print(f"Error to create data in sql data base: {e}")
                return 500
        return validation
    except exceptions.FastAPIError as error:
        print(f"Error to process data: {error}")
        return 400

@app.get("/validate_password")
async def validate(email: str):    
    try:
        return process.validate_password(email)
    except exceptions.FastAPIError as error:
        print(f"Error to validate password: {error}")
        return 401

@app.get("/get_all_keys")
async def get_all_keys(email:str):
    try:
        return keys.get_all_user_data(email)
    except exceptions.FastAPIError as error:
        print(f"Error to get sharepoint keys: {error}")
        return 401

@app.patch('/update_tokens')
async def update_tokens(email: str, tokens: int):
    try:
        if tokens < 0:
            return 0
        return keys.update_tokens_in_db(email, tokens)
    except exceptions.FastAPIError as error:
        print(f"Error to update Tokens quantity: {error}")
        return None
    
@app.get('/tokens')
async def tokens_quantity(email:str):
    try:
        return keys.tokens(email)
    except exceptions.FastAPIError as error:
        print(f"Error to get Tokens quantity: {error}")
        return False

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=7000,
        reload=True,
        log_level="info"
    )