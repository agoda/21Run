import redis
import json
import pycurl
import cStringIO
from xml.dom import minidom
#https://docs.python.org/2/library/xml.dom.minidom.html

class Fixture:
	def __init__(self):
		self.API_KEY = 'QUKJIFDZQOXAVSJLMIGQNDQHAVBWBQNBEJYNSFGAKBAHWBBXZU'
		self.url = ''
		self.properties = []
	
	def getText(self,nodelist):
		rc = []
		for node in nodelist:
			if node.nodeType == node.TEXT_NODE:
				rc.append(node.data)
		return ''.join(rc)

	def setAPIKey(self,key):
		self.API_KEY = key

	def getAPIKey(self):
		return self.API_KEY

	#abstracted function to make an API call - takes as input the URL
	def makeAPICall(self):
		buf = cStringIO.StringIO()
		c = pycurl.Curl()
		c.setopt(c.URL, self.url)
		c.setopt(c.WRITEFUNCTION, buf.write)
		c.perform()
		self.xmldoc = minidom.parseString(buf.getvalue())
		#print buf.getvalue()
		buf.close()

	#TODO: need to abstract out this ability of parsing for properties -- pass in a dictionary of key - value where key = nodeName expected, and value = expected returned format.  ex: {'Id'=> 'ID', 'Name'=>'Name'}
	def parseProperties(self, children, valDict):
		tmpProperties ={}
		for node in children:
			if node.nodeType == node.ELEMENT_NODE:
				desiredPrprty = node.nodeName
				if desiredPrprty in valDict.keys():
					expectedForm = valDict[desiredPrprty]
					if '.' in expectedForm:
						objProperty = expectedForm.split('.')
						if objProperty[0] in tmpProperties:
							tmpProperties[objProperty[0]][objProperty[1]] = self.getText(node.childNodes)
						else:
							tmpProperties[objProperty[0]] = {}
							tmpProperties[objProperty[0]][objProperty[1]] = self.getText(node.childNodes)
					else:
						tmpProperties[valDict[desiredPrprty]] = self.getText(node.childNodes)
					#print properties
		return tmpProperties

	def clearProperties(self):
		del self.properties[:]
		self.properties = []


	def getUpcomingGames(self, startDate, endDate):
		self.url=""
	def getUpcomingGamesByTeam(self, startDate, endDate, teamName):
		self.url=""
	def getUpcomingMatchesByLeagueAndSeason(self,leagueName, seasonDateString):
		htmlLeague = str(leagueName).replace(" ", "%20")
		self.url = 'http://www.xmlsoccer.com/FootballDataDemo.asmx/GetFixturesByLeagueAndSeason?ApiKey='+self.API_KEY+'&league='+htmlLeague+'&seasonDateString='+str(seasonDateString)
		self.makeAPICall()
		xmlMatches = self.xmldoc.getElementsByTagName('XMLSOCCER.COM')[0].getElementsByTagName('Match')
		self.clearProperties()

		valsDict = {
		'Id':'matchID', 'Date':'date', 'League':'league', 'Round':'round', 'HomeTeam':'home.Name','HomeTeam_Id':'home.ID',
		'AwayTeam':'away.Name', 'AwayTeam_Id':'away.ID', 'Location':'location'
		}

		for xmlMatch in xmlMatches:
			obj = self.parseProperties(xmlMatch.childNodes, valsDict)
			self.properties.extend([obj])

		return self.properties

	def parseGoalDetails(self, _set):
		allScorers = []
		if _set != None and _set != "":
			scorers = _set.split(";")[:-1] #get rid of the last element since it will always be empty -- _set:  "time:player1;time:player2;" since we split on ';'
			for scorer in scorers:
				player = scorer.split(':')#we will have the following possibilities:  ":Own dfdf", ": penalty dfdf", ": playerName"
				nameString = player[1].lstrip().split(' ') #remove leading whitespace -- so we now have options: "Own playerName", "penalty Playername", "PlayerName"
				obj = {}
				if nameString[0] == "Own": #then this was an own goal
					obj['type'] = "Own"
					obj['time'] = player[0].split("'")[0]
					if "" in nameString:
						nameString.remove("")
					name = ' '.join(nameString[1:])
					obj['name'] = name.rstrip().lstrip()
				elif nameString[0] == "penalty":
					obj['type'] = "Penalty"
					obj['time'] = player[0].split("'")[0]
					if "" in nameString:
						nameString.remove("")
					name = ' '.join(nameString[1:])
					obj['name'] = name.rstrip().lstrip()
				else:	
					obj['name'] = player[1].lstrip().rstrip()
					obj['time'] = player[0].split("'")[0]
					obj['type'] = "Normal"
				allScorers.append(obj)
		return allScorers

	def getHistoricalMatchesByLeagueAndDateInterval(self, leagueName, startDate, endDate):
		htmlLeague = str(leagueName).replace(" ", "%20")
		self.url = 'http://www.xmlsoccer.com/FootballDataDemo.asmx/GetHistoricMatchesByLeagueAndDateInterval?ApiKey='+self.API_KEY+'&league='+htmlLeague+'&startDateString='+str(startDate) +'&endDateString='+str(endDate)
		self.makeAPICall()
		xmlMatches = self.xmldoc.getElementsByTagName('XMLSOCCER.COM')[0].getElementsByTagName('Match')
		self.clearProperties()

		valsDict = {
		'Id':'matchID', 'FixtureMatch_Id':'fixtureID', 'Date':'date', 'Round':'round', 'Spectators':'spectators', 'League:':'league', 'HomeTeam':'home.name', 'HomeTeam_Id':'home.teamID',
		'HomeCorners':'home.cornerKicks', 'HomeGoals':'home.goals', 'HalfTimeHomeGoals':'home.halfTimeGoals', 'HomeShots':'home.shots', 'HomeShotsOnTarget':'home.shotsOnTarget', 'HomeFouls':'home.fouls',
		'HomeGoalDetails':'home.goalDetails', 'HomeLineupGoalkeeper':'home.lineupGoalkeeper', 'HomeLineupDefense':'home.lineupDefense', 'HomeLineupMidfield':'home.lineupMidfield', 'HomeLineupForward':'home.lineupForward',
		'HomeLineupSubstitutes':'home.lineupSubstitutes', 'HomeYellowCards':'home.yellowCards', 'HomeRedCards':'home.redCards', 'HomeSubDetails':'home.subDetails', 'AwaySubDetails':'away.subDetails', 'HomeTeamFormation':'home.teamFormation',
		'AwayTeam':'away.name', 'AwayCorners':'away.corners', 'AwayGoals':'away.goals', 'HalfTimeAwayGoals':'away.haltTimeGoals', 'AwayShots':'away.shots', 'AwayShotsOnTarget':'away.shotsOnTarget', 'AwayFouls':'away.fouls', 'AwayGoalDetails':'away.goalDetails',
		'AwayLineupGoalkeeper':'away.lineupGoalkeeper', 'AwayLineupDefense':'away.lineupDefense', 'AwayLineupMidfield':'away.lineupMidfield', 'AwayLineupForward':'away.lineupForward', 'AwayLineupSubstitutes':'away.lineupSubstitutes', 'AwayYellowCards':'away.yellowCards',
		'AwayRedCards':'away.redCards', 'AwayTeamFormation':'away.teamFormation', 'HomeTeamYellowCardDetals':'home.teamYellowCardDetails', 'AwayTeamYellowCardDetails':'away.teamYellowCardDetails', 'HomeTeamRedCardDetails':'home.teamRedCardDetails', 'AwayTeamRedCardDetails':'away.teamRedCardDetails',
		'HomeLineupCoach':'home.lineupCoach', 'AwayLineupCoach':'away.lineupCoach'
		}

		for xmlMatch in xmlMatches:
			obj = self.parseProperties(xmlMatch.childNodes, valsDict)
			if 'goalDetails' in obj['home'].keys() and 'goalDetails' in obj['away'].keys():
				obj['home']['goalDetails'] = self.parseGoalDetails(obj['home']['goalDetails'])
				obj['away']['goalDetails'] = self.parseGoalDetails(obj['away']['goalDetails'])
			self.properties.extend([obj])

		return self.properties

	def getHistoricalMatchesByLeagueAndSeason(self, leagueName, season,options):
		htmlLeague = str(leagueName).replace(" ", "%20")
		self.url = 'http://www.xmlsoccer.com/FootballDataDemo.asmx/GetHistoricMatchesByLeagueAndSeason?ApiKey='+self.API_KEY+'&league='+htmlLeague+'&seasonDateString='+str(season)
		self.makeAPICall()
		xmlMatches = self.xmldoc.getElementsByTagName('XMLSOCCER.COM')[0].getElementsByTagName('Match')
		self.clearProperties()

		valsDict = {
		'Id':'matchID', 'FixtureMatch_Id':'fixtureID', 'Date':'date', 'Round':'round', 'Spectators':'spectators', 'League:':'league', 'HomeTeam':'home.name', 'HomeTeam_Id':'home.teamID',
		'HomeCorners':'home.cornerKicks', 'HomeGoals':'home.goals', 'HalfTimeHomeGoals':'home.halfTimeGoals', 'HomeShots':'home.shots', 'HomeShotsOnTarget':'home.shotsOnTarget', 'HomeFouls':'home.fouls',
		'HomeGoalDetails':'home.goalDetails', 'HomeLineupGoalkeeper':'home.lineupGoalkeeper', 'HomeLineupDefense':'home.lineupDefense', 'HomeLineupMidfield':'home.lineupMidfield', 'HomeLineupForward':'home.lineupForward',
		'HomeLineupSubstitutes':'home.lineupSubstitutes', 'HomeYellowCards':'home.yellowCards', 'HomeRedCards':'home.redCards', 'HomeSubDetails':'home.subDetails', 'AwaySubDetails':'away.subDetails', 'HomeTeamFormation':'home.teamFormation',
		'AwayTeam':'away.name', 'AwayCorners':'away.corners', 'AwayGoals':'away.goals', 'HalfTimeAwayGoals':'away.haltTimeGoals', 'AwayShots':'away.shots', 'AwayShotsOnTarget':'away.shotsOnTarget', 'AwayFouls':'away.fouls', 'AwayGoalDetails':'away.goalDetails',
		'AwayLineupGoalkeeper':'away.lineupGoalkeeper', 'AwayLineupDefense':'away.lineupDefense', 'AwayLineupMidfield':'away.lineupMidfield', 'AwayLineupForward':'away.lineupForward', 'AwayLineupSubstitutes':'away.lineupSubstitutes', 'AwayYellowCards':'away.yellowCards',
		'AwayRedCards':'away.redCards', 'AwayTeamFormation':'away.teamFormation', 'HomeTeamYellowCardDetals':'home.teamYellowCardDetails', 'AwayTeamYellowCardDetails':'away.teamYellowCardDetails', 'HomeTeamRedCardDetails':'home.teamRedCardDetails', 'AwayTeamRedCardDetails':'away.teamRedCardDetails',
		'HomeLineupCoach':'home.lineupCoach', 'AwayLineupCoach':'away.lineupCoach'
		}

		for xmlMatch in xmlMatches:
			obj = self.parseProperties(xmlMatch.childNodes, valsDict)
			if 'goalDetails' in obj['home'].keys() and 'goalDetails' in obj['away'].keys():
				obj['home']['goalDetails'] = self.parseGoalDetails(obj['home']['goalDetails'])
				obj['away']['goalDetails'] = self.parseGoalDetails(obj['away']['goalDetails'])
			self.properties.extend([obj])

		return self.properties


#F = Fixture()
#F.getHistoricalMatchesByLeagueAndSeason('Scottish Premier League', 1314,"-o")