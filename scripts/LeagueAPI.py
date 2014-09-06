import redis
import json
import pycurl
import cStringIO
from xml.dom import minidom
#https://docs.python.org/2/library/xml.dom.minidom.html

class League:
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
					tmpProperties[valDict[desiredPrprty]] = self.getText(node.childNodes)
					#print properties
		return tmpProperties

	def clearProperties(self):
			del self.properties[:]
			self.properties = []

	def getAllLeagues(self):
		self.clearProperties()
		self.url = 'http://www.xmlsoccer.com/FootballDataDemo.asmx/GetAllLeagues?ApiKey='+self.API_KEY
		self.makeAPICall()
		xmlLeagues = self.xmldoc.getElementsByTagName('XMLSOCCER.COM')[0].getElementsByTagName('League')
		valDict = {'Id':'ID', 'Name':'Name', 'Historical_Data':'HistoricalData', 'Fixtures':'Fixtures', 'Country':'Country', 'Livescore':'Livescore', 'NumberOfMatches':'NumberOfMatches', 'LatestMatch':'LatestMatch'}
		for xmlLeague in xmlLeagues:
			self.properties.extend([self.parseProperties(xmlLeague.childNodes, valDict)])
		return self.properties

