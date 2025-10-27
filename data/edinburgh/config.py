
# config.py

# Lots of useful data here: https://github.com/sztupy/edinburgh-datasets-geojson
CITY_NAME = "edinburgh"
DATASET_PATH = "data/edinburgh/edinburgh_dataset.csv"

# Approximate Dundee center coords
CENTRE = (55.95199301211517, -3.1968157483016975)

#paths to boundary geojsons - boundaries are prepended with b_

# Data is avail from: https://mapit.mysociety.org/area/2651.html
# Note that the above file contains several ploygons - the one needed is the first one.  Use the header and footer
# from the Dundee data to produce a valid file. (The other polygons are islands in the Forth!!)
b_cityBoundry_path =  "data/edinburgh/edinburgh_boundaries.geojson"

# https://mapit.mysociety.org/area/20728.html
# Use the coords in the above file and the header/footer from Dundee
b_cityCentre_path = "data/edinburgh/cityCentre.geojson"
# ATM we don't have sepcific data for commercial centres - using city centre data as a holding point
b_commercial_centres = "data/edinburgh/cityCentre.geojson"


#  Useful info on postcod areas https://en.wikipedia.org/wiki/EH_postcode_area 
#Paths to Postcode CSV's (Prepended with pc_)
pc_dundeePostcodes = "data/edinburgh/CSVs/edinburgh_district_postcodes.csv"


pc_shopping = "data/edinburgh/CSVs/shopping_district_postcodes.csv"
pc_cityCentre = "data/edinburgh/CSVs/city_centre_postcodes.csv"

#paths to caches:(dont need this atm)
pc_cache = "data/dundee_cached_markers.json"


#map.osm.gz path
# can  use the Dundee file as it covers all of Scotland
map_osm_gz ="data/dundee/routes/map_osm/map.osm.gz"


#bus data
bus_data = "data/dundee/bus_dummy.geojson"


#saved routes
r_shopping ="data/edinburgh/routes/shopping_districts_routes.csv"
r_cityCentre = "data/edinburgh/routes/city_centre_routes.csv"