import redis
import json
import pycurl
import cStringIO
from xml.dom import minidom
#https://docs.python.org/2/library/xml.dom.minidom.html

class Player:
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
					tmpProperties[valDict[desiredPrprty]] = self.getText(node.childNodes).rstrip().lstrip()
					#print properties
		return tmpProperties


	def clearProperties(self):
		del self.properties[:]
		self.properties = []

	def getPlayersByTeam(self,teamID):
		self.url = 'http://www.xmlsoccer.com/FootballDataDemo.asmx/GetPlayersByTeam?ApiKey='+self.API_KEY+'&teamId='+str(teamID)
		self.makeAPICall()
		xmlPlayers = self.xmldoc.getElementsByTagName('XMLSOCCER.COM')[0].getElementsByTagName('Player')
		
		self.clearProperties()

		valDict = {'Id':'ID', 'Name':'Name', 'Height':'Height', 'Weight':'Weight', 'Nationality':'Nationality', 'Position':'Position', 'Team_Id':'TeamID', 'PlayerNumber':'JerseyNumber', 'DateOfBirth':'Birthday', 'DateOfSigning':'SignDate', 'Signing':'Signing'}
		for xmlPlayer in xmlPlayers:
			self.properties.extend([self.parseProperties(xmlPlayer.childNodes, valDict)])
		#print properties
		return self.properties

	def getPlayerById(self, playerID):
		self.url =  'http://www.xmlsoccer.com/FootballDataDemo.asmx/GetPlayerById?ApiKey='+self.API_KEY+'&playerId='+str(playerID)
		self.makeAPICall()
		xmlPlayers = self.xmldoc.getElementsByTagName('XMLSOCCER.COM')[0].getElementsByTagName('Player')
		self.clearProperties()
		valDict = {'Id':'ID', 'Name':'Name', 'Height':'Height', 'Weight':'Weight', 'Nationality':'Nationality', 'Position':'Position', 'Team_Id':'TeamID', 'PlayerNumber':'JerseyNumber', 'DateOfBirth':'Birthday', 'DateOfSigning':'SignDate', 'Signing':'Signing'}
		for xmlPlayer in xmlPlayers:
			return self.parseProperties(xmlPlayer.childNodes,valDict)
	
	def setRosterInTeam(self, teamID):
		self.clearProperties()
		players = self.getPlayersByTeam(teamID)
		return {'roster': players}

#p = Player()
#print p.getPlayerById(11510)
#print p.setRosterInTeam(1)
#p.getPlayersByTeam(1)
