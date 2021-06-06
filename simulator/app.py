from datetime import datetime
from os import sep
import threading
import time
import random
import math 
import pandas as pd 

province_coords = {
    'Palermo':      '38.1121,13.3366', 
    'Catania':      '37.5013,15.0742', 
    'Messina':      '38.1943,15.5505', 
    'Agrigento':    '37.3219,13.5896', 
    'Enna':         '37.5599,14.2900', 
    'Trapani':      '38.0171,12.5453', 
    'Caltanissetta':'37.4888,14.0458', 
    'Siracusa':     '37.0862,15.2738', 
    'Ragusa':       '36.9293,14.7180'
} 

def generate_path_by_province(province, dir_path='../logs', date_format='%d-%m-%Y'):
    """ Generate a log filename appending the current date to a province name """
    current_date = datetime.now().strftime(date_format)
    return f'{dir_path}/{province}-{current_date}.log'


def get_coords_as_array(coords):
    return [(float(value)) for value in coords.split(',')]


def get_nearest_province(province, set):
    x, y = get_coords_as_array(province_coords.get(province))
    nearest_distance = math.inf
    nearest_province = set[0]
    for prov in set:
        x1, y1 = get_coords_as_array(province_coords.get(prov))
        euclidean_distance = math.sqrt((x-x1)**2 + (y-y1)**2)
        if (euclidean_distance < nearest_distance):
            nearest_distance = euclidean_distance
            nearest_province = prov 
    return nearest_province


cache_df = None 
def generate_random_frequence_by_province(province):
    """
    Dobbiamo far si che data una provincia si generino PI all'interno di 
    un sottoinsieme fisso. Questo serve poiché dobbiamo simulare che in una
    certa provincia prendano bene solo alcune stazioni radio.  
    Idea: possiamo utilizzare una funzione hash 
    """
    global cache_df
    prov_with_freqs = ['Catania', 'Palermo', 'Messina']
    nearest_province = get_nearest_province(province, prov_with_freqs)
    if (cache_df is None):
        print(f'[{province}] fetching csv from github')
        url = f'https://raw.githubusercontent.com/triglie/fmap/main/kafkastream/fmdata/fm-station-map-{nearest_province.lower()}.csv'
        print(url)
        cache_df = pd.read_csv(url, sep=',')
    return cache_df['frequency'][random.randint(0, cache_df.shape[0] - 1)]


def microcontroller(province): 
    logpath = generate_path_by_province(province)
    # questo va cambiato in un while(true)
    # o va utilizzato un determinato criterio di terminazione 
    # for _ in range(15):
    while(True):
        with open(logpath, 'a') as log:
            data  = f'province={province} '
            data += f'coords={province_coords.get(province)} '
            data += f'FM={generate_random_frequence_by_province(province)} '
            #https://www.speedcheck.org/it/wiki/rssi/
            data += f'RSSI={random.randint(-120,0)} \n'            
            log.write(data)
            # time.sleep(random.randint(1,3))
            time.sleep(.5)

if __name__ == "__main__":
    print("Starting threads")
    for province in province_coords:
        if (province != "Catania"):
            threading.Thread(target=microcontroller, args=(province, )).start()
