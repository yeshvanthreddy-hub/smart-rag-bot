from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.upload_router import router as upload_router
from app.routers.chat_router import router as chat_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(chat_router)