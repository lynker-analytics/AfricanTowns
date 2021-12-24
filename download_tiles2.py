
#!/usr/bin/env python
#----------------------------------------------------------------------------------------------------------------
# Author: David Knox (Lynker Analytics)
# Date: 10/06/2020
# Functionality: Download Sentinel scene layers by date and area as defined in config.py
# Version: py3.6

##DJB 2/12/2021
##added part to crop out AOI, and delete raw sentinel download
##note - need to set projection in order to correctly reproj AOI coordinates

##To run script run this:
#python sudo download_tiles2.py -coord 42.02801769000007 4.205916441000056 42.10700657000007 4.111972809000065 -town Dans -scenes FB

#----------------------------------------------------------------------------------------------------------------
import rasterio as rio
from rasterio.windows import Window
from pyproj import CRS, Transformer
from pyproj import Proj, transform
import numpy as np
import boto3
from sentinelhub import BBox, get_area_info, CRS
import cv2
import pprint
from config import *
from os.path import isfile,isdir,islink
from os import listdir,mkdir
from subprocess import call, check_output
import os
import argparse
import shutil

base = '/home/dan/projects/Africa/SentinelALL/'
target = '/mnt/m/clients/Peloria/Sentinel_/ALL'

p = argparse.ArgumentParser()
p.add_argument('-coord', nargs="+", type=float)
p.add_argument('-town', type=str)
p.add_argument('-scenes', nargs="+", type=str)
args = p.parse_args()

coord = args.coord
town = args.town
Scenes = args.scenes

print (Scenes)

print ("downloading data for " + town)

townloc = '/home/dan/projects/Africa/SentinelALL/' + town
SentinelLayers = townloc + '/sentinellayers/'
previewdir = townloc + '/previews/'

## create folders to use to store downloads
#os.mkdir(townloc)
#os.mkdir(SentinelLayers)
#os.mkdir(previewdir)

ExtraArgs={'RequestPayer':'requester'}
s3 = boto3.client('s3')
pp = pprint.PrettyPrinter(indent=4)
print (coord)
search_bbox = BBox(bbox=coord, crs=CRS.WGS84)
search_time_interval = (startdate,enddate)



def getimagecoord(n,s,w,e,rasterinput):
	p = Proj(proj='utm',zone=37,ellps='WGS84', preserve_units=False)
	x,y = p(w, n)
	x2,y2 = p(e, s)
	with rio.open(rasterinput) as raster:
		(Xminr,Yminr)=raster.index(x,y )
		(Xmaxr,Ymaxr)=raster.index(x2,y2)
		
	return   Xminr,Yminr, Xmaxr, Ymaxr

def croptoimagecoord(n,s,w,e,rasterinput, output):
	p = Proj(proj='utm',zone=37,ellps='WGS84', preserve_units=False)
	x,y = p(w, n)
	x2,y2 = p(e, s)


	with rio.open(rasterinput) as raster:
		(Xminr,Yminr)=raster.index(x,y )
		(Xmaxr,Ymaxr)=raster.index(x2,y2)
		window = Window(Yminr,Xminr,Ymaxr-Yminr,Xmaxr-Xminr)

		kwargs = raster.meta.copy()
		kwargs.update({
		'height': window.height,
		'width': window.width,
		'transform': rio.windows.transform(window, raster.transform)})
		
		with rio.open(output, 'w', **kwargs) as dst:
			dst.write(raster.read(window=window))

for tile_info in get_area_info(search_bbox, search_time_interval, maxcc=maxcloudcover):
	print ("going")
	URI=tile_info['properties']['s3URI'].replace('-l1c','-l2a')
	if '/V' not in URI:
		#s3://sentinel-s2-l2a/tiles/60/H/VE/2019/8/9/0/
		parts=URI.split('/')
		scene=parts[-6]
		if len(Scenes) > 0 and scene not in Scenes: continue
		dirname=parts[-6]+'_'+parts[-5]+'_'+parts[-4]+'_'+parts[-3]+'_'+parts[-2]
		#print ('aws s3 cp --recursive',URI,'data/l2/'+dirname+' --request-payer' )
		#s3.download_file('BUCKET_NAME', 'OBJECT_NAME', 'FILE_NAME')
		BUCKET_NAME=URI.replace('s3://','').split('/')[0]

		#--------------------------------------------------------------------
		# download the RGB preview
		#--------------------------------------------------------------------
		OBJECT_NAME=URI.replace('s3://'+BUCKET_NAME+'/','')+previewfile
		PREVIEW_FILENAME=previewdir+'/'+dirname+'_preview.jp2'
		print ( 'URI:', URI, 'BUCKET:', BUCKET_NAME, 'OBJECT:', OBJECT_NAME, 'FILENAME:', PREVIEW_FILENAME, flush=True )
		if not isfile(PREVIEW_FILENAME):
			print ( 'URI:', URI, 'BUCKET:', BUCKET_NAME, 'OBJECT:', OBJECT_NAME, 'FILENAME:', PREVIEW_FILENAME, flush=True )
			try:
				s3.download_file(Bucket=BUCKET_NAME, Key=OBJECT_NAME, Filename=PREVIEW_FILENAME, ExtraArgs=ExtraArgs)
				output = PREVIEW_FILENAME[:-4] + "_crop.jp2"
				croptoimagecoord(North,South,West,East,PREVIEW_FILENAME,output)
				os.remove(PREVIEW_FILENAME)
			except Exception as e:
				print ( e )
				print ( 'problem downloading', PREVIEW_FILENAME, 'from', BUCKET_NAME, OBJECT_NAME )

		#--------------------------------------------------------------------
		# download the cloud mask 
		#--------------------------------------------------------------------
		OBJECT_NAME=URI.replace('s3://'+BUCKET_NAME+'/','')+cloudfile
		CLOUD_FILENAME=previewdir+'/'+dirname+'_cloud.jp2'
		if not isfile(CLOUD_FILENAME):
			print ( 'URI:', URI, 'BUCKET:', BUCKET_NAME, 'OBJECT:', OBJECT_NAME, 'FILENAME:', CLOUD_FILENAME, flush=True )
			try:
				s3.download_file(Bucket=BUCKET_NAME, Key=OBJECT_NAME, Filename=CLOUD_FILENAME, ExtraArgs=ExtraArgs)
				output = CLOUD_FILENAME[:-4] + "_crop.jp2"
				croptoimagecoord(North,South,West,East,CLOUD_FILENAME,output)
				os.remove(CLOUD_FILENAME)
			except Exception as e:
				print ( e )
				print ( 'problem downloading', CLOUD_FILENAME, 'from', BUCKET_NAME, OBJECT_NAME )

		#--------------------------------------------------------------------
		# download the scene classification file
		#--------------------------------------------------------------------
		OBJECT_NAME=URI.replace('s3://'+BUCKET_NAME+'/','')+sceneclassfile
		SCENE_FILENAME=previewdir+'/'+dirname+'_sceneclass.jp2'
		if not isfile(SCENE_FILENAME):
			print ( 'URI:', URI, 'BUCKET:', BUCKET_NAME, 'OBJECT:', OBJECT_NAME, 'FILENAME:', SCENE_FILENAME )
			try:
				s3.download_file(Bucket=BUCKET_NAME, Key=OBJECT_NAME, Filename=SCENE_FILENAME, ExtraArgs=ExtraArgs)
				output = SCENE_FILENAME[:-4] + "_crop.jp2"
				croptoimagecoord(North,South,West,East,SCENE_FILENAME,output)
				os.remove(SCENE_FILENAME)
			except Exception as e:
				print ( e )
				print ( 'problem downloading', SCENE_FILENAME, 'from', BUCKET_NAME, OBJECT_NAME )

		#--------------------------------------------------------------------
		# read in the preview and mask to see how much, nodata we have...
		#--------------------------------------------------------------------

		rgb=cv2.imread(PREVIEW_FILENAME[:-4] + "_crop.jp2")
		cloud=cv2.imread(CLOUD_FILENAME[:-4] + "_crop.jp2",0)
		print (cloud)

		print ( 'CLOUD', np.min(cloud), np.mean(cloud), np.max(cloud) )
		nodata_fraction=np.sum(rgb==0)/len(rgb.flatten())
		cloud_fraction=np.sum(cloud>0)/len(cloud.flatten())

		print ( 'NODATA fraction:', nodata_fraction, 'CLOUD fraction:', cloud_fraction, flush=True )

		if maxcleartile < (1- (cloud_fraction + nodata_fraction)):
			print ( 'ok.' )
			"""
			cmd=[]
			#print ('aws s3 cp --recursive',URI,'data/l2/'+dirname+' --request-payer' )
			cmd.append('aws')
			cmd.append('s3')
			cmd.append('cp')
			cmd.append('--recursive')
			cmd.append(URI)
			cmd.append('data/l2/'+dirname)
			cmd.append('--request-payer')
			"""
			outdir=SentinelLayers+dirname+'/'
			if not isdir(outdir): mkdir(outdir)
			for layer in inlayers:
				getfile=inlayers[layer]
				OBJECT_NAME=URI.replace('s3://'+BUCKET_NAME+'/','')+getfile
				CLOUD_FILENAME=outdir+getfile.replace('/','_')
				output = CLOUD_FILENAME[:-4] + "_crop.jp2"
				if not isfile(output) and not islink(output):
					print ( layer, CLOUD_FILENAME, flush=True )
					try:
						s3.download_file(Bucket=BUCKET_NAME, Key=OBJECT_NAME, Filename=CLOUD_FILENAME, ExtraArgs=ExtraArgs)
						croptoimagecoord(North,South,West,East,CLOUD_FILENAME,output)
						os.remove(CLOUD_FILENAME)
					
					except Exception as e:
						print ( e )
						print ( 'problem downloading', CLOUD_FILENAME, 'from', BUCKET_NAME, OBJECT_NAME )
				else:
					print ( layer, CLOUD_FILENAME, '	... already downloaded', flush=True )
shutil.copytree(townloc, target + '/' + town, copy_function = shutil.copy)




