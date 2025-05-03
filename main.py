import sys
import os
sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI
from routers import router
from repository import init_db

app = FastAPI()

init_db()

app.include_router(router, prefix="/api", tags=["api"])
