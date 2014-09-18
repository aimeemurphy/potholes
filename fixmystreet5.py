import requests
import csv
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq
from HTMLParser import HTMLParser
import time
import re
import sys

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
target = open('hazard_reports1.csv', 'a')
update_csv = csv.writer(target)
#data = ['currentreportID', 'report_url', 'report_title', 'council', 'description']
#update_csv.writerow(data)

#while loop to keep looping until we reach the ID of the last reported hazard
while counter < lastreportID:
	#pad reportid with 0s up to 6 digits for making the URL
	currentreportid= str(counter).zfill(6)
	url = 'https://www.fixmystreet.com/report/%s' % currentreportid
	report_url = url
	report_id = currentreportid

	#Now let's get the title of the report...
	response = requests.get(report_url)

	#.text() prints the text only, without html tags, we know h1 is the title from inspection
	content = pq(response.content)
	print report_id
	#add to report titles csv
	report_title = content('h1').text()
	print report_title
	if report_title != "Page Not Found":
		#searching for tag.class on the page and pulls text only, need to search text to pick out council later
		council = content("small.council_sent_info").text()
		council = council.replace("Sent to ", "")
		print council
		#find where digits start appearing, i.e., the time that we want to cut off
		#finditer should find the first instance, findall would find them all
		x = re.search("\d", council)
		print x
		p = re.compile("\d")
		for m in p.finditer(council):
			a = m.start()
			council = council[:a-1]
		print council

		#getting category, user and date!
		#these are all within the same tag, so we use regular expressions to pick out the bits we want
		category_user_date = content("em").text()
		category = category_user_date.replace("Reported in the ", "")
		q = re.compile("category")
		for m in q.finditer(category):
			a = m.start()
			user = category[a+9:]
			category = category[:a-1]
		print category
		print "user before chopping is %r" % (user)
		q = re.compile("\d\d:\d\d")
		for m in q.finditer(user):
			a = m.start()
			date_of_report = user[a:]
			user = user[:a-4]
		time_of_report = date_of_report[:5]
		date_of_report = date_of_report[7:]
		day_of_report = date_of_report[:3]
		date_of_report = date_of_report[5:]
		q = re.compile(" Sent to")
		for m in q.finditer(date_of_report):
			a = m.start()
			date_of_report = date_of_report[:a]

		#description is easy to identify specifically through the html tags
		description = content("div.problem-header div.moderate-display p").text()

		#now to get the location of the fault. pulling lat long from the link looks to be the best way to do this
		location = content("div.shadow-wrap ul li a.chevron").attr('href')
		print location
		#search the string and return from where it says lat=, then allow any 
		#digits 0-9 or a . and stop returning when something different i.e., & is found
		latitude = re.search("lat=[0-9.]*", location)
		longitude = re.search("lon=[0-9.-]*", location)
		#use an if statement to set lat to 0.0 if a lat wasn't found in the string
		if latitude:
			latitude = latitude.group().replace("lat=", "")
		else:
			latitude = 0.0
		longitude = re.search("lon=[0-9.-]*", location)
		if longitude:
			longitude = longitude.group().replace("lon=", "")
		else:
			longitude = 0.0
		print latitude, longitude
		#sys.exit()
		#work out status
		status = content("div.content div.banner p").text()
		print "\n\n STATUS: %r \n\n" % (status)
		print status


		data = [report_id, report_url, report_title, category, latitude, longitude, time_of_report, day_of_report, date_of_report, user, council, description, status]
		#print data
		update_csv.writerow(data)
		print data

		time.sleep(0.5)
		counter += 1
	else:

		#add time break between reports, 0.5s for now
		time.sleep(0.5)

		#when it's time to move on to the next report
		counter += 1


