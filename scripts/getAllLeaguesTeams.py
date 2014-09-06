import json
import sys
from pymongo import MongoClient
sys.path.append('./')
from LeagueAPI import League
from TeamAPI import Team
from PlayerAPI import Player


def start():
	client = MongoClient('localhost', 27017)
	db = client['21Run']
	collection = db['Soccer-Leagues']
	bulk = collection.initialize_unordered_bulk_op()

	season = "1314"
	l = League()
	t=  Team()
	P = Player()
	allRetObjs = []
	allLeagues = l.getAllLeagues()

	for league in allLeagues:
		teams = []
		teams = list(t.getTeamsByLeague(league['Name'], season))
		teamStandings = list(t.getTeamStandings(league['Name'], season))
		teamObjs = []
		for team in teams:
			teamObj = {}
			teamObj['ID'] = league['ID']
			teamObj['metadata'] = league
			teamObj['team'] = team
			teamObjs.append(teamObj)
		#print teamObjs
		for teamStanding in teamStandings:
			for tmpObj in teamObjs:
				if tmpObj['team']['ID'] == teamStanding['ID']:
					tmpObj['team']['stats'] = {}
					tmpObj['team']['stats'] = teamStanding
					bulk.insert(tmpObj)
					break
		allRetObjs.append(teamObjs)
	bulk.execute()
	#collection.insert(allRetObjs)


print start()