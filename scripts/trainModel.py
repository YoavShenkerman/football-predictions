import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import RandomizedSearchCV
import joblib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date

dbPath = r"C:\Users\yoavs\Desktop\אוניברסיטת תל אביב\פרוייקטים\פרוייקטים אישיים\football-predictions\database\football.db"
engine = create_engine("sqlite:///" + dbPath)
Session = sessionmaker(bind=engine)
session = Session()

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

fullDf = pd.read_sql(query, engine)

evalDate = "2025-02-01"
train = fullDf[fullDf["date"] < evalDate]
test = fullDf[fullDf["date"] >= evalDate]
predictors = ["homeCode", "awayCode", "dayCode", "homeGoalsForSum", "homeGoalsAgainstSum",
              "awayGoalsForSum", "awayGoalsAgainstSum", "homeWinRateRolling3", "awayWinRateRolling3",
              "homeWinRateRolling5", "awayWinRateRolling5", "homeWinRateExpanding", "awayWinRateExpanding",
              "homeTotalPoints", "awayTotalPoints", "homeAvgGoalsFor", "homeAvgGoalsAgainst",
              "awayAvgGoalsFor", "awayAvgGoalsAgainst","homeTotalWins", "homeTotalLosses", "homeTotalDraws",
              "awayTotalWins", "awayTotalLosses", "awayTotalDraws"]

xTrain, yTrain = train[predictors], train["target"]
xTest, yTest = test[predictors], test["target"]

weightOptions = [
	{0:1, 1:1, 2:1},
	{0:1.5, 1:1, 2:1.5},
	{0:2, 1:1, 2:2},
	{0:2.5, 1:1, 2:2.5},
	{0: 3, 1: 1, 2: 3},
]
candidates = {
	"RandomForest": (
		RandomForestClassifier(random_state=1),
		{
			"n_estimators": [100, 200, 400, 600],
			"max_depth": [10, 20, 30, None],
			"min_samples_split": [2, 3, 5, 10],
			"class_weight": weightOptions,
		}
	),
	"GradientBoosting":(
		GradientBoostingClassifier(random_state=1),
		{
			"n_estimators": [100, 200, 400],
			"learning_rate": [0.01, 0.05, 0.1],
			"max_depth": [3, 5, 7, 10, 20, None]
		}
	),
	"LogisticRegression":(
		LogisticRegression(max_iter=5000),
		{
			"C": [0.01, 0.1, 1, 10],
			"class_weight": ["balanced"] + weightOptions
		}
	)
}

bestModel = None
bestScore = -1
bestName = None

for name, (clf, params) in candidates.items():
	search = RandomizedSearchCV(clf, params, n_iter=25, cv=3, scoring="accuracy", n_jobs=-1, random_state=1)
	search.fit(xTrain, yTrain)
	preds = search.best_estimator_.predict(xTest)
	score = accuracy_score(yTest, preds)

	print(f"{name} | Best Params: {search.best_params_} | Accuracy: {score}")

	if score > bestScore:
		bestScore = score
		bestName = name
		bestModel = search.best_estimator_

print(f"Best Model: {bestName} (Accuracy: {bestScore})")

today = date.today()
xFinal, yFinal = finalDf = fullDf[predictors], fullDf["target"]

bestModel.fit(xFinal, yFinal)

joblib.dump(bestModel, "../models/best_model.pkl")
print("Model saved to best_model.pkl")


