##Dan Bull Nov 2021
##gets the x,y extent from a shapefile or fc for towns, and adds to csv file. 

import arcpy
import csv
import os

townextent=r'C:\DeepLearning\Lynker\AfricanCities\Data\AOIs.gdb\townextent'
csvsaveloc = r'C:\DeepLearning\Lynker\AfricanCities\Data'

sentineltiles=r'C:\DeepLearning\Lynker\AfricanCities\Data\Sentinel-2-Shapefile-Index-master\Sentinel-2-Shapefile-Index-master\sentinel_2_index_shapefile.shp'

csvf = os.path.basename(townextent) + ".csv"
f = open(os.path.join(csvsaveloc,csvf), 'w')
column_name = ["name", 'scene','xmin', 'ymin', 'xmax', 'ymax']
writer = csv.writer(f)
writer.writerow(column_name)

def gettiles(shape):
    senttiles = arcpy.SelectLayerByLocation_management(shape, "have_their_center_in",  sentineltiles)
    matchcount = int(arcpy.GetCount_management(senttiles)[0])
    if matchcount >0:
        for row in arcpy.da.SearchCursor(senttiles, ["Shape@","Name"]):
            print (tile)
            ##TO DO this function not completed

for row in arcpy.da.SearchCursor(townextent, ["Shape@","Name"]):
    X=[]
    Y=[]
    Name = row[1]
    print (row[0].pointCount)
    for part in row[0]:
        # Print the part number

        print("Part {}:".format(0))

        # Step through each vertex in the feature
        for pnt in part:
            if pnt:
                # Print x,y coordinates of current point
                print("{}, {}".format(pnt.X, pnt.Y))
                X.append(pnt.X)
                Y.append(pnt.Y)
    Xmax = max(X)
    Xmin = min(X)
    Ymax = max(Y)
    Ymin = min(Y)
    data = [Name, 'HE', Xmin, Ymin, Xmax, Ymax]
    writer.writerow(data)
    continue