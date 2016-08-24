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
		#Dictionary holding each feed and its associated entries (links)
		self.feedDict = {}
		#Create/load database
		self.db = self.createDB()
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
			return TinyDB(self.dbURL, default_table='feeds')
#Returns the second item of split, after protocol, as directory name
	def _buildOutDir(self, feedURL):
		tmp = feedURL.split('.').pop(1).strip(' \n\r\t')
		return tmp.strip(' \n\r\t')
#Returns the complete URL of file to store downloaded feed
	def _buildOutURL(self):
		tmp = self.feedDstRootDir + self.outDir + "/" + self.outfile
		return tmp.strip(' \n\r\t')
#Return MD5 hash string object of an entire file in binary mode
	def encFileMD5(self,inFile):
 		return hashlib.md5(open(inFile, mode='rb').read()).hexdigest().decode('utf-8')
#Return MD5 hash string object - must first convert to bytes
	def encStrMD5(self,inStr):
		return hashlib.md5(inStr.encode("utf-8")).hexdigest()
#Return MD5 hash string object
	def encBytesMD5(self, bObj):
		return hashlib.md5(bObj).hexdigest().decode('utf-8')
#Return Base64 encoded string object - must first convert to bytes
	def encStrB64(self, inStr):
		return base64.b64encode(inStr.encode('utf-8')).decode('utf-8')
#Return decoded Base64 string object from bytes
	def decStrB64(self, bObj):
		return base64.b64decode(bObj).decode('utf-8')
#Return Key for dictonary of blog feeds from feedparser link
	def genDictKey(self, inStr):
		return inStr.split('.').pop(1)
#Utilize feedparser to populate dictionary of entries from each URL in feeds/sources
# ***Eventually a test should be conducted for Internet connectivity prior to running!***
	def parseFeeds(self):
		#Get, and iterate, through each feed URL from sources folder
		for feed in self.blogFeed:
			#Create Feed Parser object from source URL
			fp = feedparser.parse(feed)
			#Temporarily store entries from each blog RSS/ATOM feed
			feedEntries = []
			
			for item in fp.entries:
				#List: [hash of feed entry link, plaintext feed entry link]
				feedEntries.append([self.encStrMD5(item.link), item.link])
			#Dictionary of each feed source. key is base64 of feed hostname, and value is list of entries
			self.feedDict[self.encStrB64(self.genDictKey(fp.feed.link))] = [self.encStrMD5(fp.modified), feedEntries]
			#Delete before next iteration - prevent duplication
			del(fp)
			del(feedEntries)

#Print out the dictionary of feed entries
	def printDict(self):
		try:
			self.feedDict
		except NameError:
			msg = "self.feedDict is not defined"
			print(msg)
		else:
			if (len(self.feedDict.keys())):
				for key in self.feedDict.keys():
					feedTitle = "Feed: " + self.decStrB64(key)
					lastModified = "Last Modified hash: " + self.feedDict[key][0]
					br = ""
					for x in range(0,80):
						br += "="					
					print(feedTitle + "\n" + lastModified + "\n" + br)
					for i,j in self.feedDict[key][1]:
						linkHash = i
						link = j
						print("Link hash: " + linkHash + "\n  " + link)
			else:
				msg = "Error: self.feedDict contains no entries"
				print(msg)				
