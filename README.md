# AfricanTowns
Process
Process describing at a high level the download and classification of Sentinel data in to towns/not towns

A separate classifier is created for each AOI using the Google buildings data as ground truth.

Sentinel processing

1. download_tiles script downloads data, and clips this to a square AOI. Note that script selects for clear areas for the AOI. Output is preview tiles (low res), individual bands for each date. Tiles are selected with less than 5% cloud, or blank. Due to issues of Sentinel cloud algorithm in Africa, these could actually be clear when 5% cloud

2. Run script 'istownclear.py'. This creates a csv of all the clear tiles + date, and copies the relevant preview files to a directory for QA

3. QA process: Manually check above previews, and update csv with any 'NO'. 'NO' indicates that there is some cloud.

4. Stack images: Script called createcompimages_inc_histo.py does several things. This iterates through csv file (from above) to stack any clear images into a single jp2 of 10 bands. Any 20m bands are resized to 10m. A histogram_match (scikit-image) is performed to match tiles to a particular tile. Output is 10 band jp2s

Buildings processing

1. Google buildings clipped to AOI. Currently manual, will need to be scripted

2. Run script: create_building_density_data.py . This rasterises buildings, creates a point fro each 2.5m pixel, then performs a kernaldensity operation to get a density model of buildings. The output of the kernel density is turned into a three class raster, which is exported to polygon

The building polygon is used as the ground truth

Classifier

1. createclassifier.py: Script assembles 25 data samples from the various time periods, ideally sampled evenly through time. It does this by spatially moving raster plus building polygon, and creating a mosaic. A random forest classifier is created.

2. classify_rasters.py: iterates through rasters and classifies, and updates a statistics table with areas for each of the 3 classes of density. The raster data is exported to polygon for easier processing, and various filters applied

Packaging

Data is added to ArcGIS Pro, a symbology script applied to give each temporal layer consistent symbology. Each Pro map is shared as a map package
