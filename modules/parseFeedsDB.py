#!/usr/bin/env python3.4
#External pkg dependencies
from tinydb import TinyDB, Query #tinydb.readthedocs.io/en/latest/

from modules.malFeedDB import Database

class ParseFeedsDB(Database):
	""" Represents tinyDB object specific to parseFeeds object """
	def __init__(self):
		""" initialize attributes of parent class """
		super().__init__()


	#Return string of plaintext url from tbl_ENTRIES
	def getUrlFromHash(self,tableIn, keyIn, hashVal):
		#tmp = "None" if item not found - should test for this on return
		tmp = self.db.table(tableIn).get(self.q[keyIn] == hashVal)
		return tmp["url"]
	#Return feed title given urlHash
	def getFeedTitleFromUrlHash(self,tableIn,keyIn, hashVal):
		tmp = self.db.table(tableIn).get(self.q[keyIn] == hashVal)
		return tmp["feed"]
	#Return feed's last known etag or modified value
	def getFeedLastMod(self,tableIn,keyIn, feedTitle):
		tmp = self.db.table(tableIn).get(self.q[keyIn] == feedTitle)
		return tmp

	#Return set of unique ips matching regex on /24 along with ref urls
	def getSlash24IPs(self,matchSet):
		slash24Dict = {}
		for ip in matchSet:
			#strips .\d* from given ip string and returns the first three octets
			slash24 = ip.rsplit('.', maxsplit=1)[0] + "."
			#Each IP has it's own ref list, check each IP for more than one match
			tmp = self.rxSearch_tbl("tbl_IPREF", "ip", slash24)
			#skip singletons
			if len(tmp) > 1:
				for element in tmp:
					currIP = element["ip"]
					currRefs = element["refs"]
					slash24Dict[currIP] = currRefs

		return slash24Dict