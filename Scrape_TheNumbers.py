# Data up-to-date as of April 25, 2018

#!/usr/bin/env python
import pandas as pd
from bs4 import BeautifulSoup
import urllib2
from re import sub
from decimal import Decimal

the_numbers_data = pd.DataFrame(columns=['date','name', 'budget', 'domestic', 'worldwide'])

for j in range (0, 56):
    page_num = j*100 + 1
    url = 'https://www.the-numbers.com/movie/budgets/all/' + str(page_num)
    page = urllib2.urlopen(url).read()
    soup = BeautifulSoup(page, "lxml")
    
    raw_data = []
    tds = soup.find('table').find_all('td')
    for i in range (0, 100):
        temp = []
        temp.append(str(tds[6*i+1].contents[0].contents[0]))
        temp.append(tds[6*i+2].contents[0].contents[0].contents[0].encode('utf-8'))
        temp.append(int(Decimal(sub(r'[^\d.]', '', tds[6*i+3].contents[0]))))
        temp.append(int(Decimal(sub(r'[^\d.]', '', tds[6*i+4].contents[0]))))
        temp.append(int(Decimal(sub(r'[^\d.]', '', tds[6*i+5].contents[0]))))
        raw_data.append(temp)
        if j == 55 and i == 18:
            break
    
    this_page_df = pd.DataFrame(raw_data, columns=['date','name', 'budget', 'domestic', 'worldwide'])
    the_numbers_data = the_numbers_data.append(this_page_df, ignore_index=True)

the_numbers_data.to_csv(path_or_buf='data/the_numbers_data.csv', mode='w+')