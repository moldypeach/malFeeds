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

	#Return set of unique ips matching regex on /24 along with ref urls
	def getSlash24IPs(self,matchSet):
		slash24Dict = {}
		for ip in matchSet:
			#strips .\d* from given ip string and returns the first three octets
			slash24 = ip.rsplit('.', maxsplit=1)[0] + "."
			#present result set may include an IP reported more than once, but on different days
			tmp = self.rxSearch_tbl("tbl_MALIPS", "ip", slash24)
			#Test that the result set exists, skip singletons from the get-go, 
			#and then loop 2x to ensure no duplicates
			if tmp and len(tmp) > 1:
				for element in tmp:
					currIP = element["ip"]
					uniq = True
					for subElement in tmp:
						if subElement["ip"] != currIP:
							uniq = False
					if not uniq:
						if not currIP in slash24Dict:
							urlHash = element["urlHash"]
							slash24Dict[currIP] = {"url": urlHash}
		#Update hash of URL with actual URL in dictionary
		if slash24Dict:
			for ip, urlHash in slash24Dict.items():
				result = self.search_tbl("tbl_ENTRIES", "urlHash", urlHash["url"])
				hashURL = result[0]["url"]
				urlHash["url"] = hashURL
		return slash24Dict

	# #Return set of unique ips matching regex on /24 along with ref urls
	# def getSlash24IPs(self,matchVal):
	# 	ipSet = set()
	# 	hashSet = set()
	# 	urlList = []
	# 	#strips .\d* from given ip string and returns the first three octets
	# 	slash24 = matchVal.rsplit('.', maxsplit=1)[0] + "."
	# 	tmp = self.rxSearch_tbl("tbl_MALIPS", "ip", slash24)
	# 	if tmp:
	# 		for element in tmp:
	# 			currIP = element["ip"]
	# 			#print("for element in tmp\n")
	# 			#print("\tcurrIP: " + currIP + " matchVal: " + matchVal + "\n")
	# 			if matchVal != currIP:
	# 				ipSet.add(currIP)
	# 				ipSet.add(matchVal)
	# 				hashSet.add(element["urlHash"])
	# 		if hashSet:
	# 			for urlHash in hashSet:
	# 				result = self.search_tbl("tbl_ENTRIES", "urlHash", urlHash)
	# 				urlList.append(result[0]["url"])
	# 	return (ipSet, urlList)