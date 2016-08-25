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

	#Return boolean of change to feed's last updated hash
	def chkUpdated(self,feedTitle, modifiedHash):
		return self.tbl_UPDATED.contains(q.feedTitle == modifiedHash)
	#Return boolean of urlHash's existence in tbl_ENTRIES
	def chkUrlHash(self, urlHash):
		return self.tbl_ENTRIES.contains(q.urlHash == urlHash)
	#Return string of plaintext url from tbl_ENTRIES
	def getUrlFromHash(self, urlHash):
		#tmp = "None" if item not found - should test for this on return
		tmp = self.tbl_ENTRIES.get(q.urlHash == urlHash)
		return tmp["url"]
	#Return feed title given urlHash
	def getFeedTitleFromUrlHash(self, urlHash):
		tmp = self.tbl_XREF.get(q.urlHash == urlHash)
		return tmp["feed"]
