#!/usr/bin/env python3.4
#External pkg dependencies
import feedparser
import validators #https://pypi.python.org/pypi/validators
import urllib3  #parseIPs
import certifi
from bs4 import BeautifulSoup  #parseIPs from <li>'s'

import hashlib # For uniqueness comparisons
import os, sys # For file system operations
import base64
import socket
import re  #parseIPs()
import datetime
from modules.malFeedDB import Database  #parseIPs
from modules.parseFeedsDB import ParseFeedsDB
#from modules.email import sendEmail

class ParseFeeds:
	""" Parse feeds URLs from source folder, download the resources, process and print the results"""

	feedBaseDir = "./feeds/"
	feedSrcDir = feedBaseDir + "sources/"
	#feedparser.USER_AGENT = "https://github.com/moldypeach/malFeeds"

	def __init__(self):
		#List of blog URLs
		self.blogFeed = []
		#Create list of feed URLs
		self.getFeeds()
		self.db = ParseFeedsDB()
		#Create tables - cached table obj is not stored when already present
		self.db.createTables(["tbl_IPREF", "tbl_UPDATED", "tbl_ENTRIES", "tbl_MALIPS"])
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
	#Breaks URL hyperlinks for surrounding last '.' with braces, e.g. co[.]uk
	def urlBreak(self,matchObj):
		if re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", matchObj.group(0)):
			return matchObj.group(0)
		else:
			i = matchObj.group(0).rfind('.')
			return matchObj.group(0)[:i] + matchObj.group(0)[i:].replace('.', '[.]')
	#Replaces matched characters
	def repChr(self,matchObj):
		if re.match("‑|‒|–|—|―|\u2011|\u2012|\u2013|\u2014|\u2015", matchObj.group(0)):
			#Replace any of the unicode hyphes with ASCII hyphen
			return matchObj.group(0).replace(matchObj.group(0), '-')
		else:
			#Replace nbsp with a space ' '
			return matchObj.group(0).replace(matchObj.group(0), ' ')

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
					eTag = tmp['etag']
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
					#etag.replace() prevents etag bug
					if not self.db.chkExists_tbl("tbl_UPDATED", "feed", feedTitle):
						if not "etag" in fp:
							etag = ""
							self.db.insert_tbl("tbl_UPDATED", {"feed":feedTitle, "etag":etag, "modified":fp.modified})
						else:
							self.db.insert_tbl("tbl_UPDATED", {"feed":feedTitle, "etag":fp.etag.replace("-gzip",""), "modified":fp.modified})
					else:
						if not "etag" in fp:
							etag = ""
							self.db.update_tbl("tbl_UPDATED", "feed", {"etag":etag}, feedTitle)
							self.db.update_tbl("tbl_UPDATED", "feed", {"modified":fp.modified}, feedTitle)							
						else:
							self.db.update_tbl("tbl_UPDATED", "feed", {"etag":fp.etag.replace("-gzip","")}, feedTitle)
							self.db.update_tbl("tbl_UPDATED", "feed", {"modified":fp.modified}, feedTitle)
			
					for item in fp.entries:
						urlHash = self.encStrMD5(item.link)
						#If urlHash isn't already in database, it must be new
						if not self.db.chkExists_tbl("tbl_ENTRIES", "urlHash", urlHash):
							self.parseIPs(item.link, urlHash)
						#List of hashed feed entry links, plaintext feed entry links
						self.db.insert_tbl("tbl_ENTRIES", {"urlHash":urlHash, "url":item.link, "feed":feedTitle})
			else:
				msg = "Feed download failed with HTTP status: " + fp.status
				print(msg)
				continue
			#Delete before next iteration - prevent duplication
			del(fp)

#Parse feed URLs for malicious IPs and extraneous info
	def parseIPs(self, urlIn, urlHash):
		user_agent = {'user-agent': 'https://github.com/moldypeach/malFeeds'}
		http = urllib3.PoolManager(
			headers=user_agent, 
			cert_reqs='CERT_REQUIRED', 
			ca_certs=certifi.where())
		rx_ip = re.compile("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(.*)")
		rx_date = re.compile("(\/\d{4}\/\d{2}\/\d{2}\/)")
		infoRx = re.compile("([a-zA-Z0-9]+(\.[a-zA-Z0-9]+)+)?")
		encRx = re.compile("‑|‒|–|—|―|\u2011|\u2012|\u2013|\u2014|\u2015|\u00A0| ")
		retries = urllib3.Retry(total=5, connect=0, read=3, redirect=2)
		req = http.request('GET', urlIn, retries=retries)

		match = rx_date.search(urlIn)
		date = match.group(0).strip('/') 

		if req.status == 200:
			soup = BeautifulSoup(req.data, 'html.parser')
			listItems = soup.find_all("li")
			noLI = False

			for i in listItems:
				text = i.get_text()
				match = rx_ip.match(text)
				if match:
					noLI = True
					ip = match.group(1).strip()
					
					tmp = re.sub(infoRx, self.urlBreak, match.group(2).strip())
					info = re.sub(encRx, self.repChr, tmp)
					del(tmp)
					self.db.insert_tbl("tbl_MALIPS", {"ip": ip, "date": date,"info": info, "urlHash": urlHash})
					#If IP is already known, associate new reference URLs to it as necessary
					ipRef = self.db.getItem_tbl('tbl_IPREF', 'ip', ip)
					if not ipRef:
						refList = [urlIn]
						self.db.insert_tbl('tbl_IPREF', {"ip":ip, "refs":refList})
					else:
						if urlIn not in ipRef["refs"]:
							ipRef["refs"].append(urlIn)
							self.db.update_tbl("tbl_IPREF", "ip", {"refs":ipRef["refs"]}, ip)
			#Apparently, on rare occasion a blog will be created with traffic in <p>'s instead of <li>'s.
			# e.g. http://www.broadanalysis.com/2016/09/19/rig-exploit-kit-via-pseudodarkleech-delivers-crypmic-ransomware/
			if not noLI:
				listItems = soup.find_all("p")
				for i in listItems:
					text = i.get_text()
					for line in re.split('\r\n|\r|\n', text):
						match = rx_ip.match(line)
						if match:
							ip = match.group(1).strip()
							
							tmp = re.sub(infoRx, self.urlBreak, match.group(2).strip())
							info = re.sub(encRx, self.repChr, tmp)
							del(tmp)
							self.db.insert_tbl("tbl_MALIPS", {"ip": ip, "date": date,"info": info, "urlHash": urlHash})
							#If IP is already known, associate new reference URLs to it as necessary
							ipRef = self.db.getItem_tbl('tbl_IPREF', 'ip', ip)
							if not ipRef:
								refList = [urlIn]
								self.db.insert_tbl('tbl_IPREF', {"ip":ip, "refs":refList})
							else:
								if urlIn not in ipRef["refs"]:
									ipRef["refs"].append(urlIn)
								self.db.update_tbl("tbl_IPREF", "ip", {"refs":ipRef["refs"]}, ip)
		else:
			#TODO: etter exception handling should be implemented
			msg = "ERROR: The following URL could not be retrieved: \r\n\t" + urlIn + "\r\n" 
			print(msg)


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
		#For getting IPs for three days prior to today. Adjust range accordingly for longer/shorter span
		for day in range(4):
			tmpDate = datetime.timedelta(days=day)
			ipDates.append((str(currDate - tmpDate).replace('-','/')))

		msgIPs = ""
		msgEntries = ""
		msgSubIPs = ""
		blogEntries = dict()
		ipSet = set()
		subIPSet = set()
		subIPRefsSet = set()
		#TODO: Explore more efficient means of accomplishing this block
		for date in ipDates:
			result = self.db.search_tbl('tbl_MALIPS', 'date', date)
			#Ignore any empty result list
			if result:
				for element in result:
					ip = element["ip"]
					info = element["info"]
					urlHash = element['urlHash']
					ipSet.add(ip)
					#Associates IPs with blog info for analyst consumption (some ips repeat because different info was analyzed)
					entry = ip + " " + info
					if urlHash not in blogEntries:
						blogEntries[urlHash] = [entry]
					else:
						blogEntries[urlHash].append(entry)
		#msgIPs are deduplicated for ease of pasting into summary db search
		for ip in ipSet:
			msgIPs += ip + "\r\n"
		#See if db contains any other ips in same /24
		slash24Dict = self.db.getSlash24IPs(ipSet)

		if slash24Dict:
			for element in sorted(slash24Dict.items(), key=lambda ipKey: socket.inet_aton(ipKey[0])):
				ip = element[0]
				url = ""
				for currURL in element[1]:
					url += "\t" + currURL.replace('http', 'hXXp') + "\r\n"
				msgSubIPs += (
					ip + "\r\n" + 
					url + "\r\n")
		else:
			msgSubIPs = "No IPs detected in the same /24 within current date range"

		#Append unique list referennce URLs for asssoicated IPs above
		for urlHash, entries in blogEntries.items():
			msgEntries += ("\r\n" + self.db.getUrlFromHash("tbl_ENTRIES", "urlHash", urlHash).replace('http', 'hXXp') + "\r\n")
			for entry in entries:
				msgEntries += "\t" + entry + "\r\n"
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

		emailFile = (
			"feeds/emails/email_" + str(datetime.date.today()) + "_ h" + str(datetime.datetime.now().hour) + "- m" + 
			str(datetime.datetime.now().minute))
		with open(emailFile, 'w') as f:
			f.write(outMsg)
			f.close()
		print(outMsg)
			
		#sendEmail(outMsg)