from tinydb import TinyDB, Query #tinydb.readthedocs.io/en/latest/

class Database:
	""" Perform database work """

	def __init__(self):
		#Create/load database
		self.db = self.createDB()
		self.q = Query()

	#Create the database object
	def createDB(self,dbDir = "./feeds/db/" ,dbFile = "malfeeds.json"):
		dbURL = dbDir + dbFile
		#Test to ENSURE db gets created and exit if not? 10Sep16
		try:
			os.makedirs(dbDir, exist_ok=False)
		except OSError:
			msg = dbDir + " already exists."
			print(msg)
		else:
			if not os.path.exists(dbURL, name="default"):
				msg = dbURL + " does not exist. Attempting to create."
		finally:
			return TinyDB(dbURL)

	#Create Tables
	def createTables(self, tblList):
		if tblList:
			for tbl in tblList:
				self.db.table(tbl)
		else:
			msg = "ERROR: table list cannot be empty"
			print(msg)
			sys.exit()

	#Insert items into table tableIn
	def insert_tbl(self,tableIn,value):
		self.db.table(tableIn).insert(value)

	#Update item in table
	def update_tbl(self,tableIn, keyIn, fields, matchVal):
		self.db.table(tableIn).update(fields, self.q[keyIn] == matchVal)

	#Search table for value(s)
	def search_tbl(self, tableIn, keyIn, matchVal):
		return self.db.table(tableIn).search(self.q[keyIn] == matchVal)

	#Check if a value exists in table (returns boolean)
	def chkExists_tbl(self, tableIn, keyIn, matchVal):
		return self.db.table(tableIn).contains(self.q[keyIn] == matchVal)

	#Show all tables
	def printTables(self):
		print(self.db.tables())

	#Print table entries
	def printTableEntries(self, tableIn):
		for i in self.db.table(tableIn).all():
			print(i)