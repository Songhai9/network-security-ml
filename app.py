import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from starlette.responses import RedirectResponse
from uvicorn import run as app_run

from networksecurity.exception.exception import NetworkSecurityException

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
        # Load training dependencies only when training is requested.
        from networksecurity.pipeline.training_pipeline import TrainingPipeline

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
