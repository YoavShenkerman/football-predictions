import os
import pandas as pd
from dbSetup import session, Team, Match

currentDir = os.path.dirname(__file__)
csvPath = os.path.join(currentDir, "..", "data", "laliga_all_seasons_plus_api.csv")
csvPath = os.path.abspath(csvPath)

df = pd.read_csv(csvPath, parse_dates=["date"])

teams = df[["homeTeam", "homeCode"]].drop_duplicates()

for _, row in teams.iterrows():
	team = Team(name=row["homeTeam"], code=row["homeCode"])
	session.merge(team)
session.commit()
print(f"{len(teams)} teams inserted/updated.")

for _, row in df.iterrows():
	homeTeam = session.query(Team).filter_by(name=row["homeTeam"]).first()
	awayTeam = session.query(Team).filter_by(name=row["awayTeam"]).first()

	match = Match(
		date=row["date"],
		homeTeamId=homeTeam.id,
		awayTeamId=awayTeam.id,
		homeScore=row.get("homeScore"),
		awayScore=row.get("awayScore"),
		season=row.get("season"),

		homeGoalsForSum=row.get("homeGoalsForSum"),
		homeGoalsAgainstSum=row.get("homeGoalsAgainstSum"),
		awayGoalsForSum=row.get("awayGoalsForSum"),
		awayGoalsAgainstSum=row.get("awayGoalsAgainstSum"),

		homeWinRateRolling3=row.get("homeWinRateRolling3"),
		awayWinRateRolling3=row.get("awayWinRateRolling3"),
		homeWinRateRolling5=row.get("homeWinRateRolling5"),
		awayWinRateRolling5=row.get("awayWinRateRolling5"),
		homeWinRateRolling10=row.get("homeWinRateRolling10"),
		awayWinRateRolling10=row.get("awayWinRateRolling10"),

		homeWinRateExpanding=row.get("homeWinRateExpanding"),
		awayWinRateExpanding=row.get("awayWinRateExpanding"),

		homeTotalPoints=row.get("homeTotalPoints"),
		awayTotalPoints=row.get("awayTotalPoints"),

		homeAvgGoalsFor=row.get("homeAvgGoalsFor"),
		homeAvgGoalsAgainst=row.get("homeAvgGoalsAgainst"),
		awayAvgGoalsFor=row.get("awayAvgGoalsFor"),
		awayAvgGoalsAgainst=row.get("awayAvgGoalsAgainst"),

		homeTotalWins=row.get("homeTotalWins"),
		homeTotalLosses=row.get("homeTotalLosses"),
		homeTotalDraws=row.get("homeTotalDraws"),
		awayTotalWins=row.get("awayTotalWins"),
		awayTotalLosses=row.get("awayTotalLosses"),
		awayTotalDraws=row.get("awayTotalDraws"),

		target=row.get("target"),
		dayCode=row.get("dayCode"),
		homeCode=row.get("homeCode"),
		awayCode=row.get("awayCode")
	)
	session.add(match)

session.commit()
print(f"{len(df)} matches inserted.")
