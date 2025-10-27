The raw CCTV data  for dundee was obtained from https://opendata.scot/datasets/

Cleaning of the data was performed on open refine.

Steps to clean data:

## Adding co-ordinates to data.

 
 co-ordinates found using:
https://dundeecity.maps.arcgis.com/home/webmap/viewer.html?webmap=1bdac89f02dd41438a09977f6994c194 to find the location of cameras.

right clicking on the same locations on google maps to get the lat longs (I believe its Decimal Degrees (DD) format).

creating a column "Coordinates" based on the column "Source" to map the values.
using this "Grel" code:

if(value == "Camera 320 Westport", "56.459638660460286, -2.9775237290405436",
if(value == "Camera 328 South Marketgait", "56.458540554802326, -2.9701746146700883",
if(value == "Camera 332 Waterfront", "56.458422918788656, -2.9646535472059705",
if(value == "Camera 317 Reform St", "56.46069036160612, -2.9704202964651807",
if(value == "Camera  308 Murraygate", "56.46263669424284, -2.96873678919877",
if(value == "Camera 500 Hilltown", "56.46562343003358, -2.971909447877699",
if(value == "Camera 310 - Seagate", "56.46341126152989, -2.9664357867981788",
if(value == "Camera 323 Union Street", "56.45873614177991, -2.9704714181456926",
if(value == "Camera 331 Railway Station", "56.457432091476086, -2.9697069057801677",
"")))))))))
    


## Cleaning date column 

remove the redundant time from date column:

value.replace(/\s\d{2}:\d{2}:\d{2}\+\d{2}/, "")
value.replace(/\s\d{1,2}:\d{2}:\d{2}\s[AP]M/, "")

# column name consistency

column names were sometimes different, ensure the format follows this structure:
Day|Date|Hour|Source |Coordinates |	F__of_Bicycles|	F__of_People|F__of_Road_Vehicles|FID

(F__of_People; the F stands for frequency)



