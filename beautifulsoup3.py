#using beautiful soup to work out the elements from the report pages that i want to scrape

from bs4 import BeautifulSoup
import requests
import csv
from pyquery import PyQuery as pq
from HTMLParser import HTMLParser

url = ("https://www.fixmystreet.com/report/522072")

r = requests.get(url)

webpage = r.text

soup = BeautifulSoup(webpage)

print soup

#string_soup = string(soup)

#print soup

#for p in soup.find_all('p')
#print(p.)


#print soup.prettify()

#print soup

#response = requests.get(url)
#response.content[:40]

#doc = pq(response.content)
#doc ('p')
#doc('p')[1].text