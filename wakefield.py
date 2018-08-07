import re
import urllib2
import csv
import os
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup, SoupStrainer
import datetime
import time
import os
import pprint
import unicodedata

script_path = os.path.dirname(os.path.realpath(__file__))

driver = webdriver.PhantomJS(executable_path="/usr/local/bin/bin/phantomjs", service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'])

case_list = []

parties = []

dates = []

case_nums = []

#this function launches the headless browser and gets us to the first page of results, which we'll scrape using main
def search():

	driver.get('https://www.courts.mo.gov/casenet/cases/nameSearch.do')

	if 'Service Unavailable' in driver.page_source:
		log('Casenet website seems to be down. Receiving "service unavailable"')
		driver.quit()
		gc.collect()
		return False

	time.sleep(2)

	court = Select(driver.find_element_by_id('courtId'))

	court.select_by_visible_text('All Participating Courts')

	case_enter = driver.find_element_by_id('inputVO.lastName')

	case_enter.send_keys('Wakefield & Associates')

	year_enter = driver.find_element_by_id('inputVO.yearFiled')

	year_enter.send_keys('2018')

	driver.find_element_by_id('findButton').click()

	time.sleep(3)

#scrapes table and stores what we need in a list of lists
def main():

	html = driver.page_source

	soup = BeautifulSoup(html, 'html.parser')

	table = soup.findAll('table', {'class':'outerTable'})
	
	for row in table:

		party = row.find_all('td', attrs={'colspan':'2'})

		all_links = soup.findAll('a')

		col = row.find_all('td', attrs={'class':'td1'})

		col2 = row.find_all('td', attrs={'class':'td2'})

		for p in party:
			if 'V' in p.text:
				p = p.string
				p = re.sub("\xa0'\'", '', p).strip()
				p = str(p).encode('utf-8').strip()
				parties.append(p)

		for link in all_links:
			raw_html = str(link)

			if 'goToThisCase' in raw_html:
				start = raw_html.find("('") + 2
				end = raw_html.find("',")
				case = raw_html[start:end].strip()
				case_nums.append(case)

		for a in col:
			if '/2018' in a.text:
				a = a.string
				a = re.sub("\xa0", '', a).strip()
				str(a).encode('utf-8').strip()
				dates.append(a)

		for b in col2:
			if '/2018' in b.text:
				b = b.string
				b = re.sub("\xa0", '', b).strip()
				str(b).encode('utf-8').strip()
				dates.append(b)

	return parties, case_nums, dates

def page_looper(count):

	main()

	print "page %s fully scraped" % count

	count = str(int(count) +1)

	print len(parties), " cases so far"

	for i in range(9):

		link = driver.find_element_by_link_text(str(count))

		link.click()

		time.sleep(2)

		main()

		print "page %s fully scraped" % count

		count = str(int(count) +1)

		print len(parties), " cases so far"

		#print(parties,case_nums,dates)

	try: 
		
		next_page_link = driver.find_element_by_partial_link_text('Next')
		next_page_link.click()
		print "Next 10 pages found"
		time.sleep(10)

		page_looper(count)

		#print "page %s fully scraped" % count

		count = str(int(count) +1)

		print len(parties), " cases so far"

		for i in range(9):

			link = driver.find_element_by_link_text(str(count))

			link.click()

			time.sleep(2)

			main()

			print "page %s fully scraped" % count

			count = str(int(count) +1)

			print len(parties), " cases so far"

			#print(parties,case_nums,dates)

			#page_looper(count)

	except NoSuchElementException:

		print "Next 10 pages not found"

		# main()

		# print "page %s fully scraped" % count

		# count = str(int(count) +1)

		# print len(parties), " cases so far"

		# for i in range(9):

		# 	try:

		# 		link = driver.find_element_by_link_text(str(count))

		# 		link.click()

		# 		time.sleep(2)

		# 		main()

		# 		print "page %s fully scraped" % count

		# 		count = str(int(count) +1)

		# 		print len(parties), " cases so far"

		# 		#print(parties, case_nums, dates)

		# 		#print(parties,case_nums,dates)

		# 	except NoSuchElementException:
		# 		break

def write_file():

	search()

	count = '1'

	page_looper(count)

	case_list.append(parties)
	case_list.append(case_nums)
	case_list.append(dates)

	data = zip(case_list[0], case_list[1], case_list[2])

	with open(script_path + "/cases.csv", "w") as f:
		writer = csv.writer(f)
		for d in data:
			writer.writerow(d)

write_file()
