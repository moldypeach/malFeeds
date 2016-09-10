from tinydb import TinyDB, Query #tinydb.readthedocs.io/en/latest/
from malFeedDB import Database

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
