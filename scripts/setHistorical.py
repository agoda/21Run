import sys
sys.path.append('./')
import json
from FixtureAPI import Fixture
from pymongo import MongoClient

#TODO: pull from central configuration file
#include 0405, 0506 0607 0708 0809 0910 1011
seasons = ["1213","1314"]
leagues = ["Scottish Premier League"]

def start():
	client = MongoClient('localhost', 27017)
	db = client['21Run']
	collection = db['Matches']
	bulk = collection.initialize_unordered_bulk_op()
	F = Fixture()
	for season in seasons:
		for league in leagues:
			allMatches = F.getHistoricalMatchesByLeagueAndSeason(league, season, "-o")
			for match in allMatches:
				match['league'] = league
				bulk.insert(match)
				print match
	bulk.execute()
start()