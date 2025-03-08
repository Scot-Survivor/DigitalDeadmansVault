import os
import fastapi
import logging

from fastapi import FastAPI
from sqlmodel import SQLModel
from vault.models import engine
from vault.routers import auth, docs
from vault.config import get_main_config
from fastapi_pagination import add_pagination

config = get_main_config()
logging.basicConfig(level=logging.DEBUG)
app = FastAPI()
app.include_router(auth.router)
app.include_router(docs.router)
add_pagination(app)  # include pagination support


@app.on_event("startup")
async def startup_event():
    logging.info("Starting up")
    logging.debug("Building database connection")
    SQLModel.metadata.create_all(engine)
    logging.debug("Checking file paths")
    os.makedirs(config.file_save_path, exist_ok=True)


@app.on_event("shutdown")
async def shutdown_event():
    logging.info("Shutting down")
    logging.debug("Closing database connection")
    engine.dispose()


@app.get("/")
async def root():
    """Return 404 on root for now"""
    return fastapi.Response(status_code=404)
