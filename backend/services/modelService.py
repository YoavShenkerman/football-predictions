import os
import joblib
import pandas as pd
from sqlalchemy import create_engine

class MatchPredictor:
	def __init__(self, modelPath=None, dbPath=None):
		currentDir = os.path.dirname(__file__)

		if modelPath is None:
			modelPath = os.path.join(currentDir, "..", "models", "best_model.pkl")
		if dbPath is None:
			dbPath = os.path.join(currentDir, "..", "database", "football.db")

		if not os.path.exists(modelPath):
			raise FileNotFoundError(f"Model file {modelPath} not found")
		if not os.path.exists(dbPath):
			raise FileNotFoundError(f"DB file {dbPath} not found")

		self.model = joblib.load(modelPath)

		query = """
                SELECT m.date, \
                       ht.name AS homeTeam, \
                       at.name AS awayTeam, \
                       m.homeScore, \
                       m.awayScore, \
                       m.target, \
                       m.homeCode, \
                       m.awayCode, \
                       m.dayCode, \
                       m.homeGoalsForSum, \
                       m.homeGoalsAgainstSum, \
                       m.awayGoalsForSum, \
                       m.awayGoalsAgainstSum, \
                       m.homeWinRateRolling3, \
                       m.awayWinRateRolling3, \
                       m.homeWinRateRolling5, \
                       m.awayWinRateRolling5, \
                       m.homeWinRateExpanding, \
                       m.awayWinRateExpanding, \
                       m.homeTotalPoints, \
                       m.awayTotalPoints, \
                       m.homeAvgGoalsFor, \
                       m.homeAvgGoalsAgainst, \
                       m.awayAvgGoalsFor, \
                       m.awayAvgGoalsAgainst, \
                       m.homeTotalWins, \
                       m.homeTotalLosses, \
                       m.homeTotalDraws, \
                       m.awayTotalWins, \
                       m.awayTotalLosses, \
                       m.awayTotalDraws
                FROM matches m
                         JOIN teams ht ON m.homeTeamId = ht.id
                         JOIN teams at \
                ON m.awayTeamId = at.id \
		        """

		engine = create_engine(f"sqlite:///{dbPath}")
		self.fullDf = pd.read_sql(query, engine, parse_dates=["date"])

		teams = self.fullDf[["homeTeam", "homeCode"]].drop_duplicates()
		self.teamCodeMap = dict(zip(teams["homeTeam"], teams["homeCode"]))

		self.predictors = ["homeCode", "awayCode", "dayCode", "homeGoalsForSum", "homeGoalsAgainstSum",
              "awayGoalsForSum", "awayGoalsAgainstSum", "homeWinRateRolling3", "awayWinRateRolling3",
              "homeWinRateRolling5", "awayWinRateRolling5", "homeWinRateExpanding", "awayWinRateExpanding",
              "homeTotalPoints", "awayTotalPoints", "homeAvgGoalsFor", "homeAvgGoalsAgainst",
              "awayAvgGoalsFor", "awayAvgGoalsAgainst","homeTotalWins", "homeTotalLosses", "homeTotalDraws",
              "awayTotalWins", "awayTotalLosses", "awayTotalDraws"]

	def preprocess(self, data: dict) -> pd.DataFrame:
		"""
		:param data: {"homeTeam": str, "awayTeam": str, "date": "YYYY-MM-DD"}
		"""
		homeCode = self.teamCodeMap[data["homeTeam"].value]
		awayCode = self.teamCodeMap[data["awayTeam"].value]
		matchDate = pd.to_datetime(data["date"], dayfirst=True)
		dayCode = matchDate.dayofweek

		lastHome = self.fullDf[self.fullDf["homeTeam"] == data["homeTeam"].value].sort_values("date").iloc[-1]
		lastAway = self.fullDf[self.fullDf["awayTeam"] == data["awayTeam"].value].sort_values("date").iloc[-1]

		row = {
			"homeCode": homeCode,
			"awayCode": awayCode,
			"dayCode": dayCode,
			"homeGoalsForSum": lastHome["homeGoalsForSum"],
			"homeGoalsAgainstSum": lastHome["homeGoalsAgainstSum"],
			"awayGoalsForSum": lastAway["awayGoalsForSum"],
			"awayGoalsAgainstSum": lastAway["awayGoalsAgainstSum"],
			"homeWinRateRolling3": lastHome["homeWinRateRolling3"],
			"awayWinRateRolling3": lastAway["awayWinRateRolling3"],
			"homeWinRateRolling5": lastHome["homeWinRateRolling5"],
			"awayWinRateRolling5": lastAway["awayWinRateRolling5"],
			"homeWinRateExpanding": lastHome["homeWinRateExpanding"],
			"awayWinRateExpanding": lastAway["awayWinRateExpanding"],
			"homeTotalPoints": lastHome["homeTotalPoints"],
			"awayTotalPoints": lastAway["awayTotalPoints"],
			"homeAvgGoalsFor": lastHome["homeAvgGoalsFor"],
			"homeAvgGoalsAgainst": lastHome["homeAvgGoalsAgainst"],
			"awayAvgGoalsFor": lastAway["awayAvgGoalsFor"],
			"awayAvgGoalsAgainst": lastAway["awayAvgGoalsAgainst"],
			"homeTotalWins": lastHome["homeTotalWins"],
			"homeTotalLosses": lastHome["homeTotalLosses"],
			"homeTotalDraws": lastHome["homeTotalDraws"],
			"awayTotalWins": lastAway["awayTotalWins"],
			"awayTotalLosses": lastAway["awayTotalLosses"],
			"awayTotalDraws": lastAway["awayTotalDraws"],
		}

		return pd.DataFrame([row])

	def predict(self, data: dict) -> int:
		"""
		Return prediction for certain match
		:param data: {"homeTeam": str, "awayTeam": str, "date": "YYYY-MM-DD"}
		:return int: 0 - Draw, 1 - home team wins, 2 - away team wins
		"""
		x = self.preprocess(data)
		return int(self.model.predict(x)[0])