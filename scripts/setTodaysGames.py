#This script will run at EOD, every day, timestamps will be this days timestamp
import sys
sys.path.append('./')
import json
from FixtureAPI import Fixture
from pymongo import MongoClient
import datetime
import calendar
import time

#TODO: pull from central configuration file
leagues = ["Scottish Premier League"]

def getTime():
	timeNow = datetime.datetime.fromtimestamp(int(str(calendar.timegm(time.gmtime())))).strftime('%Y-%m-%d %H:%M:%S')
	return timeNow.split(' ')[0]

def start():
	client = MongoClient('localhost', 27017)
	db = client['21Run']
	collection = db['Matches']
	bulk = collection.initialize_unordered_bulk_op()

	interval = getTime()

	F = Fixture()
	for season in seasons:
		for league in leagues:
			allMatches = F.getHistoricalMatchesByLeagueAndDateInterval(league, interval, interval)
			for match in allMatches:
				match['league'] = league
				bulk.insert(match)
				print match
	bulk.execute()
start()

#F = Fixture()
#leagueName = "Scottish Premier League"
#startDate = "2005-05-21"
#allMatchesToday = F.getHistoricalMatchesByLeagueAndDateInterval(leagueName, startDate, startDate)
#print allMatchesToday