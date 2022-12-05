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


"""
We are building several functions on top of OSMnx library which itself build
to interact with Overpass API (a copy of OMS data without the same API limitations)
"""

##########################################
##### General function ########
##########################################

def get_place_POI_tags(place : str,
    tags = {"amenity":["restaurant", "cafe","bar","ice_cream","fast_food","pub","food_court","biergarten"]},
    city : str = "Paris, Ile-de-France, France", consolidate = True,
    network_type = 'walk') : 
    """
    Function to get any city's (Paris' by default) neighborhood's OMS POI.
    place : str, must be name sufficiently known
    city : str, format : "Name, Region, Country" (Example : Paris, Ile-de-France, France)
    tags : dict, keys and values are the same as in OMS. 
    For instance : https://wiki.openstreetmap.org/wiki/FR:%C3%89l%C3%A9ments_cartographiques#
    consolidate : use the osmnx consolidate_intersections (tolerance = 15) to merge place with too complicated intersections like a roundabout 
    Returns the street network in a 1km walking distance as a networkx object 
    and the POI in the same area as a geodataframe

    Streets network and POI are projected to WGS-84
    """
    #récupération des données piétons
    place += ", "+city # complete addresse

    #get the network
    g_place = ox.graph_from_place(place, buffer_dist=1000, network_type=network_type, retain_all=True, truncate_by_edge=True)
    g_place = ox.project_graph(g_place, to_crs="WGS-84")
    if consolidate:
        g_proj = ox.project_graph(g_place)
        g_place = ox.consolidate_intersections(g_proj, rebuild_graph=True, tolerance=15, dead_ends=False)

    #get the POI
    tags = {"amenity":["restaurant", "cafe","bar","ice_cream","fast_food","pub","food_court","biergarten"]}
    # Voir : https://wiki.openstreetmap.org/wiki/FR:%C3%89l%C3%A9ments_cartographiques 
    # ce qui nous interresse est probablement le plus : 
    # https://wiki.openstreetmap.org/wiki/FR:%C3%89l%C3%A9ments_cartographiques#Consommation
    
    gdf_pois = ox.geometries_from_place(place, tags, buffer_dist=1000)
    #certains lieux (comme une ville) ont un polygone associée : 
    # on peut donc récupérer les POI sans indiquer de dist
    
    gdf_pois["center"]=gdf_pois.centroid
    #chaque ligne peut être soit un polygone (par exemple pour le champ de Mars), soit un point comme un restaurant : on calcul le centre pour avoir une référence unique
    gdf_pois = ox.project_gdf(gdf= gdf_pois, to_crs="WGS-84")
    return g_place, gdf_pois
    #On récupère directement un geodataframe

def plot_POI_folium(place_latlong : np.array,
    gdf_poi: gpd.GeoDataFrame, tiles = "OpenStreetMap", zoom_start = 14) :
    """
    place_latlong : the central place for which to center the map on, tuple (lat, long)
    gdf_poi : GeoPandas.GeoDataFrame with POI
    It is the classical folium method : you create a list with geometry point values (here gdf_poi.center) and for each 
    coordinates, you add a marker. 
    Returns a Folium map
    """
    #on représente en lat, long (et donc y,x)!!!
    # y = lat
    # x = long
    map = folium.Map(location=place_latlong, tiles=tiles, zoom_start=zoom_start)

    for poi in gdf_poi.iterrows():
        # Place the markers with the popup labels and data
        x , y = (poi[1]['center'].x, poi[1]['center'].y)
        map.add_child(
            folium.Marker(
                location=[y,x],
                popup=
                    "Name: " + str(poi[1]['name']) + "<br>" #here to add name 
                    #+ "Leisure: " + str(poi[1]['leisure']) + "<br>" #type 
                    + "Amenity: " + str(poi[1]['amenity']) + "<br>" #type 
                    + "Coordinates: " + str(y)+', '+str(x)
                ,
            
                icon=folium.Icon(color="blue"),
            )
        )
    return map

def route_between_coordinates(streets : nx.classes.MultiDiGraph,
    coord1: tuple, coord2 : tuple, weight = "lenght"):
    """
    Using the street network closest point to each coordinate, 
    calculate the shortest path on the networks
    coord : format (long, lat)
    """
    orig = ox.distance.nearest_nodes(streets,X=coord1[0],Y = coord1[1])
    dest = ox.distance.nearest_nodes(streets,X=coord2[0],Y = coord2[1])
    route = ox.shortest_path(streets, orig, dest, weight=weight) # on peut aussi mettre travel_time

    return route

def distance_route(route, streets : nx.classes.MultiDiGraph):
    n = len(route)-1
    dist_metric = 0
    for i in range(n):
        adj = streets.adj[route[i]]
        dist_metric += adj[route[i+1]][0]['length']
    return dist_metric

def route_between_POI(streets : nx.classes.MultiDiGraph, poi : gpd.GeoDataFrame,
    name1: str, name2 : str, weight = "lenght"):
    """
    Calculate the distance between the POI named name1 and name2
    using their centroid coordinates
    """
    coord1 = get_POI_coordinates(poi = poi, name = name1)
    coord2 = get_POI_coordinates(poi = poi, name= name2)

    return route_between_coordinates(streets= streets, coord1= coord1,
    coord2= coord2, weight= weight)

def get_POI_coordinates(poi: gpd.GeoDataFrame, name : str):
    coord = poi[poi['name']==name]['center']
    return (coord.x[0], coord.y[0])

