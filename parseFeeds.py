import feedparser
import hashlib

class parseFeeds:
	""" Parse downloaded feeds and look for updates"""

	#All instances share an object to create hashes of content
	#Syntax: h.update("whatever your string is".encode('utf-8')).hexdigest() - encode ensures byte data
	h = hashlib.md5()

	def __init__(self, feedFile="mta.rss"):
		#Each instance maintains its own feed resource
		fp = feedparser.parse(feedFile)
