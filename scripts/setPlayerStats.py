import sys
sys.path.append('./')
import json
from pymongo import MongoClient
from collections import Counter



def getMongoScorers(db):
	result = db['Matches'].aggregate([
					{"$group":{"_id":"null", "homeScorers":{"$push":"$home.goalDetails"},"awayScorers":{"$push":"$away.goalDetails"}}},
					])
	return result


def goalSpreadCalculation( homeRes, awayRes, collectionPlayers):

	bulkP = collectionPlayers.initialize_unordered_bulk_op()

	#calculate goals scored at home
	home = []
	away = []
	combined = []

	for player in awayRes:
		away.append(player['name'])
		#combined.append(player['name'])

	for player in homeRes:
		home.append(player['name'])
		#combined.append(player['name'])

	homeCounts = Counter(home)
	awayCounts = Counter(away)
	combinedCounts = homeCounts + awayCounts#Counter(combined)
	
	#for each player, update appropriate fields in Player collection
	for player in homeCounts:
		bulkP.find({'metadata.Name': player}).upsert().update({"$set":{'stats.historical.goalsAtHome': homeCounts[player], 'stats.historical.goalsAtOpponent': 0, 'stats.historical.totalGoals':0}})
	for player in awayCounts:
		bulkP.find({'metadata.Name': player}).upsert().update({"$set":{'stats.historical.goalsAtOpponent': awayCounts[player], 'stats.historical.totalGoals':0}})
	for player in combinedCounts:
		bulkP.find({'metadata.Name': player}).upsert().update({"$set":{'stats.historical.totalGoals': combinedCounts[player]}})


	bulkP.execute()
def unwind(result):
	#decompose an array of arrays into a single array of elements: [[{}],[{},{}]] ---> [{},{},{}]
	unwound = []
	for elem in result:
		for obj in elem:
			unwound.append(obj)
	return unwound

def start():
	client = MongoClient('localhost', 27017)
	db = client['21Run']
	collectionLeagues = db['Matches']
	collectionPlayers = db['Players']
	bulkMatches = collectionLeagues.initialize_unordered_bulk_op()
	

	response = getMongoScorers(db)
	result = response['result'][0]
	homeResult = unwind(result['homeScorers'])
	awayResult = unwind(result['awayScorers'])
	goalSpreadCalculation(homeResult, awayResult, collectionPlayers)
	
	
start()