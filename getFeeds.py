#!/bin/bash

import urllib3 #https://pypi.python.org/pypi/urllib3
import shutil #https://docs.python.org/3/library/shutil.html
import validators #https://pypi.python.org/pypi/validators

class GetFeeds:
	"""A simple class to get RSS and ATOM feeds"""

	# Class variables shared by all instances
	mtaFeed = "http://www.malware-traffic-analysis.net/blog-entries.rss"

	# Instance variables unique to each instance
	def __init__(self, feedURL=mtaFeed, outFile=""):
		self.feedURL = feedURL
		self.outFile = outFile

	def getFeedURL(self):
		#print("\"" + self.feedURL + "\"")
		return str(self.feedURL)

	def setFeedURL(self, url):
		if self.validateFeedURL(str(url)):
			self.feedURL = url
		else:
			print("ERROR: invalid URL sntax")

	def getOutFile(self):
		return str(self.outFile)

	def setOutFile(self, file):
		self.outFile = file

	def downloadFeed(self):
		# http://stackoverflow.com/questions/27387783/how-to-download-a-file-with-urllib3
		http = urllib3.PoolManager()
		with http.request('GET', self.getFeedURL(), preload_content=False) as r, open(self.getOutFile(), 'wb') as rssFile:
			shutil.copyfileobj(r, rssFile) #https://docs.python.org/3.4/library/shutil.html

	def validateFeedURL(self, url):
		return validators.url(url)