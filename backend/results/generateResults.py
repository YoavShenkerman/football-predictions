import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from pathlib import Path
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

currentDir = os.path.dirname(__file__)
modelPath = os.path.join(currentDir, "..", "models", "best_model.pkl")
modelPath = os.path.abspath(modelPath)
model = joblib.load(modelPath)

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

yPred = model.predict(xTest)

accuracy = accuracy_score(yTest, yPred)
precision = precision_score(yTest, yPred, average="macro")
recall = recall_score(yTest, yPred, average="macro")
f1 = f1_score(yTest, yPred, average="macro")

dfMetrics = pd.DataFrame({
	"Metric": ["Accuracy", "Precision", "Recall", "F1 Score"],
	"Value": [accuracy, precision, recall, f1]
})

labels = yTest.unique().tolist()
cm = confusion_matrix(yTest, yPred, labels=labels)
dfCm = pd.DataFrame(cm, index=labels, columns=labels)

resultsDir = Path(currentDir)

dfMetrics.to_csv(resultsDir / "model_metrics.csv", index=False)
dfCm.to_csv(resultsDir / "confusion_matrix.csv", index=False)

print("\n=== Model Metrics ===")
print(dfMetrics.to_string(index=False))

print("\n=== Confusion matrix ===")
print(dfCm)
