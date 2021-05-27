import pandas as pd 

italian_municipalities_coords_url =\
    "https://raw.githubusercontent.com/MatteoHenryChinaski/Comuni-Italiani-2018-Sql-Json-excel/master/italy_geo.json"


if __name__ == "__main__":
    sicilian_municipalities = pd.read_csv('../data/sicily_municipalities.csv')
    italian_municipalities_coords = pd.read_json(italian_municipalities_coords_url)
    sicilian_municipalities.head()
    italian_municipalities_coords.head()
    
    df = pd.merge(sicilian_municipalities, \
        italian_municipalities_coords, \
        on='comune', how='left')

    df = df.rename(columns={'lng': 'lon'})
    df.to_csv('../data/sicily_municipalities_with_coords.csv')