from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
import requests
import re
import csv

base_url = 'https://radiomap.eu/it/'
provinces = ['palermo', 'messina', 'catania']


def is_part_of_station_name(token):
    """
    If the token contains letters, numbers or parenthesis, 
    then is actually a part of the station name
    """
    return re.match(r"[a-zA-Z\(\)]+", token)


def find_station_names(messy_tag):
    """
    Uses a regular expression to find a string between a /> closing 
    tag and a < opening tag. This is where the station names are 
    stored in the scraped HTML. 
    """
    regex = r"\/>(\s|\n|\t|[a-zA-Z0-9\(\)])*<"
    matches = re.finditer(regex, messy_tag, re.MULTILINE)
    station_names = []
    for match in matches:
        # iterate trough tokens and find station
        # name parts 
        tokens = re.split('\s', match.group(0))        
        station_name_tokens = []
        for token in tokens:
            if(is_part_of_station_name(token)):
                station_name_tokens.append(token)
        # check if we got any station name parts  
        if (len(station_name_tokens) > 0):
            station_names.append(' '.join(station_name_tokens))
    return station_names


def is_tag(el):
    return isinstance(el, Tag)


if __name__ == '__main__': 
    
    for province in provinces:

        page = requests.get(f'{base_url}/{province}')
        soup = BeautifulSoup(page.content, 'html.parser')
        rows = soup.select('[class^=\'rt\']')

        stations = []
        for row in rows:
            children = row.children 
            children = list(filter(is_tag, children))
            frequency = children[0].string 
            if (frequency is None):
                continue
            frequency = float(frequency.strip())
            messy_tags = str(children[1])
            # there could be more than one names under the same freq. 
            station_names = find_station_names(messy_tags)
            for station_name in station_names:
                stations.append({'name': station_name, 'frequency': frequency})
        
        csv_file = f'../kafkastream/fmdata/fm-station-map-{province}.csv'
        try:
            with open(csv_file, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=['name', 'frequency'])
                writer.writeheader()
                for data in stations:
                    writer.writerow(data)
        except IOError:
            print("I/O error")
