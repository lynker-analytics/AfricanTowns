
#----------------------------------------------------------------------------------------------------------------
# Author: Dan Bull (Lynker Analytics)
# Date: Dec 2021
# Functionality: iterates through data and creates csv file of all clear images, and copies previews to a location
#next step is to manually review the previews and update the spreadsheet
# Version: py3.6
#----------------------------------------------------------------------------------------------------------------

from config import *
import csv
import shutil


import os
import argparse

dest = '/mnt/m/clients/Peloria/Sentinel_/previewstocheck/'


p = argparse.ArgumentParser()
p.add_argument('-town', type=str)
args = p.parse_args()

town = args.town

townloc = '/home/dan/projects/Africa/SentinelALL/' + town
previewdir = townloc + '/previews/'
SentinelLayers = townloc + '/sentinellayers'
dest_previews = dest + town

os.mkdir(dest_previews)
csvsaveloc = dest_previews
prevtocheck = dest_previews #'/home/dan/projects/Africa/previewstocheck/WAJIR/'

csvf = town + '_dates_to_keep.csv'
f = open(os.path.join(csvsaveloc,csvf), 'w')
column_name = ['town', 'date', 'IsClear']
writer = csv.writer(f)
writer.writerow(column_name)

for dir in os.listdir(SentinelLayers):
    print (dir)
    ddate = dir[3:-2]
    prevname = os.path.join(previewdir, dir + '_preview_crop.jp2')
    data = [ddate, 'YES']
    writer.writerow(data)
    shutil.copy(prevname, prevtocheck)
