import redis
import json
import pycurl
import cStringIO
from xml.dom import minidom
#https://docs.python.org/2/library/xml.dom.minidom.html

#THIS SCRIPT MUST BE RUN AFTER getAllLeagues!

RPROD = redis.StrictRedis(host='localhost', port = 6379, db = 0)
TEAMS = 'teams'
LEAGUES = 'leagues'
API_KEY = 'QUKJIFDZQOXAVSJLMIGQNDQHAVBWBQNBEJYNSFGAKBAHWBBXZU'

#reads the text within each XMl tag -- think of it as reading the actual values that are in text format
#So, for "Website" -- this function will read the actual value associated with the Website tag, which will 
# be the url
def getText(nodelist):
	rc = []
	for node in nodelist:
		if node.nodeType == node.TEXT_NODE:
			rc.append(node.data)
	return ''.join(rc)

#for each Team, xml tag - this function will look for the id, name, stadium, website, and country for each Team
def teamProperties(children):
	properties = {}
	for node in children:
		if node.nodeType == node.ELEMENT_NODE:
			teamProperty = node.nodeName
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
			#print getText(node.childNodes)
        #print getText(node.getElementsByTagName('Name')
	return properties

#a call to redis that will retrieve all of the leagues
def getLeagues():
	allLeagues = RPROD.hkeys(LEAGUES)
	return allLeagues
		
#abstracted function to make an API call - takes as input the URL
def makeAPICall(url):
	buf = cStringIO.StringIO()
	c = pycurl.Curl()
	c.setopt(c.URL, url)
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.perform()
	xmldoc = minidom.parseString(buf.getvalue())
	#print buf.getvalue()
	buf.close()
	return xmldoc

#for each team in the leage, it will cal the teamProperties function which parses the properties of the team(id, stadiums, etc..)
def teamsInLeague(xmldoc,league):
	if xmldoc != None:
		allProperties = []
		teams = xmldoc.getElementsByTagName('XMLSOCCER.COM')[0].getElementsByTagName('Team')
		for team in teams:
			properties = teamProperties(team.childNodes)
			properties['League'] = league
			allProperties.extend([properties])
		#print allProperties	
		return allProperties
	else:
		return None	

#main function -- pull all leagues, and for each league, finds all teams -- writes back to redis
def start():
	pipe = RPROD.pipeline()
	allProperties = []
	allLeagues = getLeagues()
	season = "1314" #YYAA  where YY = season in older year, and AA = season in new year
	if allLeagues != None:
		for league in allLeagues:
			htmlLeague = league.replace(" ", "%20") #need to convert spaces to %20
			getTeams = 'http://www.xmlsoccer.com/FootballDataDemo.asmx/GetAllTeamsByLeagueAndSeason?ApiKey='+API_KEY+'&league='+htmlLeague+'&seasonDateString='+season
			print getTeams
			xmldoc = makeAPICall(getTeams)
			allProperties.extend(teamsInLeague(xmldoc,league))
	#now write to Redis
	for team in allProperties:
		pipe.hmset(TEAMS, {team['Name']: json.dumps(team)})
	pipe.execute()
			
					
 

#call to start function
start()
