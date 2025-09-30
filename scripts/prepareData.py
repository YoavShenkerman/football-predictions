import os
import glob
from datetime import date
import requests
import pandas as pd
from utils.teamNameMapping import nameMapping
from dotenv import load_dotenv
from pathlib import Path

#Delete old files so there's no duplicates
filesToRemove = ["laliga_all_seasons.csv", "laliga_all_seasons_plus_api.csv",
                 "matches.csv", "test.csv","completedMatches.csv", "futureMatches.csv"]
for file in filesToRemove:
	f = Path(file)
	if f.exists():
		f.unlink()

#Merge CSV files
csv_files = glob.glob("laliga*.csv")
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
merged_df.to_csv("laliga_all_seasons.csv", index=False)

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


#Keys for myself
#print(data.keys())
#print(data["matches"][0].keys())
#print(data['matches'][0]["homeTeam"].keys())
#print(data['matches'][0]["score"]["fullTime"].keys())

#Organaize the winners
matches = []
for match in data["matches"]:
	winner = match["score"]["winner"]

	if winner == "HOME_TEAM":
		result = "H"
	elif winner == "AWAY_TEAM":
		result = "A"
	elif winner == "DRAW":
		result = "D"
	else:
		result = None

	matches.append({
	    "date": match["utcDate"],
	    "homeTeam": match["homeTeam"]["shortName"],
	    "awayTeam": match["awayTeam"]["shortName"],
		"homeScore": match["score"]["fullTime"]["home"],
	    "awayScore": match["score"]["fullTime"]["away"],
	    "matchResult": result
    })


api_df = pd.DataFrame(matches)

#Edit names and dates
historical_df = pd.read_csv("../data/laliga_all_seasons.csv")
historical_df["homeTeam"] = historical_df["homeTeam"].replace(nameMapping)
historical_df["awayTeam"] = historical_df["awayTeam"].replace(nameMapping)
historical_df["date"] = pd.to_datetime(historical_df["date"], dayfirst=True, errors="coerce").dt.date

api_df["date"] = pd.to_datetime(api_df["date"], errors="coerce").dt.date
api_df["homeTeam"] = api_df["homeTeam"].replace(nameMapping)
api_df["awayTeam"] = api_df["awayTeam"].replace(nameMapping)

completedMatches = api_df[api_df["date"] < date.today()]
futureMatches = api_df[api_df["date"] >= date.today()]
api_df.to_csv("matches.csv", index=False)
completedMatches.to_csv("completedMatches.csv", index=False)
futureMatches.to_csv("futureMatches.csv", index=False)
print("Data saved to matches.csv, completedMatches.csv, futureMatches.csv")


#Merge the CVS from old seasons with the API data from current season
fullDf = pd.concat([historical_df, completedMatches], ignore_index=True)

fullDf["date"] = pd.to_datetime(fullDf["date"], dayfirst = True)

#Give all teams a number
teams = pd.concat([fullDf["homeTeam"], fullDf["awayTeam"]], ignore_index=True).unique()
team_mapping = {team: i for i, team in enumerate(teams)}
fullDf["homeCode"] = fullDf["homeTeam"].map(team_mapping)
fullDf["awayCode"] = fullDf["awayTeam"].map(team_mapping)

#Add dayCode column
fullDf["dayCode"] = fullDf["date"].dt.dayofweek

#Add result column
result_map = {
	"H" : 1,
	"A" : 2,
	"D" : 0
}
fullDf["target"] = fullDf["matchResult"].map(result_map)


#Season mapping
def get_season(date):
	"""
	Return the correct season in which the match was played based on the date
	:param date: Date of the match
	:return int: Correct season
	"""
	year = date.year
	if date.month <=7:
		return year-1
	else:
		return year
fullDf["season"] = fullDf["date"].apply(get_season)

#Goals for/against stats per season
fullDf["homeGoalsForSum"] = fullDf.groupby(["season", "homeTeam"])["homeScore"].apply(lambda x: x.cumsum().shift(fill_value=0)).reset_index(level=[0,1], drop=True)
fullDf["homeGoalsAgainstSum"] = fullDf.groupby(["season", "homeTeam"])["awayScore"].apply(lambda x: x.cumsum().shift(fill_value=0)).reset_index(level=[0,1], drop=True)
fullDf["awayGoalsForSum"] = fullDf.groupby(["season", "awayTeam"])["awayScore"].apply(lambda x: x.cumsum().shift(fill_value=0)).reset_index(level=[0,1], drop=True)
fullDf["awayGoalsAgainstSum"] = fullDf.groupby(["season", "awayTeam"])["homeScore"].apply(lambda x: x.cumsum().shift(fill_value=0)).reset_index(level=[0,1], drop=True)

#Rolling win rate of last 3/5/10 games
fullDf["homeWinRateRolling3"] = fullDf.groupby("homeTeam")["target"].apply(lambda x: (x==1).rolling(3,min_periods=1).mean().shift(fill_value=0)).reset_index(level=0, drop=True)
fullDf["awayWinRateRolling3"] = fullDf.groupby("awayTeam")["target"].apply(lambda x: (x==2).rolling(3,min_periods=1).mean().shift(fill_value=0)).reset_index(level=0, drop=True)
fullDf["homeWinRateRolling5"] = fullDf.groupby("homeTeam")["target"].apply(lambda x: (x==1).rolling(5,min_periods=1).mean().shift(fill_value=0)).reset_index(level=0, drop=True)
fullDf["awayWinRateRolling5"] = fullDf.groupby("awayTeam")["target"].apply(lambda x: (x==2).rolling(5,min_periods=1).mean().shift(fill_value=0)).reset_index(level=0, drop=True)
fullDf["homeWinRateRolling10"] = fullDf.groupby("homeTeam")["target"].apply(lambda x: (x==1).rolling(10,min_periods=1).mean().shift(fill_value=0)).reset_index(level=0, drop=True)
fullDf["awayWinRateRolling10"] = fullDf.groupby("awayTeam")["target"].apply(lambda x: (x==2).rolling(10,min_periods=1).mean().shift(fill_value=0)).reset_index(level=0, drop=True)

#Expanding win rate per season
fullDf["homeWinRateExpanding"] = fullDf.groupby(["season", "homeTeam"])["target"].apply(lambda x: (x==1).expanding().mean().shift(fill_value=0)).reset_index(level=[0,1], drop=True)
fullDf["awayWinRateExpanding"] = fullDf.groupby(["season", "awayTeam"])["target"].apply(lambda x: (x==2).expanding().mean().shift(fill_value=0)).reset_index(level=[0,1], drop=True)

#Adding points
fullDf["homePoints"] = fullDf["target"].map({0:1, 1:3, 2:0})
fullDf["awayPoints"] = fullDf["target"].map({0:1, 1:0, 2:3})
homeP = fullDf[["date","season", "homeTeam", "homePoints"]].rename(columns={"homeTeam":"team", "homePoints":"points"})
awayP = fullDf[["date","season", "awayTeam", "awayPoints"]].rename(columns={"awayTeam":"team", "awayPoints":"points"})
totalP = pd.concat([homeP, awayP], ignore_index=True)
totalP = totalP.sort_values("date").reset_index(drop=True)
totalP["totalPoints"] = totalP.groupby(["team","season"])["points"].apply(lambda x: x.cumsum().shift(fill_value=0)).reset_index(level=[0,1], drop=True)

fullDf = fullDf.merge(totalP[["date", "team","totalPoints"]].rename(columns={"team":"homeTeam", "totalPoints":"homeTotalPoints"}),
                      on=["date", "homeTeam"],
                      how = "left")
fullDf = fullDf.merge(totalP[["date", "team","totalPoints"]].rename(columns={"team":"awayTeam", "totalPoints":"awayTotalPoints"}),
                      on=["date", "awayTeam"],
                      how = "left")

#Goals for/against per game
homeGoals = fullDf[["date", "season", "homeTeam", "homeScore", "awayScore"]].rename(columns={"homeTeam":"team", "homeScore":"goalsFor", "awayScore":"goalsAgainst"})
awayGoals = fullDf[["date", "season", "awayTeam", "homeScore", "awayScore"]].rename(columns={"awayTeam":"team", "homeScore":"goalsAgainst", "awayScore":"goalsFor"})
totalGoals = pd.concat([homeGoals, awayGoals], ignore_index=True)
totalGoals = totalGoals.sort_values("date").reset_index(drop=True)
totalGoals["avgGoalsFor"] = totalGoals.groupby(["team", "season"])["goalsFor"].apply(lambda x: x.expanding().mean().shift(fill_value=0)).reset_index(level=[0,1], drop=True)
totalGoals["avgGoalsAgainst"] = totalGoals.groupby(["team", "season"])["goalsAgainst"].apply(lambda x: x.expanding().mean().shift(fill_value=0)).reset_index(level=[0,1], drop=True)

fullDf = fullDf.merge(totalGoals[["date", "team", "avgGoalsFor", "avgGoalsAgainst"]].rename(columns={"team":"homeTeam", "avgGoalsFor":"homeAvgGoalsFor", "avgGoalsAgainst":"homeAvgGoalsAgainst"}),
                      on=["date", "homeTeam"],
                      how = "left")
fullDf = fullDf.merge(totalGoals[["date", "team", "avgGoalsFor", "avgGoalsAgainst"]].rename(columns={"team":"awayTeam", "avgGoalsFor":"awayAvgGoalsFor", "avgGoalsAgainst":"awayAvgGoalsAgainst"}),
                      on=["date", "awayTeam"],
                      how = "left")

#Win/Loss/Draw count
homecount = fullDf[["date", "season", "homeTeam", "target"]].rename(columns={"homeTeam":"team"})
awaycount = fullDf[["date", "season", "awayTeam", "target"]].rename(columns={"awayTeam":"team"})
awaycount["target"] = awaycount["target"].map({0:0, 1:2, 2:1})
totalWLD = pd.concat([homecount, awaycount], ignore_index=True)
totalWLD = totalWLD.sort_values("date").reset_index(drop=True)
totalWLD["totalWins"] = totalWLD.groupby(["team","season"])["target"].apply(lambda x: (x==1).cumsum().shift(fill_value=0)).reset_index(level=[0,1], drop=True)
totalWLD["totalLosses"] = totalWLD.groupby(["team","season"])["target"].apply(lambda x: (x==2).cumsum().shift(fill_value=0)).reset_index(level=[0,1], drop=True)
totalWLD["totalDraws"] = totalWLD.groupby(["team","season"])["target"].apply(lambda x: (x==0).cumsum().shift(fill_value=0)).reset_index(level=[0,1], drop=True)

fullDf = fullDf.merge(totalWLD[["date", "team", "totalWins", "totalLosses", "totalDraws"]].rename(columns={"team":"homeTeam", "totalWins":"homeTotalWins", "totalLosses":"homeTotalLosses", "totalDraws":"homeTotalDraws"}),
                      on=["date", "homeTeam"],
                      how = "left")
fullDf = fullDf.merge(totalWLD[["date", "team", "totalWins", "totalLosses", "totalDraws"]].rename(columns={"team":"awayTeam", "totalWins":"awayTotalWins", "totalLosses":"awayTotalLosses", "totalDraws":"awayTotalDraws"}),
                      on=["date", "awayTeam"],
                      how = "left")

fullDf.to_csv("laliga_all_seasons_plus_api.csv", index=False)
print("All seasons + API data saved to laliga_all_seasons_plus_api.csv")