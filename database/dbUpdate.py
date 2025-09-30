import os
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.dbSetup import Team, Match
import pandas as pd
import schedule
import time
from services.footballApiService import addStats, organizeWinners, addSeason, addDayCode, addTeamCodes, addTargetCode, \
	processApiDf

currentDir = os.path.dirname(__file__)
dbPath = os.path.join(currentDir, "football.db")
dbPath = os.path.abspath(dbPath)

engine = create_engine(f"sqlite:///{dbPath}")
Session = sessionmaker(bind=engine)
session = Session()

def updateDbFromApi(session, apiUrl, apiToken):
	cnt = 0
	headers = {"X-Auth-Token" : apiToken}
	try:
		response = requests.get(apiUrl, headers=headers, timeout=10)
		response.raise_for_status()
		data = response.json()
	except Exception as e:
		print(f"API request failed: {e}")
		raise RuntimeError("Failed to fetch data from API")

	apiDf = organizeWinners(data)
	competedMatchesDF,_ = processApiDf(apiDf)
	competedMatchesDF = addTeamCodes(competedMatchesDF)
	competedMatchesDF = addDayCode(competedMatchesDF)
	competedMatchesDF = addTargetCode(competedMatchesDF)
	competedMatchesDF = addSeason(competedMatchesDF)
	competedMatchesDF = addStats(competedMatchesDF)

	for _, row in competedMatchesDF.iterrows():
		for teamName, teamCode in [(row["homeTeam"], row["homeCode"]),
		                           (row["awayTeam"], row["awayCode"])]:
			team = session.query(Team).filter_by(name=teamName).first()
			if not team:
				team = Team(name=teamName, code=teamCode)
				session.add(team)
	session.commit()

	for _, row in competedMatchesDF.iterrows():
		homeTeam = session.query(Team).filter_by(name=row["homeTeam"]).first()
		awayTeam = session.query(Team).filter_by(name=row["awayTeam"]).first()

		existingMatch = session.query(Match).filter_by(
			date=pd.to_datetime(row["date"]).date(),
			homeTeamId=homeTeam.id,
			awayTeamId=awayTeam.id
		).first()

		if not existingMatch:
			cnt += 1
			match = Match(
				date=pd.to_datetime(row["date"]).date(),
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
	print(f"Database updated from API! | Added {cnt} matches")

load_dotenv("../config/APIToken.env")
APIToken = os.getenv("API_TOKEN")

url = "https://api.football-data.org/v4/competitions/PD/matches"
headers = {"X-Auth-Token": APIToken}

"""
def job():
	updateDbFromApi(session, url, APIToken)

job()

schedule.every().day.at("03:00").do(job)
while True:
	schedule.run_pending()
	time.sleep(60)
"""





