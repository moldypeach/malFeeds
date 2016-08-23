import feedparser
#from getFeeds import GetFeeds
#import urllib3 #https://pypi.python.org/pypi/urllib3
import shutil #https://docs.python.org/3/library/shutil.html
import validators #https://pypi.python.org/pypi/validators
import hashlib # For uniqueness comparisons
import os, sys # For file system operations
import base64
from tinydb import TinyDB, Query #tinydb.readthedocs.io/en/latest/

class ParseFeeds:
	""" Parse feeds URLs from source folder"""

	feedBaseDir = "./feeds/"
	feedSrcDir = feedBaseDir + "sources/"
	dbDir = "./feeds/db/"
	dbFile = "malfeeds.json"
	dbURL = dbDir + dbFile
	#Create database object
	#db = TinyDB(dbURL, default_table='feeds')
	#Create database query object
	query = Query()

	def __init__(self):
		#List of blog URLs
		self.blogFeed = []
		#Store etries in each blog RSS/ATOM feed
		self.feedEntries = []
		#Dictionary holding each feed and its associated entries (links)
		self.feedDict = {}
		#Create/load database
		self.createDB()
		#Create list of feed URLs
		self.getFeeds()

	def getFeeds(self):
		for feed in os.listdir(self.feedSrcDir):
			try:
				currFile = open(self.feedSrcDir + feed, "r")
				currFeed = currFile.read().strip(' \n\r\t')
			except:
				msg ="Error opening " + self.feedSrcDir + feed
				print(msg)
			else:
				if self.validateFeedURL(currFeed):
					self.blogFeed.append(currFeed)
				else:
					next()
			if not self.blogFeed:
				msg = self.FeedSrcDir + " contains no feed files"
				print(msg)
				sys.exit()

#Validates http(s):// URL is valid
	def validateFeedURL(self, url):
		if validators.url(url):
			return True
		else:
			print("ERROR: invalid URL sntax:\n\t" + url)
#Create the database object
	def createDB(self):
		try:
			os.makedirs(self.dbDir, exist_ok=False)
		except OSError:
			msg = self.dbDir + " already exists."
			print(msg)
		else:
			if not os.path.exists(self.dbURL):
				msg = self.dbURL + " does not exist. Attempting to create."
		finally:
			db = TinyDB(self.dbURL, default_table='feeds')
#Returns the second item of split, after protocol, as directory name
	def _buildOutDir(self, feedURL):
		tmp = feedURL.split('.').pop(1).strip(' \n\r\t')
		return tmp.strip(' \n\r\t')
#Returns the complete URL of file to store downloaded feed
	def _buildOutURL(self):
		tmp = self.feedDstRootDir + self.outDir + "/" + self.outfile
		return tmp.strip(' \n\r\t')
#Return MD5 hash of an entire file in binary mode
	def genFileMD5(self,inFile):
 		return hashlib.md5(open(inFile, mode='rb').read()).hexdigest()
#Return MD5 hash of a string converted to utf-8, which returns a bytes object
	def genStrMD5(self,inStr):
		return hashlib.md5(inStr.encode("utf-8")).hexdigest()
#Return MD5 hash of a byyes object
	def genBytesMD5(self, bObj):
		return hashlib.md5(bObj).hexdigest()
#Return Base64 encoded bytes object from string
	def genStrB64(self, inStr):
		return base64.b64encode(inStr.encode('utf-8'))
#Return Key for dictonary of blog feeds from feedparser link
	def genDictKey(self, inStr):
		return inStr.split('.').pop(1)

	def parseFeeds(self):
		#Get, and iterate, through each feed URL from sources folder
		for feed in self.blogFeed:
			fp = feedparser.parse(feed)
			print(fp.modified)
			
			for item in fp.entries:
				self.feedEntries.append([self.genStrMD5(item.link), item.link.encode('utf-8')])
			self.feedDict[self.genStrB64(self.genDictKey(fp.feed.link))] = self.feedEntries
		print(self.feedDict.keys())

