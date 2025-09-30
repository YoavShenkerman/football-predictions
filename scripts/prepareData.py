import os
import glob
import requests
import pandas as pd
from utils.teamNameMapping import nameMapping
from dotenv import load_dotenv
from pathlib import Path
from services.footballApiService import organizeWinners,processApiDf,addStats,addSeason,addDayCode,addTargetCode,addTeamCodes

dataPath = Path(r"C:\Users\yoavs\Desktop\אוניברסיטת תל אביב\פרוייקטים\פרוייקטים אישיים\football-predictions\data")

#Delete old files so there's no duplicates
filesToRemove = ["laliga_all_seasons.csv", "laliga_all_seasons_plus_api.csv",
                 "matches.csv", "test.csv","completedMatches.csv", "futureMatches.csv"]
for file in filesToRemove:
	f = dataPath / file
	if f.exists():
		f.unlink()

#Merge CSV files
csv_files = glob.glob(str(dataPath / "laliga*.csv"))
all_seasons = []

for file in csv_files:
	df = pd.read_csv(file)
	df = df.rename(columns={
		"Date": "date",
		"HomeTeam": "homeTeam",
		"AwayTeam": "awayTeam",
		"FTHG": "homeScore",
		"FTAG": "awayScore",
		"FTR": "matchResult"
	})

	df = df[["date", "homeTeam", "awayTeam", "homeScore", "awayScore", "matchResult"]]
	all_seasons.append(df)

merged_df = pd.concat(all_seasons, ignore_index=True)


merged_df.to_csv(dataPath / "laliga_all_seasons.csv", index=False)
print("All season merged and saved to laliga_all_seasons.csv")

#Load APIToken.env
load_dotenv("../config/APIToken.env")
APIToken = os.getenv("API_TOKEN")

#Get updated data from API
url = "https://api.football-data.org/v4/competitions/PD/matches"
headers = {"X-Auth-Token" : APIToken}

try:
	response = requests.get(url, headers=headers, timeout=10)
	response.raise_for_status()
	data = response.json()
except Exception as e:
	print(f"API request failed: {e}")
	raise RuntimeError("Failed to fetch data from API")

api_df = organizeWinners(data)

#Edit names and dates
historical_df = pd.read_csv("../data/laliga_all_seasons.csv")
historical_df["homeTeam"] = historical_df["homeTeam"].replace(nameMapping)
historical_df["awayTeam"] = historical_df["awayTeam"].replace(nameMapping)
historical_df["date"] = pd.to_datetime(historical_df["date"], dayfirst=True, errors="coerce").dt.date

completedMatches, futureMatches = processApiDf(api_df)

#Merge the CVS from old seasons with the API data from current season
fullDf = pd.concat([historical_df, completedMatches], ignore_index=True)

fullDf["date"] = pd.to_datetime(fullDf["date"], dayfirst = True)

fullDf = addTeamCodes(fullDf)
fullDf = addDayCode(fullDf)
fullDf = addTargetCode(fullDf)
fullDf = addSeason(fullDf)
fullDf = addStats(fullDf)

fullDf.to_csv(dataPath / "laliga_all_seasons_plus_api.csv", index=False)
print("All seasons + API data saved to laliga_all_seasons_plus_api.csv")
