from fastapi import FastAPI
from routes import predictions

app = FastAPI()

app.include_router(predictions.router)