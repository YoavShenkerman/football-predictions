from fastapi import APIRouter
from pydantic import BaseModel
from services.modelService import MatchPredictor
from datetime import date
from utils.teamNameMapping import teamsEnum
import redis
import json
from hashlib import sha256

router = APIRouter()
r = redis.Redis(host='localhost', port=6379, db=0)
predictor = MatchPredictor()

class MatchData(BaseModel):
	homeTeam: teamsEnum
	awayTeam: teamsEnum
	date: date

def makeCacheKey(data: dict):
	dataStr = json.dumps(data, sort_keys=True)
	return sha256(dataStr.encode()).hexdigest()

def formatPrediction(target, homeTeam, awayTeam):
	if target == 1:
		return f"{homeTeam} will win"
	elif target == 2:
		return f"{awayTeam} will win"
	else:
		return "Draw"

@router.post("/predict")
def predictMatch(data: MatchData):
	key = makeCacheKey({
		"homeTeam": data.homeTeam.value,
		"awayTeam": data.awayTeam.value,
		"date": str(data.date)
	})
	cached = r.get(key)
	if cached:
		return {"prediction": cached.decode("utf-8")}

	x = predictor.predict(data.model_dump())
	prediction = formatPrediction(x, data.homeTeam.value, data.awayTeam.value)

	r.setex(key, 86400, prediction)

	return {"prediction": prediction}

