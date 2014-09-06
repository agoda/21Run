#run once a season
import sys
sys.path.append('./')
import json
from FixtureAPI import Fixture
from pymongo import MongoClient

upcomingSeason = "1415"
leagues = ["Scottish Premier League"]

def start():
	client = MongoClient('localhost', 27017)
	db = client['21Run']
	collection = db['UpcomingSchedules']
	bulk = collection.initialize_unordered_bulk_op()
	F = Fixture()
	for league in leagues:
		allMatches = F.getUpcomingMatchesByLeagueAndSeason(league, upcomingSeason)
		for match in allMatches:
			bulk.insert(match)
			print match
	bulk.execute()
start()
