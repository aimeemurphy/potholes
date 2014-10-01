import requests
import csv
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq
from HTMLParser import HTMLParser
import time
import re
import sys

#compile url of url start + counter padded with zeros using zfill
print "Enter report ID to start from: \n Note: The first ID ever is 10, we have up to 420320 from World Bank, or start from the most recent hazardid already obtained"
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
update_csv = csv.writer(target)


#while loop to keep looping until we reach the ID of the last reported hazard
while counter < lastreportID+1:
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
		print "a council.... %r" % a
		print council

		#getting category, user and date!
		#these are all within the same tag, so we use regular expressions to pick out the bits we want
		#the category_user_date is not the same for all records, need to work out how to deal with lack of category or inclusion of report method
		#the latest records may begin with the method of reporting, such as "via iOS", we can determine if a report contains this by searching the start of the string to decide how to split it
		method_category_user_date = content("em").text()
		category_user_date = method_category_user_date
		#delcare outside loops
		#add if statement to decide how the line should be dealt with, needs boolean test of regexp
		q = re.compile("Reported via")
		if q.search(method_category_user_date) is not None:
			#Need to break up method and category
			#Method will be sandwiched between "reported via" and "in the"
			method_category_user_date = method_category_user_date.replace("Reported via ", "")
			q = re.compile(" in the ")
			for m in q.finditer(method_category_user_date):
				a = m.start()
				category_user_date = method_category_user_date[a+8:]
				method = method_category_user_date[:a]

		else:
		
		#if it doesn't have a method, there's also a chance it doesn't have a category for older reports
		#it's not necessary to deal with this now as i'm only scraping from jan 2014...

			#if there is only a category, user and date...
			method = 0
			category_user_date = category_user_date.replace("Reported in the ", "")


		q = re.compile("category")
		for m in q.finditer(category_user_date):
			a = m.start()
			user = category_user_date[a+9:]
			category = category_user_date[:a-1]
		#print method
		#print category
		#print user
		date_of_report = user
		print "category a.... %r" % a 

		#now take out user and date
		#need to deal with user differently if it's anonymous, much like method...
		q = re.compile("anonymously")
		if q.search(user) is not None:
			date = user.replace("anonymously at ", "")
			user = "anonymously"
			#have date!			
		else:
			user = user.replace("By ")
			date = user
			q = re.compile("\d\d:\d\d")
			for m in q.finditer(user):
				a = m.start()
				date = user[a:]
				user = user[:a-4]
			#have date!
		#should now be able to break down the dates in the same way
		time_of_report = date[:5]
		check_date = date[:7]
		q = re.compile(",")
		#older records have a comma after time
		if q.search(check_date) is not None:
			date = date[7:]
		else:
			date = date[6:]
		print "date:...%r" % date

		#reports from the last week will have only a weekday without an actual date, we will need to identify these and calculate the date
		#older records are easier to deal with: look for a digit, up until then is day, rest is date
		p = re.compile("\d")
		if p.search(date) is not None:
			p = re.compile("\d")
			p.finditer(date)
			b = m.start()
			day_of_report = date[:b-1]
			print "full date: %r" % date
			date = date[b:]
			print "b..... %r" % b
			print "day: %r" % day_of_report

		#day_of_report = date[:3]
		#date_of_report = date_of_report[5:]
		#print date_of_report
		#print time_of_report
		sys.exit()
		print day_of_report
		print date_of_report
		print time_of_report
		
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


		data = [report_id, report_url, report_title, report_method, category, latitude, longitude, time_of_report, day_of_report, date_of_report, user, council, description, status]
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


