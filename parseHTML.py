import urllib3
from bs4 import BeautifulSoup
from parseFeeds import ParseFeed

pf = ParseFeeds()

http = urllib3.PoolManager()
req = http.request('GET', url)

soup = BeautifulSoup(req.data, 'html.parser')

for item in soup.find_all('a'):
	print(item.get('href'))
