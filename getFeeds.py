#!/bin/bash

import urllib3 #https://pypi.python.org/pypi/urllib3
import shutil #https://docs.python.org/3/library/shutil.html
import validators #https://pypi.python.org/pypi/validators
import hashlib # For uniqueness comparisons
import os # For file system operations

class GetFeeds:
	"""A simple class to get RSS and ATOM feeds"""

	# Class variables shared by all instances
	feedBaseDir = "./feeds/"
	feedSrcDir = feedBaseDir + "sources/"
	feedDownDir = "/downloads"

	# Instance variables unique to each instance
	def __init__(self, feedURL):
		self.feedURL = self.setFeedURL(feedURL)
		self.outfile = self._buildOutFile()
		self.outDir = self._buildOutDir()
		self.outURL = self._buildOutURL()

	def getFeedURL(self):
		return self.feedURL
	#Validates http(s):// URL is valid
	def setFeedURL(self, url):
		if validators.url(url):
			return url
		else:
			print("ERROR: invalid URL sntax")
	#Download feed and write it to a file previously defined
	def downloadFeed(self):
		# http://stackoverflow.com/questions/27387783/how-to-download-a-file-with-urllib3
		http = urllib3.PoolManager()
		with http.request('GET', self.feedURL, preload_content=False) as r, open(self.outURL, 'wb') as rssFile:
			shutil.copyfileobj(r, rssFile) #https://docs.python.org/3.4/library/shutil.html
	#Returns last item of split URL list as the filename, e.g. file.rss
	def _buildOutFile(self):
		return self.feedURL.split('/').pop(-1)
	#Returns the second item of split, after protocol, as directory name
	def _buildOutDir(self):
		return self.feedURL.split('.').pop(1)
	#Returns the complete URL of file to store downloaded feed
	def _buildOutURL(self):
		return self.feedSrcDir + self.outfile
	#Return MD5 hash of an entire file in binary mode
	def genFileMD5(self,inFile):
		return hashlib.md5(open(inFile, mode='rb').read()).hexdigest()
	#Return MD5 hash of a string converted to utf-8, which returns a bytes object
	def genStrMD5(self,inStr):
		return hashlib.md5(inStr.encode("utf-8")).hexdigest()

