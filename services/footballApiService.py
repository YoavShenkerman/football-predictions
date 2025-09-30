import pandas as pd
from datetime import date
from utils.teamNameMapping import nameMapping

def organizeWinners(data):
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
	return pd.DataFrame(matches)

def processApiDf(api_df):
	api_df["date"] = pd.to_datetime(api_df["date"], errors="coerce").dt.date
	api_df["homeTeam"] = api_df["homeTeam"].replace(nameMapping)
	api_df["awayTeam"] = api_df["awayTeam"].replace(nameMapping)

	completedMatches = api_df[api_df["date"] < date.today()]
	futureMatches = api_df[api_df["date"] >= date.today()]

	return completedMatches, futureMatches

def addTeamCodes(df):
	df = df.copy()  # עותק של DataFrame כדי לשנות בבטחה
	teams = pd.concat([df["homeTeam"], df["awayTeam"]], ignore_index=True).unique()
	team_mapping = {team: i for i, team in enumerate(teams)}
	df["homeCode"] = df["homeTeam"].map(team_mapping)
	df["awayCode"] = df["awayTeam"].map(team_mapping)
	return df

def addDayCode(df):
	df = df.copy()
	df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)
	df["dayCode"] = df["date"].dt.dayofweek
	return df

def addTargetCode(df):
	result_map = {
		"H" : 1,
		"A" : 2,
		"D" : 0
	}
	df["target"] = df["matchResult"].map(result_map)
	return df

def addSeason(df):
	def getSeason(date):
		"""
		Return the correct season in which the match was played based on the date
		:param date: Date of the match
		:return int: Correct season
		"""
		year = date.year
		if date.month <= 7:
			return year - 1
		else:
			return year

	df["season"] = df["date"].apply(getSeason)
	return df

def addStats(df):
	df["homeGoalsForSum"] = df.groupby(["season", "homeTeam"])["homeScore"].apply(
		lambda x: x.cumsum().shift(fill_value=0)).reset_index(level=[0, 1], drop=True)
	df["homeGoalsAgainstSum"] = df.groupby(["season", "homeTeam"])["awayScore"].apply(
		lambda x: x.cumsum().shift(fill_value=0)).reset_index(level=[0, 1], drop=True)
	df["awayGoalsForSum"] = df.groupby(["season", "awayTeam"])["awayScore"].apply(
		lambda x: x.cumsum().shift(fill_value=0)).reset_index(level=[0, 1], drop=True)
	df["awayGoalsAgainstSum"] = df.groupby(["season", "awayTeam"])["homeScore"].apply(
		lambda x: x.cumsum().shift(fill_value=0)).reset_index(level=[0, 1], drop=True)

	# Rolling win rate of last 3/5/10 games
	df["homeWinRateRolling3"] = df.groupby("homeTeam")["target"].apply(
		lambda x: (x == 1).rolling(3, min_periods=1).mean().shift(fill_value=0)).reset_index(level=0, drop=True)
	df["awayWinRateRolling3"] = df.groupby("awayTeam")["target"].apply(
		lambda x: (x == 2).rolling(3, min_periods=1).mean().shift(fill_value=0)).reset_index(level=0, drop=True)
	df["homeWinRateRolling5"] = df.groupby("homeTeam")["target"].apply(
		lambda x: (x == 1).rolling(5, min_periods=1).mean().shift(fill_value=0)).reset_index(level=0, drop=True)
	df["awayWinRateRolling5"] = df.groupby("awayTeam")["target"].apply(
		lambda x: (x == 2).rolling(5, min_periods=1).mean().shift(fill_value=0)).reset_index(level=0, drop=True)
	df["homeWinRateRolling10"] = df.groupby("homeTeam")["target"].apply(
		lambda x: (x == 1).rolling(10, min_periods=1).mean().shift(fill_value=0)).reset_index(level=0, drop=True)
	df["awayWinRateRolling10"] = df.groupby("awayTeam")["target"].apply(
		lambda x: (x == 2).rolling(10, min_periods=1).mean().shift(fill_value=0)).reset_index(level=0, drop=True)

	# Expanding win rate per season
	df["homeWinRateExpanding"] = df.groupby(["season", "homeTeam"])["target"].apply(
		lambda x: (x == 1).expanding().mean().shift(fill_value=0)).reset_index(level=[0, 1], drop=True)
	df["awayWinRateExpanding"] = df.groupby(["season", "awayTeam"])["target"].apply(
		lambda x: (x == 2).expanding().mean().shift(fill_value=0)).reset_index(level=[0, 1], drop=True)

	# Adding points
	df["homePoints"] = df["target"].map({0: 1, 1: 3, 2: 0})
	df["awayPoints"] = df["target"].map({0: 1, 1: 0, 2: 3})
	homeP = df[["date", "season", "homeTeam", "homePoints"]].rename(
		columns={"homeTeam": "team", "homePoints": "points"})
	awayP = df[["date", "season", "awayTeam", "awayPoints"]].rename(
		columns={"awayTeam": "team", "awayPoints": "points"})
	totalP = pd.concat([homeP, awayP], ignore_index=True)
	totalP = totalP.sort_values("date").reset_index(drop=True)
	totalP["totalPoints"] = totalP.groupby(["team", "season"])["points"].apply(
		lambda x: x.cumsum().shift(fill_value=0)).reset_index(level=[0, 1], drop=True)

	df = df.merge(
		totalP[["date", "team", "totalPoints"]].rename(columns={"team": "homeTeam", "totalPoints": "homeTotalPoints"}),
		on=["date", "homeTeam"],
		how="left")
	df = df.merge(
		totalP[["date", "team", "totalPoints"]].rename(columns={"team": "awayTeam", "totalPoints": "awayTotalPoints"}),
		on=["date", "awayTeam"],
		how="left")

	# Goals for/against per game
	homeGoals = df[["date", "season", "homeTeam", "homeScore", "awayScore"]].rename(
		columns={"homeTeam": "team", "homeScore": "goalsFor", "awayScore": "goalsAgainst"})
	awayGoals = df[["date", "season", "awayTeam", "homeScore", "awayScore"]].rename(
		columns={"awayTeam": "team", "homeScore": "goalsAgainst", "awayScore": "goalsFor"})
	totalGoals = pd.concat([homeGoals, awayGoals], ignore_index=True)
	totalGoals = totalGoals.sort_values("date").reset_index(drop=True)
	totalGoals["avgGoalsFor"] = totalGoals.groupby(["team", "season"])["goalsFor"].apply(
		lambda x: x.expanding().mean().shift(fill_value=0)).reset_index(level=[0, 1], drop=True)
	totalGoals["avgGoalsAgainst"] = totalGoals.groupby(["team", "season"])["goalsAgainst"].apply(
		lambda x: x.expanding().mean().shift(fill_value=0)).reset_index(level=[0, 1], drop=True)

	df = df.merge(totalGoals[["date", "team", "avgGoalsFor", "avgGoalsAgainst"]].rename(
		columns={"team": "homeTeam", "avgGoalsFor": "homeAvgGoalsFor", "avgGoalsAgainst": "homeAvgGoalsAgainst"}),
	                      on=["date", "homeTeam"],
	                      how="left")
	df = df.merge(totalGoals[["date", "team", "avgGoalsFor", "avgGoalsAgainst"]].rename(
		columns={"team": "awayTeam", "avgGoalsFor": "awayAvgGoalsFor", "avgGoalsAgainst": "awayAvgGoalsAgainst"}),
	                      on=["date", "awayTeam"],
	                      how="left")

	# Win/Loss/Draw count
	homecount = df[["date", "season", "homeTeam", "target"]].rename(columns={"homeTeam": "team"})
	awaycount = df[["date", "season", "awayTeam", "target"]].rename(columns={"awayTeam": "team"})
	awaycount["target"] = awaycount["target"].map({0: 0, 1: 2, 2: 1})
	totalWLD = pd.concat([homecount, awaycount], ignore_index=True)
	totalWLD = totalWLD.sort_values("date").reset_index(drop=True)
	totalWLD["totalWins"] = totalWLD.groupby(["team", "season"])["target"].apply(
		lambda x: (x == 1).cumsum().shift(fill_value=0)).reset_index(level=[0, 1], drop=True)
	totalWLD["totalLosses"] = totalWLD.groupby(["team", "season"])["target"].apply(
		lambda x: (x == 2).cumsum().shift(fill_value=0)).reset_index(level=[0, 1], drop=True)
	totalWLD["totalDraws"] = totalWLD.groupby(["team", "season"])["target"].apply(
		lambda x: (x == 0).cumsum().shift(fill_value=0)).reset_index(level=[0, 1], drop=True)

	df = df.merge(totalWLD[["date", "team", "totalWins", "totalLosses", "totalDraws"]].rename(
		columns={"team": "homeTeam", "totalWins": "homeTotalWins", "totalLosses": "homeTotalLosses",
		         "totalDraws": "homeTotalDraws"}),
	                      on=["date", "homeTeam"],
	                      how="left")
	df = df.merge(totalWLD[["date", "team", "totalWins", "totalLosses", "totalDraws"]].rename(
		columns={"team": "awayTeam", "totalWins": "awayTotalWins", "totalLosses": "awayTotalLosses",
		         "totalDraws": "awayTotalDraws"}),
	                      on=["date", "awayTeam"],
	                      how="left")
	return df
