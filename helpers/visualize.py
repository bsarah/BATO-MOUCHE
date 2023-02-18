import folium
import pandas as pd
import geopandas as gpd

def folium_grid_cat_plot(gdf, var : str, cmap = 'Set1', 
coordinates =(48.8534100,2.3488000),zoom_start=12.1):
    m = folium.Map(coordinates, zoom_start = zoom_start)
    m = gdf.explore(
        m = m,
        column = var,
        tooltip = var,
        tiles = 'OpenStreetMap',
        popup = True,
        cmap = cmap,
        style_kwds = dict(color = "black", opacity = 0.6,
        fillOpacity = 0.4)
    )

    return m