#----------------------------------------------------------------------------------------------------------------
# Author: Dan Bull (Lynker Analytics)
# Date: Dec 2021
# Functionality: Creates building density fc from buildings data
# Version: py3.7
#----------------------------------------------------------------------------------------------------------------

import arcpy
from arcpy.sa import *
import os

arcpy.CheckOutExtension("Spatial")

buildings=r'C:\DeepLearning\Lynker\AfricanCities\Data\GoogleBuildings.gdb\Buildings_Dolo'

snapraster = r'C:\DeepLearning\Lynker\AfricanCities\Data\Sentinel\DOLO\adj_HE_2017_1_16_0.jp2'
workspace = r'C:\DeepLearning\Lynker\AfricanCities\Data\Results\DOLO'
barrier = r'C:\DeepLearning\Lynker\AfricanCities\Data\GoogleBuildings.gdb\streets'

## this tile is used as a training tile - date should roughly match the google buildings
#trainingtile = r'C:\DeepLearning\Lynker\AfricanCities\Data\Sentinel\WAJIR\Adj_FB_2021_1_5_0.jp2'

##this is the final classifier 
#classifier = "ecd_" + os.path.basename(trainingtile)[:-4] + ".ecd"

arcpy.env.workspace = workspace
arcpy.env.snapRaster = snapraster
arcpy.env.cellSize = 2.5
arcpy.env.extent = snapraster
arcpy.env.outputCoordinateSystem = snapraster
arcpy.env.overwriteOutput=True
buildings_rast = 'buildings.tif'
arcpy.conversion.PolygonToRaster(buildings, "confidence", buildings_rast, "CELL_CENTER")

arcpy.CreateFileGDB_management(workspace, 'kernaldense.gdb')

building_pts = 'kernaldense.gdb\\building_pts'
arcpy.conversion.RasterToPoint(buildings_rast, building_pts)


kernel_density='kernaldense.tif'
outKDens = KernelDensity(building_pts, "", 2.5, 10, "SQUARE_KILOMETERS","DENSITIES", "GEODESIC")
outKDens.save(kernel_density)

kernel_density_rec='kernaldense_reclass.tif'
reclass = Reclassify(kernel_density, "Value", RemapRange([[0,1000,"1"],[1000,25000, "2"],[25000, 200000, "3"]]))
reclass.save(kernel_density_rec)

kernel_density_poly = 'kernaldense.gdb\\density'
arcpy.RasterToPolygon_conversion(kernel_density_rec, kernel_density_poly, "NO_SIMPLIFY")

arcpy.AddField_management(kernel_density_poly, 'classvalue', "LONG")
arcpy.AddField_management(kernel_density_poly, 'classname', "TEXT")
arcpy.CalculateField_management(kernel_density_poly, 'classvalue', "!gridcode!", "PYTHON3")
arcpy.CalculateField_management(kernel_density_poly, 'classname', "str(!gridcode!)", "PYTHON3")

#arcpy.sa.TrainSupportVectorMachineClassifier(trainingtile, kernel_density_poly, classifier,"", 500)
