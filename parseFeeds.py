#!/usr/bin/env python3.4
import feedparser
import shutil #https://docs.python.org/3/library/shutil.html
import validators #https://pypi.python.org/pypi/validators
import hashlib # For uniqueness comparisons
import os, sys # For file system operations
import base64
import socket
import smtplib
from email.mime.text import MIMEText
import urllib3  #parseIPs
import re  #parseIPs
from bs4 import BeautifulSoup  #parseIPs
from malFeedDB import Database  #parseIPs
import datetime
from parseFeedsDB import ParseFeedsDB

class ParseFeeds:
	""" Parse feeds URLs from source folder"""

	feedBaseDir = "./feeds/"
	feedSrcDir = feedBaseDir + "sources/"

	def __init__(self):
		#List of blog URLs
		self.blogFeed = []
		#Create list of feed URLs
		self.getFeeds()
		self.db = ParseFeedsDB()
		#Create tables - cached table obj is not stored when already present
		self.db.createTables(["tbl_XREF", "tbl_UPDATED", "tbl_ENTRIES", "tbl_MALIPS"])
		#List of new feed entries for further processing
		self.parseFeeds()
		self.createMessage()

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
			if self.db.chkExists_tbl("tbl_UPDATED", "feed", feedTitle):
				tmp = self.db.getFeedLastMod("tbl_UPDATED", "feed", feedTitle)
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
					if not self.db.chkExists_tbl("tbl_UPDATED", "feed", feedTitle):
						self.db.insert_tbl("tbl_UPDATED", {"feed":feedTitle, "etag":fp.etag, "modified":fp.modified})					
					else:
						self.db.update_tbl("tbl_UPDATED", "feed", {"etag":fp.etag}, feedTitle)
						self.db.update_tbl("tbl_UPDATED", "feed", {"modified":fp.modified}, feedTitle)
			
					for item in fp.entries:
						urlHash = self.encStrMD5(item.link)
						#If urlHash isn't already in database, it must be new
						if not self.db.chkExists_tbl("tbl_ENTRIES", "urlHash", urlHash):
							self.parseIPs(item.link, urlHash)
						#List of hashed feed entry links, plaintext feed entry links
						self.db.insert_tbl("tbl_ENTRIES", {"urlHash":urlHash, "url":item.link})
						self.db.insert_tbl("tbl_XREF", {"urlHash":urlHash, "feed":feedTitle})
			else:
				msg = "Feed download failed with HTTP status: " + fp.status
				print(msg)
				continue
			#Delete before next iteration - prevent duplication
			del(fp)

#Parse feed URLs for malicious IPs and extraneous info
	def parseIPs(self, urlIn, urlHash):
		http = urllib3.PoolManager()
		rx_ip = re.compile("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(.*)")
		rx_date = re.compile("(\/\d{4}\/\d{2}\/\d{2}\/)") 
		req = http.request('GET', urlIn)

		match = rx_date.search(urlIn)
		date = match.group(0).strip('/') 

		if req.status == 200:
			soup = BeautifulSoup(req.data, 'html.parser')
			listItems = soup.find_all("li")

			for i in listItems:
				text = i.get_text()
				match = rx_ip.match(text)
				if match:
					ip = match.group(1).strip()
					info = match.group(2).strip()
					#TODO: sanatize malicious URLs on insert, e.g. replace *.com with *[.]com
					self.db.insert_tbl("tbl_MALIPS", {"ip": ip, "date": date,"info": info, "urlHash": urlHash})

#Format new entry messagee
	def createMessage(self):
		#TODO: Don't need currDate for final version as new blog entries will possess the currDate already
		#For testing, however, this allows the retrieval of data from a reference  point
		#TODO: This method should be only be called when new entires are present
		currDate = datetime.date.today()
		ipDates = []
		ipDates.append(str(currDate).replace('-','/'))
		br = ""
		for n in range(1,81):
			br += "*"
		#For getting IPs for three days prior to today
		for day in range(4):
			tmpDate = datetime.timedelta(days=day)
			ipDates.append((str(currDate - tmpDate).replace('-','/')))

		msgIPs = ""
		msgEntries = ""
		msgSubIPs = ""
		ipSet = set()
		refURLs = set()
		subIPSet = set()
		subIPRefsSet = set()
		for date in ipDates:
			result = self.db.search_tbl('tbl_MALIPS', 'date', date)
			#Ignore any empty result list
			if result:
				for element in result:
					ip = element["ip"]
					info = element["info"]
					ipSet.add(ip)
					#Associates IPs with blog info for analyst consumption (some ips repeat because different info was analyzed)
					msgEntries += ip + " " + info + "\r\n"
					refURLs.add(element["urlHash"])
		#msgIPs are duplicated for ease of pasting into summary db search
		for ip in ipSet:
			msgIPs += ip + "\r\n"
		#See if db contains any other ips in same /24
		#TODO: Because of the way I stored unique IPs I am presently not capturing all of the ref-
		#erence URLs associated with each IP, but rather just one of them. This should be addressed!
		slash24Dict = self.db.getSlash24IPs(ipSet)

		if slash24Dict:
			for element in sorted(slash24Dict.items(), key=lambda ipKey: socket.inet_aton(ipKey[0])):
				ip = element[0]
				url = element[1]["url"]
				msgSubIPs += (
					ip + "\r\n" + 
					"\t" + url + "\r\n")
		else:
			msgSubIPs = "No IPs detected in the same /24 within current date range"

		#Append unique list referennce URLs for asssoicated IPs above
		for urlHash in refURLs:
			msgEntries += self.db.getUrlFromHash("tbl_ENTRIES", "urlHash", urlHash) + "\r\n"

		outMsg = (
			"EK traffic IPs over the last three days" + "\r\n" + 
			br + "\r\n" +  
			br + "\r\n" + 
			msgIPs + "\r\n" + 
			"EK traffic IPs (with info) from blog entries" + "\r\n" + 
			br + "\r\n" + 
			br + "\r\n" + 
			msgEntries + "\r\n" + 
			"EK traffic IPs occuring on same /24" + "\r\n" + 
			br + "\r\n" + 
			br + "\r\n" + 
			msgSubIPs)
		self.sendEmail(outMsg)
