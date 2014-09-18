import requests
import csv
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq
from HTMLParser import HTMLParser
import time
import re

#compile url of url start + counter padded with zeros using zfill
print "Enter report ID to start from: \n Note: The first ID is 10, or start from the most recent hazardid already obtained"
counter = int(raw_input())

#get lastreportid by getting the url of the most recent report on main page
#and clipping off last six digits of url as the report id

mainpage_url = ("http://www.fixmystreet.com")
r = requests.get(mainpage_url)
webpage = r.text
soup = BeautifulSoup(webpage)

#this will extract URLs through a loop, add each URL to a list
soup_out = ['Soup output',]
for link in soup.find_all('a'):
   	k=(link.get('href'))
   	soup_out.append(k)

#the most recent url is always first and is an index position 3
#get the report ID from end of URL, make an integer for the loop and print some info...
kid = soup_out[3]
lastreportID = int(kid[-6:])
print "The most recent hazard report ID is ID %r at link %r" % (lastreportID, soup_out[3])  

#open files to print to once, outside of loop
#ee ex16 for making csv 'a' append 'wb' open as empty file and start writing
target = open('hazard_reports1.csv', 'wb')
b = csv.writer(target)
data = ['currentreportID', 'report_url', 'report_title', 'council', 'description']
b.writerow(data)

#while loop to keep looping until we reach the ID of the last reported hazard
while counter < lastreportID:
	#pad reportid with 0s up to 6 digits for making the URL
	currentreportid= str(counter).zfill(6)
	url = 'https://www.fixmystreet.com/report/%s' % currentreportid
	report_url = url

	#Now let's get the title of the report...
	response = requests.get(report_url)

	#.text() prints the text only, without html tags, we know h1 is the title from inspection
	content = pq(response.content)

	#add to report titles csv
	report_title = content('h1').text()
	#searching for tag.class on the page and pulls text only, need to search text to pick out council later
	council = content("small.council_sent_info").text()
	council = council.replace("Sent to ", "")
	print council
	#find where digits start appearing, i.e., the time that we want to cut off
	x = re.search("\d", council)
	print x
	p = re.compile("\d")
	for m in p.finditer(council):
		a = m.start()
		print a
		council = council[:a-1]
	print council

	#getting category, user and date!
	category_user_date = content("em").text()
	print category_user_date
	category = category_user_date.replace("Reported in the ", "")
	q = re.compile("category")
	for m in q.finditer(category):
		a = m.start()
		user = category[a+9:]
		category = category[:a-1]
	print category
	q = re.compile("\d\d:?\d\d")
	for m in q.finditer(user):
		a = m.start()
		date = user[a:]
		user = user[:a-4]
	print user
	print date

	#print "\n\n\n" + "CATEGORY:" + category
	#print "\n\n\n" + user_date + "\n\n\n"
	#print user_date

	#category is within a <p> tag with date and text we don't want. 
	#can use replace to replace the standard text with empty text
	#will probably need to use "regular expressions" to look for where the date starts etc
	#category = content()

	description = content("div.problem-header div.moderate-display p").text()
	print description

	data = [currentreportid, report_url, report_title, council, description]
	#print data
	b.writerow(data)

	#add time break between reports, 0.5s for now
	time.sleep(0.5)

	#when it's time to move on to the next report
	counter += 1


