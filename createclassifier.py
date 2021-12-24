#----------------------------------------------------------------------------------------------------------------
# Author: Dan Bull (Lynker Analytics)
# Date: Dec 2021
# Functionality: Creates classifier from buildings Ground truth and images. 
# Version: py3.7
#----------------------------------------------------------------------------------------------------------------

import arcpy
import os

workspace = r'C:\DeepLearning\Lynker\AfricanCities\Data\Results\MOYALE_UPPER'
arcpy.env.workspace = workspace

xshift = 32840
yshift = 30040
leap=1

x=5
y=5

dir=r'C:\DeepLearning\Lynker\AfricanCities\Data\Sentinel\MOYALE_UPPER'
groundtruth = r'C:\DeepLearning\Lynker\AfricanCities\Data\Results\MOYALE_UPPER\kernaldense.gdb\density'

arcpy.CreateFileGDB_management(workspace, 'shiftedfc.gdb')

def shift_features(in_features, x_shift=None, y_shift=None, num=0): 
    arcpy.CopyFeatures_management(in_features, "shiftedfc.gdb\\shift" + str(num))
    with arcpy.da.UpdateCursor("shiftedfc.gdb\\shift" + str(num), ['SHAPE@XY']) as cursor:
        for row in cursor:
            cursor.updateRow([[row[0][0] + (x_shift or 0),
                               row[0][1] + (y_shift or 0)]])
 
    return

images = os.listdir(dir)
n=0

for ix in range(x):
    for iy in range(y):
        item = images[n]
        print ("working on " + item)
        itemloc = os.path.join(dir,item)
        itemoutloc = os.path.join(workspace,item)
        this_xshift = ix * xshift
        print ("this xshift is " + str(this_xshift))
        this_yshift = iy * yshift
        print ("this yshift is " + str(this_yshift))
        arcpy.Shift_management(itemloc, itemoutloc, str(this_xshift),str(this_yshift))
        shift_features(groundtruth, this_xshift, this_yshift, n)
        n=n+leap

arcpy.CreateFeatureclass_management("shiftedfc.gdb", "allshifts", "POLYGON", "shiftedfc.gdb\\shift0")
fcList = arcpy.ListFeatureClasses(os.path.join(workspace, "shiftedfc.gdb"))
fcList = [os.path.join("shiftedfc.gdb", "shift" + str(l)) for l in range(0,x*y,leap)]
arcpy.Append_management(fcList, os.path.join("shiftedfc.gdb", "allshifts"))

spatial_ref = arcpy.Describe("shiftedfc.gdb\\shift0").spatialReference
arcpy.management.CreateMosaicDataset("shiftedfc.gdb", "shifted_rasters", spatial_ref, 10, "16_BIT_UNSIGNED")
all_rasters = arcpy.ListRasters("*", "JP2")
arcpy.AddRastersToMosaicDataset_management(os.path.join("shiftedfc.gdb","shifted_rasters"), "Raster Dataset", workspace)
classifier = workspace + "\\RF.ecd"
#arcpy.sa.TrainSupportVectorMachineClassifier(os.path.join("shiftedfc.gdb","shifted_rasters"), os.path.join("shiftedfc.gdb", "allshifts"), classifier,"", 1000)
arcpy.sa.TrainRandomTreesClassifier(os.path.join("shiftedfc.gdb","shifted_rasters"), os.path.join("shiftedfc.gdb", "allshifts"), classifier)