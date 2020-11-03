#Version 7 
#Import section
import osmnx as ox
import json
from shapely.geometry import Point, Polygon, MultiPolygon
import pandas as pd
from pandas import DataFrame as df
import geopandas as gpd
import urllib
import webbrowser
#ox.config(overpass_settings='[out:json][timeout:50]')

#Input section
input_c={}
input_choice =  int(input('1 - place \n2 - bbox \n'))
while input_choice not in [1,2]:
    print('wrong input')
    input_choice = int(input('1 - place \n2 - bbox \n'))
    
input_key = str(input('Input category key:\n- for list of keys input "options"\n- for networks input "network"\n- for complex input, input "complex"\n'))

if input_key=='options':
    webbrowser.open('https://wiki.openstreetmap.org/wiki/Category:Key_descriptions')
    input_key = str(input('Input category key:\n- for list of keys input "options"\n- for networks input "network"\n- for complex input, input "complex"\n'))
    
if input_key == 'complex':
    input_c=str(input('Complex input example:\n{"amenity":["pub","restaurant","hospital"],"tourism":"hotel"}\nFor complex inputs for network categories, use network option for category key input'))
    input_c=json.loads(input_c)      
        
if input_choice == 1:    
    place_name = (str(input('Input place name: \n (for example Winchester USA):\n')))
    place = ox.geocode_to_gdf(place_name)
    #place.plot()
else:
    bbox=[]
    put = input('input coordinates of a bbox in format [left,top,right,bottom]:\n')
    spliter=put.split(',')
    for i in spliter:
        bbox.append(float(i))       
#network section
if input_key=='network':
    ntype = str(input('Input network type:\nfor example "drive"'))
    customf=str(input('Input custom filter parameters\nfor example ["highway"="motorway"] or\n["highway"~"cycleway"]["bicycle"!~"no"]\n'))
    if input_choice==1:
        G = ox.graph_from_place(place_name, network_type=ntype, 
            retain_all=True ,custom_filter=customf)
        ped=ox.graph_to_gdfs(G,nodes=False)
        ped.geometry.to_file("network.geojson", driver='GeoJSON')
        ped.to_csv("network.csv")
    else:
        p1=Point(bbox[0],bbox[3])
        p2=Point(bbox[2],bbox[3])
        p3=Point(bbox[2],bbox[1])
        p4=Point(bbox[0],bbox[1])
        pol=Polygon([p1,p2,p3,p4])
        G = ox.graph_from_polygon(pol, network_type=ntype, 
            retain_all=False ,custom_filter=customf)
        ped=ox.graph_to_gdfs(G,nodes=False)
        ped.geometry.to_file("network.geojson", driver='GeoJSON')
        ped.to_csv("network.csv")
elif input_key!='complex':
    input_value = str (input('Input category value\n'))

#Input choice check
    
    #For bbox_________________________
if input_choice == 2:
    p1=Point(bbox[0],bbox[3])
    p2=Point(bbox[2],bbox[3])
    p3=Point(bbox[2],bbox[1])
    p4=Point(bbox[0],bbox[1])
    pol=Polygon([p1,p2,p3,p4])
        
    if input_key=='complex':
        pois=ox.pois.pois_from_polygon(pol, tags=input_c)
    else:
        pois=ox.pois.pois_from_polygon(pol, tags={input_key:input_value})

    main_gdf=gpd.GeoDataFrame(pois[pois.geometry.type=='Polygon'],
            geometry=pois.geometry[pois.geometry.type=='Polygon'])
    points_gdf=pois[pois.geometry.type=='Point']
    
    buildings = gpd.GeoDataFrame()
    for points in points_gdf.index:
        building = ox.footprints.footprints_from_point((points_gdf.loc[points,'geometry'].y,points_gdf.loc[points,'geometry'].x),dist=12,footprint_type='building')
        buildings=buildings.append(building)
    
    buildings.geometry=buildings.buffer(distance=0.000000001)
    out=gpd.sjoin(buildings,points_gdf,how='left',op='contains')
    out=out[out.osmid.notna()]
    out2 = pd.merge(out, points_gdf, how='outer', on=['osmid'])
    for i in out2.index:
        if out2.loc[i,'geometry_x']==None:
            out2.loc[i,'geometry_x']=out2.loc[i,'geometry_y']
    out2=out2.rename(columns={'geometry_x':'geometry'})
    result=out2.append(main_gdf)
    
    result.to_csv('Main_v2.csv')
    result=result[['osmid','building_left','source_left','geometry','amenity','tourism','building']]
    result.to_file("Main_v2.geojson", driver='GeoJSON')
    #result.geometry.to_file("Main_v2.geojson", driver='GeoJSON')
    
    #pois.geometry.to_file("Pois_v2.geojson", driver='GeoJSON')
    pois.to_csv('Pois_v2.csv')
    pois=pois[['osmid','geometry','amenity','name']]
    pois.to_file("Pois_v2.geojson", driver='GeoJSON')
    
    polygons_all = result[result.geometry.type=='Polygon']
    polygons_all.to_file("all_polygons.geojson", driver='GeoJSON')
    #polygons_all.to_csv('all_polygons.csv')
    
#For place_name_______________
if input_choice == 1:
        
    if input_key=='complex':
        pois=ox.pois.pois_from_place(place_name,tags=input_c)
    else:
        pois=ox.pois.pois_from_place(place_name,tags={input_key:input_value})
    main_gdf=gpd.GeoDataFrame(pois[pois.geometry.type=='Polygon'],
            geometry=pois.geometry[pois.geometry.type=='Polygon'])
    points_gdf=pois[pois.geometry.type=='Point']
    
    buildings = gpd.GeoDataFrame()
    for points in points_gdf.index:
        building = ox.footprints.footprints_from_point((points_gdf.loc[points,'geometry'].y,points_gdf.loc[points,'geometry'].x),dist=12,footprint_type='building')
        buildings=buildings.append(building)
    
    buildings.geometry=buildings.buffer(distance=0.000000001)
    out=gpd.sjoin(buildings,points_gdf,how='left',op='contains')
    out=out[out.osmid.notna()]
    out2 = pd.merge(out, points_gdf, how='outer', on=['osmid'])
    for i in out2.index:
        if out2.loc[i,'geometry_x']==None:
            out2.loc[i,'geometry_x']=out2.loc[i,'geometry_y']
    out2=out2.rename(columns={'geometry_x':'geometry'})
    result=out2.append(main_gdf)
    
    result.to_csv('Main_v2.csv')
    result=result[['osmid','building_left','source_left','geometry','amenity','tourism','building']]
    result.to_file("Main_v2.geojson", driver='GeoJSON')
    #result.geometry.to_file("Main_v2.geojson", driver='GeoJSON')
    
    #pois.geometry.to_file("Pois_v2.geojson", driver='GeoJSON')
    pois.to_csv('Pois_v2.csv')
    pois=pois[['osmid','geometry','amenity','name']]
    pois.to_file("Pois_v2.geojson", driver='GeoJSON')
    
    polygons_all = result[result.geometry.type=='Polygon']
    polygons_all.to_file("all_polygons.geojson", driver='GeoJSON')
    #polygons_all.to_csv('all_polygons.csv')