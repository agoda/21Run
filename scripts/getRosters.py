import sys
sys.path.append('./')
import json
from LeagueAPI import League
from TeamAPI import Team
from PlayerAPI import Player
from pymongo import MongoClient


def getMongoLeagueTeamNames(db):
	result = db['Soccer-Leagues'].aggregate([
					{"$group":{"_id":{"league":"$metadata.Name"}, "teams":{"$push":"$team.ID"}}},
					{"$project":{"league":"$_id.league","teams" : 1, "_id":0}}])
	return result
def getPlayers(roster,allPlayers,bulkP):
	#take a roster as input, iterate through and create a new player object
	for player in roster:
		#print player
		bulkP.find({'ID': player["ID"]}).upsert().update({"$set":{'ID': player['ID'], "metadata": player}})
		#allPlayers.extend([player])

def start():
	client = MongoClient('localhost', 27017)
	db = client['21Run']
	collectionLeagues = db['Soccer-Leagues']
	collectionPlayers = db['Players']
	bulkLeagues = collectionLeagues.initialize_unordered_bulk_op()
	bulkPlayers = collectionPlayers.initialize_unordered_bulk_op()


	response = getMongoLeagueTeamNames(db)
	results = response['result']
	for result in results:
		league = result['league']
		teams = result['teams']
		rosters = {} # dictionary that will contain all the teams and associated rosters, will bulk upsert these objects to mongo
		P = Player()
		allPlayers = [] #will contain all the players for this league(in other words, all the plyaers for all teams in this league)
		for team in teams:
			#need to set roster for league
			roster = P.setRosterInTeam(str(team))
			#roster will be a object of format:  {'roster': [{player}]}
			rosters[team] = roster 
			bulkLeagues.find({'metadata.Name':league, 'team.ID':str(team)}).update({"$set": {'team.Roster':roster['roster']}})
			#rosters  --->  {'451': {'roster':[{player1},{player2}]}}
			getPlayers(roster['roster'],allPlayers, bulkPlayers)

	bulkLeagues.execute()
	bulkPlayers.execute()




start()