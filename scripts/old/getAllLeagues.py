import redis
import json
import pycurl
import cStringIO
import pickle
from xml.dom import minidom
#https://docs.python.org/2/library/xml.dom.minidom.html

RPROD = redis.StrictRedis(host='localhost', port=6379, db = 0)
LEAGUES = 'leagues'

#reads the text within each XMl tag -- think of it as reading the actual values that are in text format
#So, for "Name" -- this function will read the actual value associated with the Name tag, which will 
# be the, for example:  Scottish Premier League
def getText(nodelist):
	rc = []
	for node in nodelist:
		if node.nodeType == node.TEXT_NODE:
			rc.append(node.data)
	return ''.join(rc)


#calls getText for each tag we care about for the league(id, name, etc..)
def leagueProperties(children):
	properties = {}
	for node in children:
		if node.nodeType == node.ELEMENT_NODE:
			leagueProperty = node.nodeName
			if(leagueProperty == "Id"):
				properties['ID'] = getText(node.childNodes)
			elif(leagueProperty == "Name"):
				properties['Name'] = getText(node.childNodes)
			elif(leagueProperty == "Historical_Data"):
				properties['HistoricalData'] = getText(node.childNodes)
			elif(leagueProperty == "Fixtures"):
				properties['Fixtures'] = getText(node.childNodes)
			elif(leagueProperty == "Country"):
				properties['Country'] = getText(node.childNodes)
			elif(leagueProperty == "Livescore"):
				properties['Livescore'] = getText(node.childNodes)
			elif(leagueProperty == "NumberOfMatches"):
				properties['NumberOfMatches'] = getText(node.childNodes)
			elif(leagueProperty == "LatestMatch"):
				properties['LatestMatch'] = getText(node.childNodes)
			#print getText(node.childNodes)
        #print getText(node.getElementsByTagName('Name')
	return properties


#for each Team, xml tag - this function will look for the id, name, stadium, website, and country for each Team
def teamProperties(children, mode):
	properties = {}
	for node in children:
		if node.nodeType == node.ELEMENT_NODE:
			teamProperty = node.nodeName
			if mode == 'normal':
				if(teamProperty == "Team_Id"):
					properties['ID'] = getText(node.childNodes)
				elif(teamProperty == "Name"):
					properties['Name'] = getText(node.childNodes)
				elif(teamProperty == "Stadium"):
					properties['Stadium'] = getText(node.childNodes)
				elif(teamProperty == "HomePageURL"):
					properties['Website'] = getText(node.childNodes)
				elif(teamProperty == "Country"):
					properties['Country'] = getText(node.childNodes)
			elif mode == 'standings':
				if(teamProperty == 'Team_Id'):
					properties['ID'] = getText(node.childNodes)
				elif(teamProperty == 'Played'):
					properties['gamesPlayed'] = getText(node.childNodes)
				elif(teamProperty == 'PlayedAtHome'):
					properties['gamesPlayedAtHome'] = getText(node.childNodes)
				elif(teamProperty == 'PlayedAway'):
					properties['playedAway'] = getText(node.childNodes)
				elif(teamProperty == 'Won'):
					properties['gamesWon'] = getText(node.childNodes)
				elif(teamProperty == 'Draw'):
					properties['gamesDrawn'] = getText(node.childNodes)
				elif(teamProperty == 'Lost'):
					properties['gamesLost'] = getText(node.childNodes)
				elif(teamProperty == 'NumberOfShots'):
					properties['shotsTaken'] = getText(node.childNodes)
				elif(teamProperty == 'YellowCards'):
					properties['yellowCards'] = getText(node.childNodes)
				elif(teamProperty == 'RedCards'):
					properties['redCards'] = getText(node.childNodes)
				elif(teamProperty == 'Goals_For'):
					properties['goalsScored'] = getText(node.childNodes)
				elif(teamProperty == 'Goals_Against'):
					properties['goalsConceded'] = getText(node.childNodes)
				elif(teamProperty == 'Goal_Difference'):
					properties['goalDifferential'] = getText(node.childNodes)
				elif(teamProperty == 'Points'):
					properties['points'] = getText(node.childNodes)
					
			#print getText(node.childNodes)
        #print getText(node.getElementsByTagName('Name')
	return properties




#for each team in the leage, it will cal the teamProperties function which parses the properties of the team(id, stadiums, etc..)
def teamsInLeague(xmldoc,league):
	if xmldoc != None:
		allProperties = []
		teams = xmldoc.getElementsByTagName('XMLSOCCER.COM')[0].getElementsByTagName('Team')
		for team in teams:
			properties = teamProperties(team.childNodes, "normal")
			properties['League'] = league
			allProperties.extend([properties])
		#print allProperties	
		return allProperties
	else:
		return None	

def teamStandings(xmldoc, league):
	if xmldoc != None:
		allProperties = []
		teams = xmldoc.getElementsByTagName('XMLSOCCER.COM')[0].getElementsByTagName('TeamLeagueStanding')
		for team in teams:
			properties = teamProperties(team.childNodes, "standings")
			allProperties.extend([properties])
		return allProperties
	else:
		return None



#abstracted function to make an API call - takes as input the URL
def makeAPICall(in_url):
	url = in_url.encode(encoding='UTF-8',errors='strict')#convert any unicode url into string, otherwise it will fail
	buf = cStringIO.StringIO()
	c = pycurl.Curl()
	c.setopt(c.URL, url)
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.perform()
	xmldoc = minidom.parseString(buf.getvalue())
	#print buf.getvalue()
	buf.close()
	c.close()
	return xmldoc


#main function -- makes API call for all leagues -- then for each league parses key info, then writes to redis collection
def start():
	teamsInLeagues = []
	leagues = []
	leagueTeams = []# for all teams in the league
	leagueStandings = [] #for all team standings in the league
	buf = cStringIO.StringIO()
	API_KEY = 'QUKJIFDZQOXAVSJLMIGQNDQHAVBWBQNBEJYNSFGAKBAHWBBXZU'
	getLeagues = 'http://www.xmlsoccer.com/FootballDataDemo.asmx/GetAllLeagues?ApiKey='+API_KEY
	xmldoc = makeAPICall(getLeagues)
	xmlLeagues = xmldoc.getElementsByTagName('XMLSOCCER.COM')[0].getElementsByTagName('League')
	
	properties = {}
	season = "1314" #YYAA  where YY = season in older year, and AA = season in new year
	for xmlLeague in xmlLeagues:
		fullTeamInfo = []
		properties = leagueProperties(xmlLeague.childNodes)
		htmlLeague = properties['Name'].replace(" ", "%20") #need to convert spaces to %20
		
		#Get teams for the League
		getTeams = 'http://www.xmlsoccer.com/FootballDataDemo.asmx/GetAllTeamsByLeagueAndSeason?ApiKey='+API_KEY+'&league='+htmlLeague+'&seasonDateString='+season
		xmldoc = makeAPICall(getTeams)
		leagueTeams.extend(teamsInLeague(xmldoc,properties['Name']))

		#Get team standings for this League
		getTeamStandings = 'http://www.xmlsoccer.com/FootballDataDemo.asmx/GetLeagueStandingsBySeason?ApiKey='+API_KEY+'&league='+htmlLeague+'&seasonDateString='+season
		xmldoc = makeAPICall(getTeamStandings)
		leagueStandings.extend(teamStandings(xmldoc, properties['Name']))
		#print leagueStandings
		
		for leagueTeam in leagueTeams:
			obj = {}
			obj['metadata'] = properties
			obj['team'] = leagueTeam
			obj['ID'] = properties['ID']
			fullTeamInfo.append(obj)
			
	
		for leagueStanding in leagueStandings:
			for tmp_obj in fullTeamInfo:
				if tmp_obj['team']['ID'] == leagueStanding['ID']:
					tmp_obj['team']['stats'] = {}
					tmp_obj['team']['stats'] = leagueStanding
					#print tmp_obj
					break

		teamsInLeagues.append(fullTeamInfo)
	
	print teamsInLeagues

 


start()

