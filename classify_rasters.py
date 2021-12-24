#----------------------------------------------------------------------------------------------------------------
# Author: Dan Bull (Lynker Analytics)
# Date: Dec 2021
# Functionality: iterates through dir and performs classification
# Version: py3.7
#----------------------------------------------------------------------------------------------------------------

import arcpy
from arcpy.sa import *
import os

workspace = r'C:\DeepLearning\Lynker\AfricanCities\Data\Results\DOLO'
#workspace2 = r'C:\DeepLearning\Lynker\AfricanCities\Data\Results\MOYALE'
arcpy.env.workspace = workspace
inputs = r'C:\DeepLearning\Lynker\AfricanCities\Data\Sentinel\DOLO'

classifier = workspace + "\\RF.ecd"
arcpy.CreateFileGDB_management(workspace, 'output.gdb')
arcpy.CreateTable_management('output.gdb', "DOLO_all_stats")
allstats = "output.gdb\\DOLO_all_stats"
arcpy.AddField_management(allstats, 'sum_shape_area', "double")
arcpy.AddField_management(allstats, 'image_date', "text")
for r in range(3):
    arcpy.AddField_management(allstats, 'gridcode' + str(r), "double")

def convertdate(ddate):
    ddate = ddate[:-4].replace('_', '-')
    dashlist = [pos for pos, char in enumerate(ddate) if char == '-']
    print (dashlist)
    year = ddate[7:11]
    if dashlist[3] == 13:
        month = '0' + ddate[12:13]
    else: 
        month = ddate[12:14]
    if dashlist[3] == 13 and dashlist[4] == 15:
        day = '0' + ddate[14:15]
    elif dashlist[3] == 14 and dashlist[4] == 16:
        day = '0' + ddate[15:16]
    elif dashlist[3] == 13 and dashlist[4] == 16:
        day = ddate[14:16]
    else:
        day = ddate[15:17]

    newddate = year + '_' + month + '_' + day
    return newddate
for input in os.listdir(inputs):
    if input[-3:] == "jp2":
        print (input)
        p = convertdate(input)
        print (p)

        print ("classifying raster " + input)
        classifiedraster = ClassifyRaster(os.path.join(inputs,input), classifier)
        classified_rast =  "classify_out_" + os.path.basename(input)[:-4] + ".tif"
        classifiedraster.save(classified_rast)

        print ("execute majority filter")
        # Execute MajorityFilter
        outMajFilt = MajorityFilter(classified_rast, "EIGHT")

        # Save the output 
        print ("saving output")
        output =  workspace + '\\out_' + os.path.basename(input)[:-4] + ".tif"
        outMajFilt.save(output)
        output_fc = 'output.gdb\\out_' + os.path.basename(input)[:-4]
        arcpy.RasterToPolygon_conversion(output, output_fc, "NO_SIMPLIFY", "VALUE")
        output_fc_elim = 'output.gdb\\outelim_' + os.path.basename(input)[:-4]
        arcpy.EliminatePolygonPart_management(output_fc, output_fc_elim, "AREA", 100)
        stats = 'output.gdb\\stats_' + os.path.basename(input)[:-4]
        arcpy.Statistics_analysis(output_fc_elim, stats, [["Shape_Area", "SUM"]], "gridcode")
        arcpy.AddField_management(stats, "image_date", "TEXT")
        ddate = convertdate(input)
        arcpy.CalculateField_management(stats, "image_date",ddate)
        stats_pivot = 'output.gdb\\stats_pivot' + os.path.basename(input)[:-4]
        arcpy.PivotTable_management(stats, "image_date", "gridcode",  "SUM_Shape_Area", stats_pivot)
        arcpy.Append_management(stats_pivot, allstats, "NO_TEST")