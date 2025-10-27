# config.py

#----------------------------------------------------------------------------------
#SETUP

CITY_NAME = "dundee"
#DATASET_PATH = "data/dundee/dundee_dataset.csv"

# Approximate Dundee center coords
CENTRE = (56.476401691737124, -2.9620267318538933) 

#----path shortcuts
data_folder = "data/dundee"
#----------------------------------------------------------------------------------------
#paths to BOUNDARIES geojsons - boundaries are prepended with b_ (boundaries/)

b_cityBoundry_path =  f"{data_folder}/boundaries/dundee_boundaries.geojson"
b_cityCentre_path = f"{data_folder}/boundaries/cityCentre.geojson"
b_commercial_centres = f"{data_folder}/boundaries/commercial_centres.geojson"

#----------------------------------------------------------------------------------------
#Paths to POSTCODES CSV's (Prepended with pc_)(lives in CSVs/postcodes/) 

pc_cityPostcodes = f"{data_folder}/CSVs/postcodes/dundee_district_postcodes.csv"
pc_shopping = f"{data_folder}/CSVs/postcodes/shopping_district_postcodes.csv"
pc_cityCentre = f"{data_folder}/CSVs/postcodes/city_centre_postcodes.csv"

#paths to caches:(dont need this atm)
pc_cache = f"{data_folder}/CSVs/postcodes/dundee_cached_markers.json"

#----------------------------------------------------------------------------------------
#folder to save ROUTES CSV's (prepended with r_)(lives in routes/)
route_data_folder = f"{data_folder}/routes"
#----------------------------------------------------------------------------------------
#map.osm.gz routes/map_osm/

map_osm_gz = f"{route_data_folder}/map_osm/map.osm.gz"

#----------------------------------------------------------------------------------------
#saved ROUTES routes/


r_shopping = f"{route_data_folder}/shopping_districts_routes.csv"
r_cityCentre = f"{route_data_folder}/city_centre_routes.csv"

#----------------------------------------------------------------------------------------
#BUSDATA

bus_data = f"{data_folder}/bus_dummy.geojson"

#----------------------------------------------------------------------------------------


#CCTV DATA

cctv_data = f"{data_folder}/CSVs/CCTV/cleaned_Counts_March25.csv" ## direct path to test data
cctv_datasets = f"{data_folder}/CSVs/CCTV/" # path to cctv dataset folder.

cctv_vehicle_classification = f"{data_folder}/CSVs/CCTV/Vehicle_Classification_Counts"

#----------------------------------------------------------------------------------------
# business data
business_data_path = f"{data_folder}/CSVs/pois.csv"

# list of all file paths  with postcodes
selected_data_paths = [
    pc_cityPostcodes,
    business_data_path,
]

#list of boundary paths
boundary_paths = [
    b_cityBoundry_path, 
    b_cityCentre_path,
    b_commercial_centres
]

