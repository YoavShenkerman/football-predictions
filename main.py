from fastapi import FastAPI
from pydantic import BaseModel
from modelService import MatchPredictor
from datetime import date
from teamNameMapping import teamsEnum
app = FastAPI()
predictor = MatchPredictor()

class MatchData(BaseModel):
	homeTeam: teamsEnum
	awayTeam: teamsEnum
	date: date

def formatPrediction(target, homeTeam, awayTeam):
	if target == 1:
		return f"{homeTeam} will win"
	elif target == 2:
		return f"{awayTeam} will win"
	else:
		return "Draw"

@app.post("/predict")
def predictMatch(data: MatchData):
	x = predictor.predict(data.model_dump())
	prediction = formatPrediction(x, data.homeTeam.value, data.awayTeam.value)
	return {"prediction": prediction}

