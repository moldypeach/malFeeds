#!/bin/bash

import urllib3 #https://pypi.python.org/pypi/urllib3
import shutil #https://docs.python.org/3/library/shutil.html
import validators #https://pypi.python.org/pypi/validators
import hashlib # For uniqueness comparisons
import os # For file system operations

class GetFeeds:
	"""A simple class to get RSS and ATOM feeds"""

	# Class variables shared by all instances
	feedBaseDir = "./feeds"
	feedSrcDir = feedBaseDir + "/sources"
	feedDownDir = "/downloads"
	mtaFeed = "http://www.malware-traffic-analysis.net/blog-entries.rss"

	# Instance variables unique to each instance
	def __init__(self, feedURL=mtaFeed, fileOut="default"):
		self.feedURL = feedURL
		self.outfile = fileOut
		self.outPATH = self._buildOutPath()
		self.outURL = self._buildOutURL()

	def getFeedURL(self):
		return self.feedURL

	def setFeedURL(self, url):
		if self._validateFeedURL(str(url)):
			self.feedURL = url
		else:
			print("ERROR: invalid URL sntax")

	def getOutfile(self):
		return self.outfile

	def setOutfile(self, fileOut):
		self.outfile = fileOut

	def downloadFeed(self):
		# http://stackoverflow.com/questions/27387783/how-to-download-a-file-with-urllib3
		http = urllib3.PoolManager()
		with http.request('GET', self.getFeedURL(), preload_content=False) as r, open(self.getOutURL(), 'wb') as rssFile:
			shutil.copyfileobj(r, rssFile) #https://docs.python.org/3.4/library/shutil.html

	def _validateFeedURL(self, url):
		return validators.url(url)

	def _buildOutPath(self):
		return str(self.feedDir + self.outfile)

	def _buildOutURL(self):
		return str(self.feedDir + self.outfile)

	def getOutURL(self):
		return self.outURL

	def genFileMD5(self,inFile):
		return hashlib.md5(open(inFile, mode='rb').read()).hexdigest()

	def genStrMD5(self,inStr):
		return hashlib.md5(inStr.encode("utf-8")).hexdigest()	
