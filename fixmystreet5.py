import requests
import csv
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq
from HTMLParser import HTMLParser
import time
import re
import sys
from dateutil import parser

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
target = open('hazard_reports1.csv', 'a')
update_csv = csv.writer(target)
#need to write header row
a = "report_id report_url report_title report_method category latitude longitude date user council description status"
update_csv.writerow(a.split())


#while loop to keep looping until we reach the ID of the last reported hazard
#currently the code can't handle reports from the last week without a full date and will fail once it reaches these reports
while counter < lastreportID+1:
	#pad reportid with 0s up to 6 digits for making the URL
	currentreportid= str(counter).zfill(6)
	url = 'https://www.fixmystreet.com/report/%s' % currentreportid
	report_url = url
	report_id = currentreportid

	#Get report title
	response = requests.get(report_url)
	content = pq(response.content)
	print report_id
	report_title = content('h1').text()
	print report_title
	report_title = report_title.encode("utf-8")

	#writing a report generates a report id, some are not submitted so the report does not exist
	#if the report exists, go through the code, otherwise loop to the next report id
	if report_title != "Page Not Found":
		#searching for tag.class on the page and pulls text only, need to search text to pick out council later
		council = content("small.council_sent_info").text()
		council = council.replace("Sent to ", "")
		print council
		#find where digits start appearing, i.e., the time that we want to cut off
		#finditer in a loop will find all instances of a digit occuring
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
		method_category_user_date = content("em").text()
		category_user_date = method_category_user_date

		#some reports do not have a category, these are dealt with differently in the else
		q = re.compile("category")
		if q.search(method_category_user_date) is not None:

#IF THERE IS A CATEGORY		
			
			#more recent reports may be submitted via an app so will have method additionally in the title
			#method needs to be removed before the category can be extracted
			q = re.compile("Reported via")
			if q.search(method_category_user_date) is not None:

#IF THERE IS A CATEGORY AND METHOD				
				
				#Method will be sandwiched between "reported via" and "in the"
				method_category_user_date = method_category_user_date.replace("Reported via ", "")
				q = re.compile(" in the ")
				for m in q.finditer(method_category_user_date):
					a = m.start()
					category_user_date = method_category_user_date[a+8:]
					report_method = method_category_user_date[:a]
					user = category_user_date
					print "user...... %r" % user


			else:
		
				#if there is only a category, user and date...
				report_method = 0
				category_user_date = category_user_date.replace("Reported in the ", "")

#WORKING OUT CATEGORY

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

#IF THERE IS A CATEGORY, METHOD/NOMETHOD, ANONYMOUS/USER

			q = re.compile("anonymously")
			if q.search(user) is not None:
				date = user.replace("anonymously at ", "")
				user = "anonymously"
						
			else:
				user = user.replace("by ","")
				date = user
				q = re.compile("\d\d:\d\d")
				for m in q.finditer(user):
					a = m.start()
					date = user[a:]
					user = user[:a-4]

#IF THERE IS NO CATEGORY

		else:
			category = 0

#IF THERE IS NO CATEGORY BUT A METHOD

			q = re.compile("Reported via")
			if q.search(method_category_user_date) is not None:
				method_category_user_date = method_category_user_date.replace("Reported via", "")	
				p = re.compile("anonymously")

#no category, method, anonymous

				if p.search(method_category_user_date) is not None:
					p = re.compile("anonymously")
					for m in p.finditer(method_category_user_date):
						a = m.start()
						report_method = method_category_user_date[1:a-1]
						user = method_category_user_date[a:a+11]
						date = method_category_user_date[a+16:]
						print "report_method: %r \n user: %r" % (report_method, user)
						print date 

#NO CATEGORY, METHOD, USER
				else:

					p = re.compile (" by ")
					for m in p.finditer(method_category_user_date):
						a = m.start()
						report_method = method_category_user_date[:a-2]
						user = method_category_user_date[a+4:]
					q = re.compile("\d\d:\d\d")
					for m in q.finditer(user):
						a = m.start()
						date = user[a:]
						user = user[:a-4]
						user = user.encode("utf-8")
#NO CATEGORY, NO METHOD, USER/NOUSER

			else:
				report_method = 0
				category = 0
				user = method_category_user_date
				q = re.compile("anonymously")
				if q.search(user) is not None:
					p = re.compile("anonymously")
					for m in p.finditer(user):
						a = m.start()
						date = user[a+16:]
						user = "anonymously"
				else:
					p = re.compile("Reported by ")
					for m in p.finditer(user):
						a = m.start()
						q = re.compile("\d\d:\d\d")
						for m in q.finditer(user):
							b = m.start()
							date = user [b:]
							user = user[a+1:b-2]


		#encode("utf-8") is used to deal with special characters such as accents or pound sign
		
		print "method: %r \n category: %r \n user: %r \n date so far: %r" % (report_method, category, user, date)
				
		user = user.encode("utf-8")
		q = re.compile("\d\d\d\d")
		for m in q.finditer(date):
			a = m.start()
			date = date[:a+4]
			#have date!
		#break down date using dateutil
		#won't work on last week of reocrds as they have only a day of the week but these are not essential
		print "date before parsing: %r" % date
		date = parser.parse(date)
		print date

		#description is easy to identify specifically through the html tags
		description = content("div.problem-header div.moderate-display p").text()
		description = description.encode("utf-8")

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
		if status is "":
			status = 0
		print "\n\n STATUS: %r \n\n" % (status)
		print status


		data = [report_id, report_url, report_title, report_method, category, latitude, longitude, date, user, council, description, status]
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


