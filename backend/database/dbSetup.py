import os
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

class Team(Base):
	__tablename__ = "teams"
	id = Column(Integer, primary_key=True)
	name = Column(String, unique=True)
	code = Column(String, unique=True)

class Match(Base):
	__tablename__ = "matches"
	id = Column(Integer, primary_key=True)
	homeTeamId = Column(Integer, ForeignKey("teams.id"))
	awayTeamId = Column(Integer, ForeignKey("teams.id"))
	homeScore = Column(Integer, nullable=True)
	awayScore = Column(Integer, nullable=True)
	season = Column(Integer)
	date = Column(Date)

	homeGoalsForSum = Column(Integer)
	homeGoalsAgainstSum = Column(Integer)
	awayGoalsForSum = Column(Integer)
	awayGoalsAgainstSum = Column(Integer)

	homeWinRateRolling3 = Column(Float)
	awayWinRateRolling3 = Column(Float)
	homeWinRateRolling5 = Column(Float)
	awayWinRateRolling5 = Column(Float)
	homeWinRateRolling10 = Column(Float)
	awayWinRateRolling10 = Column(Float)

	homeWinRateExpanding = Column(Float)
	awayWinRateExpanding = Column(Float)

	homeTotalPoints = Column(Integer)
	awayTotalPoints = Column(Integer)

	homeAvgGoalsFor = Column(Float)
	homeAvgGoalsAgainst = Column(Float)
	awayAvgGoalsFor = Column(Float)
	awayAvgGoalsAgainst = Column(Float)

	homeTotalWins = Column(Integer)
	homeTotalLosses = Column(Integer)
	homeTotalDraws = Column(Integer)
	awayTotalWins = Column(Integer)
	awayTotalLosses = Column(Integer)
	awayTotalDraws = Column(Integer)

	target = Column(Integer)  # 0=Draw, 1=Home, 2=Away
	dayCode = Column(Integer)
	homeCode = Column(Integer)
	awayCode = Column(Integer)

	homeTeam = relationship("Team", foreign_keys=[homeTeamId])
	awayTeam = relationship("Team", foreign_keys=[awayTeamId])

currentDir = os.path.dirname(__file__)
dbDir = os.path.join(currentDir)
if not os.path.exists(dbDir):
	os.makedirs(dbDir)

dbPath = os.path.join(dbDir, "football.db")
engine = create_engine(f"sqlite:///{dbPath}")

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

print(f"Database created at: {dbPath}")

