import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import numpy as np
import geopandas as gpd


page = requests.get("https://www.statista.com/statistics/1219589/youtube-penetration-worldwide-by-country/")
soup = BeautifulSoup(page.content, 'html.parser')
tables = soup.find_all("table")


table = tables[0]
tab_data = [[cell.text for cell in row.find_all(["th","td"])]
                        for row in table.find_all("tr")]
df = pd.DataFrame(tab_data)
print(df)

df = df.iloc[1: , :]
# print(df)

df.columns =['name', 'data_value']

# print(df)
df.reset_index(drop=True, inplace=True)
# print(df)

#Cleaning
df['data_value'] = list(map(lambda x: x[:-1], df['data_value'].values))
df = df[df.name != "Worldwide"]
df.name = df.name.apply(lambda x: 'United Arab Emirates' if 'U.A.E.' in x else x)


df['data_value']=df['data_value'].astype(float).apply(np.floor)
# print(df)


# SECOND WORKING
#read the world_shape_file

world_data=gpd.read_file(r'/home/collins/Documents/APPLICATION/Data/qgis_world_shapefile.shp')
# print(world_data)
world_data=world_data.dropna()
# print(world_data.columns)
world_data=world_data[['NAME','iso_a2','ISO_A3','geometry']]

df.name = df.name.apply(lambda x: 'United States of America' if 'United States' in x else x)

for items in df['name'].tolist():
    world_data_list=world_data['NAME'].tolist()
    if items in world_data_list:
        pass
    else:
        print(items,' is not in the world_data_list')

# print(df.columns)

df = df.rename(columns = {'name': 'NAME','data_value':'Dvalue'}, inplace = False)

df = pd.merge(world_data, df, on='NAME', how='outer')

print(df)

print(df.info())
df=df.fillna(0.0)

print(df.info())

print(type(df))

df.to_file(r"/home/collins/Documents/APPLICATION/Data/geodata.shp")