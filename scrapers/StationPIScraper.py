from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
import requests
import re
import csv

base_url = 'https://www.teleradioe.eu/radio-data-system-rds-cose-ps-pi-rt/'


if __name__ == '__main__': 

    page = requests.get(base_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    rows = soup.findAll('tr')
    stations = []

    for tr in rows:
        tds = tr.findAll('td')
        freq = tds[0].get_text()
        name = tds[1].get_text()
        rspi = tds[3].get_text()
        for f in freq.split('-'):
            stations.append({'name': name, 'frequency': f.replace(',', '.'), 'pi': rspi}) 

    csv_file = '../kafkastream/fmdata/complete-pi-station-map.csv'
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['name', 'frequency', 'pi'])
            writer.writeheader()
            for data in stations:
                writer.writerow(data)
    except IOError:
        print("I/O error")
