from fastapi import FastAPI
from backend.routes import predictions

app = FastAPI()

app.include_router(predictions.router)