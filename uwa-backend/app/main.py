from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.config import CORS_ORIGINS
from app.routers import auth_router
from app.user_data import user_data_router
from umd_api import router as umd_api_router

app = FastAPI(
    title="UWA Backend",
    version="1.0.0",
    docs_url="/docs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(umd_api_router, prefix="/umd-api", tags=["UMD Courses"])
app.include_router(user_data_router, prefix="/user_data", tags=["Get and Manipulate User Data"])

@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    uvicorn.run("app.main:app",
        host="localhost",
        port=8000,
        reload=True
    )   
