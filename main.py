import sys
import os
sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI
from routers import router
from repository import init_db
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

init_db()

## cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api", tags=["api"])
