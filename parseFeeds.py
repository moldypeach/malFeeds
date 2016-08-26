import feedparser
import shutil #https://docs.python.org/3/library/shutil.html
import validators #https://pypi.python.org/pypi/validators
import hashlib # For uniqueness comparisons
import os, sys # For file system operations
import base64
from malFeedDB import Database

class ParseFeeds:
	""" Parse feeds URLs from source folder"""

	feedBaseDir = "./feeds/"
	feedSrcDir = feedBaseDir + "sources/"

	def __init__(self):
		#List of blog URLs
		self.blogFeed = []
		#Create list of feed URLs
		self.getFeeds()
		self.db = Database()
		#List of new feed entries for further processing
		self.newURLs = []
		self.parseFeeds()

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
		# boolean - test if element exists before getting value: e.g. 'title' in fp.feed
		#Get, and iterate, through each feed URL from sources folder
		for feed in self.blogFeed:
			#Name of feed. Used to store said feed's dictionary items
			feedTitle = self.genDictKey(feed)
			#Check if a feed already has db entry - block saves on bandwidth usage
			if self.db.chkExistsUpdated(feedTitle):
				tmp = self.db.getFeedLastMod(feedTitle)
				if tmp['etag'] != '':
					eTag = tmp['etag'].replace("-gzip","") #replace resolves etag bug
					fp = feedparser.parse(feed, etag=eTag)
				else:
					feedMod = tmp['modified']
					fp = feedparser.parse(feed, modified=feedMod)
				del(tmp)
			else:
				fp = feedparser.parse(feed)
			
			#Test for required variables from feedparser - fp.entries[0] only tests there is at least one item
			if fp.status == 304:
				msg =  feedTitle + " has not been modified since last check"
				print(msg)
				continue
			elif fp.status == 200:
				if not all ((('modified' in fp or 'etag' in fp), 'link' in fp.feed, 'status' in fp, 'link' in fp.entries[0] )):
					msg = "ERROR: One or more required feed elements was missing"
					print(msg)
					continue
				else:
					if not self.db.chkExistsUpdated(feedTitle):
						self.db.insUPDATED_tbl({"feed":feedTitle, "etag":fp.etag, "modified":fp.modified})					
					else:
						self.db.updUPDATED_tbl({"etag":fp.etag}, feedTitle)
						self.db.updUPDATED_tbl({"modified":fp.modified}, feedTitle)
			
					for item in fp.entries:
						urlHash = self.encStrMD5(item.link)
						#If urlHash isn't already in database, it must be new
						if not self.db.chkExistsEntries(urlHash):
							self.newURLs.append({"url":item.link})
						#List of hashed feed entry links, plaintext feed entry links
						self.db.insENTRIES_tbl({"urlHash":urlHash, "url":item.link})
						self.db.insXREF_tbl({"urlHash":urlHash, "feed":feedTitle})
			else:
				msg = "Feed download failed with HTTP status: " + fp.status
				print(msg)
				continue
			#Delete before next iteration - prevent duplication
			del(fp)
#Print out the dictionary of feed entries
	def printDict(self):
		try:
			self.feedDict
		except NameError:
			msg = "self.feedDict is not defined"
			print(msg)
		else:
			if (len(self.feedDict.keys())):
				for feed in self.feedDict.keys():
					feedTitle = "Feed: " + feed
					for key in self.feedDict[feed].keys():
						if key == "modified":
							lastModified = "Last Modified hash: " + self.feedDict[feed][key]
							br = ""
							for x in range(0,80):
								br += "="					
							print(feedTitle + "\n" + lastModified + "\n" + br)
						else:
							for lnkHash in self.feedDict[feed][key]:
								link = self.feedDict[feed][key][lnkHash]
								print("Link hash: " + lnkHash + "\n  " + link)
			else:
				msg = "Error: self.feedDict contains no entries"
				print(msg)

