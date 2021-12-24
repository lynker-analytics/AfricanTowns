##Symbolises data in arcpro
#run inside project i.e. copy and paste to ArcPro

import arcpy
from arcpy import env

aprx = arcpy.mp.ArcGISProject("CURRENT")


m = aprx.listMaps('Dolo')[0]
sym_layer = m.listLayers()[0] 
for lyr in m.listLayers():  
    if lyr != sym_layer:
        arcpy.ApplySymbologyFromLayer_management(lyr, sym_layer)

