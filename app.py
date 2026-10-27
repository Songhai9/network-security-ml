import sys
import os
from xmlrpc import client

import certifi

from networksecurity.constant.training_pipeline import DATA_INGESTION_COLLECTION_NAME, DATA_INGESTION_DATABASE_NAME
ca = certifi.where()

from dotenv import load_dotenv
load_dotenv()

monogodb_url = os.getenv("MONGODB_URL")
print(monogodb_url)

import pymongo

from networksecurity.app_logging.logger import logger
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.pipeline.training_pipeline import TrainingPipeline

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Request
from uvicorn import run as app_run
from fastapi.responses import Response
from starlette.responses import RedirectResponse

import pandas as pd

from networksecurity.utils.main_utils.utils import load_object

database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")


@app.get("/train")
async def train_route():
    try:
        training_pipeline = TrainingPipeline()
        training_pipeline.run_pipeline()
        return Response("Training successful!!")
    except Exception as e:
        raise NetworkSecurityException(e, sys)

if __name__ == "__main__":
    try:
        app_run(app, host="localhost", port=8000)
    except Exception as e:
        raise NetworkSecurityException(e, sys)