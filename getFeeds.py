#!/bin/bash

import urllib3 #https://pypi.python.org/pypi/urllib3
import shutil #https://docs.python.org/3/library/shutil.html
import validators #https://pypi.python.org/pypi/validators

class GetFeeds:
	"""A simple class to get RSS and ATOM feeds"""

	# Class variables shared by all instances
	feedDir = "./feeds/"
	mtaFeed = "http://www.malware-traffic-analysis.net/blog-entries.rss"

	# Instance variables unique to each instance
	def __init__(self, feedURL=mtaFeed, Outfile="default"):
		self.feedURL = feedURL
		self.Outfile = Outfile
		self.OutfileURL = self._buildOutfileURL()

	def getFeedURL(self):
		#print("\"" + self.feedURL + "\"")
		return self.feedURL

	def setFeedURL(self, url):
		if self._validateFeedURL(str(url)):
			self.feedURL = url
		else:
			print("ERROR: invalid URL sntax")

	def getOutfile(self):
		return self.Outfile

	def setOutfile(self, file):
		self.Outfile = file

	def downloadFeed(self):
		# http://stackoverflow.com/questions/27387783/how-to-download-a-file-with-urllib3
		http = urllib3.PoolManager()
		with http.request('GET', self.getFeedURL(), preload_content=False) as r, open(self.getOutfileURL(), 'wb') as rssFile:
			shutil.copyfileobj(r, rssFile) #https://docs.python.org/3.4/library/shutil.html

	def _validateFeedURL(self, url):
		return validators.url(url)

	def _buildOutfileURL(self):
		return str(self.feedDir + self.Outfile)

	def getOutfileURL(self):
		return self.OutfileURL