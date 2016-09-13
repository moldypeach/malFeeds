# malFeeds

This script takes RSS/ATOM feeds specified in a local directory, checks for updates to feeds, and then downloads the associated URLs for parsing.

This is is presently done in a manner very specific to http://www.malware-traffic-analysis.net and http://www.broadanalysis.com. List items within the blog entries of these resources are parsed to acquire researched IPs and their associated information - as provided within the resource. These items are then stored locally in a database and processed to make the data a little more conveniently accessed. Output is stored to feeds/emails/, and eventually sent by email as well (tested email, and it works, but I don't want any email creds in a public github repo).

Being that this script was crafted as an exercise in learning Python, there are likely at least a few inefficiencies (i.e. more elegant methods to accomplish the same goals). It was created and tested on Python 3.4
