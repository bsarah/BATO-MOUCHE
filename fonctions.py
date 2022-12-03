import geopandas as gpd
import contextily as ctx
import matplotlib.pyplot as plt
import folium
import pandas as pd
import urllib3
from zipfile import ZipFile
import requests
import osmnx as ox
import networkx as nx
import numpy as np
from tqdm.auto import tqdm 

def get_place(place : str) : 
    
    #récupération des données piétons
    place += ", Paris, Ile-de-France, France" 
    g_place = ox.graph_from_place(place, buffer_dist=1000, network_type="walk", retain_all=True, truncate_by_edge=True)
    
    tags = {"amenity":["restaurant", "cafe","bar","ice_cream","fast_food","pub","food_court","biergarten"]}
    # Voir : https://wiki.openstreetmap.org/wiki/FR:%C3%89l%C3%A9ments_cartographiques 
    # ce qui nous interresse est probablement le plus : 
    # https://wiki.openstreetmap.org/wiki/FR:%C3%89l%C3%A9ments_cartographiques#Consommation
    
    gdf_pois = ox.geometries_from_place(place, tags, buffer_dist=1000)
    #certains lieux (comme une ville) ont un polygone associée : 
    # on peut donc récupérer les POI sans indiquer de dist
    
    gdf_pois["center"]=gdf_pois.centroid
    #chaque ligne peut être soit un polygone (par exemple pour le champ de Mars), soit un point comme un restaurant : on calcul le centre pour avoir une référence unique
    
    return gdf_pois
    #On récupère directement un geodataframe
    

def count_amenities(place) :
    
    tab = get_place(place)
    column_amenity = tab['amenity']
    
    amenities = np.array(["restaurant", "cafe","bar","ice_cream","fast_food","pub","food_court","biergarten"])
    amenities = np.append(amenities, "total")
    amenities = amenities.astype('object')
    amenities = np.array([amenities, np.zeros(len(amenities))])

    for i in column_amenity : 
        for j in range(len(amenities[0])) : 
            if i == amenities[0][j] :
                amenities[1][j] += 1

    amenities[1][-1] = np.sum(amenities[1][0 : len(amenities[0]) - 1])
    
    df_amenities = pd.DataFrame(np.transpose(amenities), columns = ['amenity', 'how many'])
    return df_amenities