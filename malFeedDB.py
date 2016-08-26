from tinydb import TinyDB, Query #tinydb.readthedocs.io/en/latest/

class Database:
	""" Perform database work """

	dbDir = "./feeds/db/"
	dbFile = "malfeeds.json"
	dbURL = dbDir + dbFile

	def __init__(self):
		#Create/load database
		self.db = self.createDB()
		self.tbl_XREF = self.db.table("tbl_XREF")
		self.tbl_UPDATED = self.db.table("tbl_UPDATED")
		self.tbl_ENTRIES = self.db.table("tbl_ENTRIES")
		#Query object for searching database tables
		self.q = Query()

	#Create the database object
	def createDB(self):
		try:
			os.makedirs(self.dbDir, exist_ok=False)
		except OSError:
			msg = self.dbDir + " already exists."
			print(msg)
		else:
			if not os.path.exists(self.dbURL, name="default"):
				msg = self.dbURL + " does not exist. Attempting to create."
		finally:
			return TinyDB(self.dbURL)

	#Insert items into tbl_XREF
	def insXREF_tbl(self,value):
		self.tbl_XREF.insert(value)
	#Insert items into tbl_UPDATED
	def insUPDATED_tbl(self,value):
		self.tbl_UPDATED.insert(value)
	#Insert items into tbl_ENTRIES
	def insENTRIES_tbl(self,value):
		self.tbl_ENTRIES.insert(value)

	#Update modified hash for a feed - passed fields are updated where q.feed is a match
	def updUPDATED_tbl(self, fields, feedTitle):
		self.tbl_UPDATED.update(fields, self.q.feed == feedTitle)

	#Check a feed exists in tbl_UPDATED
	def chkExistsUpdated(self, feedTitle):
		return self.tbl_UPDATED.contains(self.q.feed == feedTitle)
	#Check if a url (urlHash) already exists in tbl_ENTRIES
	def chkExistsEntries(self, hashVal):
		return self.tbl_ENTRIES.contains(self.q.urlHash == hashVal)
	#Return boolean of change to feed's last updated hash
	#def chkUpdated(self,feedTitle, modifiedHash):
	#	return self.tbl_UPDATED.contains((self.q.feed == feedTitle)&(q.modHash == modifiedHash))
	#Return boolean of urlHash's existence in tbl_ENTRIES
	def chkUrlHash(self, hashVal):
		return self.tbl_ENTRIES.contains(q.urlHash == hashVal)
	#Return string of plaintext url from tbl_ENTRIES
	def getUrlFromHash(self, hashVal):
		#tmp = "None" if item not found - should test for this on return
		tmp = self.tbl_ENTRIES.get(self.q.urlHash == hashVal)
		return tmp["url"]
	#Return feed title given urlHash
	def getFeedTitleFromUrlHash(self, hashVal):
		tmp = self.tbl_XREF.get(self.q.urlHash == hashVal)
		return tmp["feed"]
	#Return feed's last known etag or modified value
	def getFeedLastMod(self, feedTitle):
		tmp = self.tbl_UPDATED.get((self.q.feed == feedTitle))
		return tmp
