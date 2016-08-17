#!/bin/bash

import urllib3 #https://pypi.python.org/pypi/urllib3
import shutil #https://docs.python.org/3/library/shutil.html
import validators #https://pypi.python.org/pypi/validators
import hashlib # For uniqueness comparisons
import os, sys # For file system operations

class GetFeeds:
	"""A simple class to get RSS and ATOM feeds"""

	# Class variables shared by all instances
	feedBaseDir = "./feeds/"
	feedSrcDir = feedBaseDir + "sources/"
	feedDstRootDir = feedBaseDir + "downloads/"
	feedDstDir = ""

	# Instance variables unique to each instance
	def __init__(self):
		self.feeds = []
		self.getFeeds()
		#self.feedURL = self.setFeedURL(feedURL)
		self.outfile = ""
		self.outDir = ""
		self.outURL = ""

	def getFeeds(self):
		for feed in os.listdir(self.feedSrcDir):
			try:
				currFile = open(self.feedSrcDir + feed, "r")
				currFeed = currFile.read()
				#print(currFeed)
			except:
				msg ="Error opening " + self.feedSrcDir + feed
				print(msg)
			else:
				if self.validateFeedURL(currFeed):
					self.feeds.append(currFeed)
				else:
					next()
		if not self.feeds:
			msg = self.FeedSrcDir + " contains no feed files"
			print(msg)
			sys.exit()
		else:
			for item in self.feeds:
				print("Item ln 46: " + item)
				self.outfile = self._buildOutFile(item)
				print("outfile ln 47: " + self.outfile)
				self.outDir = self._buildOutDir(item)
				print("outDir ln 49: " + self.outDir)
				self.feedDstDir = self.feedDstRootDir + self.outDir
				print("feedDstDir ln 52: " + self.feedDstDir)
				self.outURL = self._buildOutURL()
				print("outURL ln 54: " + self.outURL)
				self.downloadFeed(item)
	#Return the current feed URL
	def getFeedURL(self):
		return self.feedURL
	#Validates http(s):// URL is valid
	def validateFeedURL(self, url):
		if validators.url(url):
			return True
		else:
			print("ERROR: invalid URL sntax:\n\t" + url)
	#Download feed and write it to a file previously defined
	def downloadFeed(self, feedURL):
		print("feedURL ln 67: " + feedURL)
		#Create feed download directory if it doesn't already exist
		#os.makedirs(self.feedDstRootDir, exist_ok=True)
		os.makedirs(self.feedDstDir, exist_ok=True)

		# http://stackoverflow.com/questions/27387783/how-to-download-a-file-with-urllib3
		http = urllib3.PoolManager()
		with http.request('GET', feedURL, preload_content=False) as r, open(self.outURL, 'wb') as rssFile:
			shutil.copyfileobj(r, rssFile) #https://docs.python.org/3.4/library/shutil.html
	#Returns last item of split URL list as the filename, e.g. file.rss
	def _buildOutFile(self, feedURL):
		return feedURL.split('/').pop(-1)
	#Returns the second item of split, after protocol, as directory name
	def _buildOutDir(self, feedURL):
		return feedURL.split('.').pop(1)
	#Returns the complete URL of file to store downloaded feed
	def _buildOutURL(self):
		return self.feedDstRootDir + self.outDir + "/" + self.outfile
	#Return MD5 hash of an entire file in binary mode
	def genFileMD5(self,inFile):
		return hashlib.md5(open(inFile, mode='rb').read()).hexdigest()
	#Return MD5 hash of a string converted to utf-8, which returns a bytes object
	def genStrMD5(self,inStr):
		return hashlib.md5(inStr.encode("utf-8")).hexdigest()

