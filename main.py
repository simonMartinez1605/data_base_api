import uvicorn
from fastapi import FastAPI
from routers import anchors, errors, extracted_data, fields, folders, profiles, queues, users

app = FastAPI()

app.include_router(users.router)
app.include_router(profiles.router)
app.include_router(folders.router)
app.include_router(fields.router)
app.include_router(extracted_data.router)
app.include_router(errors.router)
app.include_router(anchors.router)
app.include_router(queues.router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=7000,
        reload=True,
        log_level="info"
    )