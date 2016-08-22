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
	db = TinyDB(dbURL, default_table='feeds')
	#Create database query object
	query = Query()

	def __init__(self):
		#List of blog URLs
		self.blogs = []
		self.feedEntries[]
		#Each instance maintains its own feed resource
		#self.fp = feedparser.parse(feedFile)
		#Dictionary holding each feed and its associated entries (links)
		self.feedDict = {}

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
					self.blogs.append(currFeed)
				else:
					next()
			if not self.feeds:
				msg = self.FeedSrcDir + " contains no feed files"
				print(msg)
				sys.exit()

#Validates http(s):// URL is valid
	def validateFeedURL(self, url):
		if validators.url(url):
			return True
		else:
			print("ERROR: invalid URL sntax:\n\t" + url)

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

	def parseFeeds(self):
		#Get, and iterate, through each feed URL from sources folder
		for feed in self.blogs:
			fp = feedparser.parse(feed)
			print(fp.modified)
			
			for item in fp.entries:
				self.feeds.append([self.genStrMD5(item.link.encode('utf-8'), item.link.encode('utf-8'))])
				#print("item type: " + type(item).__name__)
				for i in se
