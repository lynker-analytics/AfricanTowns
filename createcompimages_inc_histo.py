
#----------------------------------------------------------------------------------------------------------------
# Author: Dan Bull (Lynker Analytics)
# Date: Dec 2021
# Functionality: Turns sentinel bands in to 10 band jp2, and performs a histogram match. Searches for a 'YES' in csv file and only stacks these images
# Version: py3.7
#----------------------------------------------------------------------------------------------------------------

from pilutil import *
import numpy as np
import rasterio
from os import listdir
from os.path import isfile, islink
from config import *
import os
#from sklearn.preprocessing import normalize
import csv
import cv2
from skimage import exposure


##csv file with manually checked images for cloud
Wajir = '/home/dan/projects/Africa/good_vs_bad_AOI/Wajir.csv'

##raw sentinel data
images = '/home/dan/projects/Africa/WAJIR/sentinel_layers/'

##output
rgbi_output = '/home/dan/projects/Africa/WAJIR/'

##this is the reference image which is used to perform the histogram match
refimagedir = '/home/dan/projects/Africa/WAJIR/sentinel_layers/FB_2017_10_3_0'

with open(Wajir, 'r') as csvfile:
	datareader = csv.reader(csvfile)
	for row in datareader:
		if row[2]=='YES':
			imdirname = 'FB_' + row[1] + '_0'
			dir = os.path.join(images, imdirname)
			print ("stacking image " + dir)
			red = os.path.join(dir, 'R10m_B04_crop.jp2')
			raster=rasterio.open(red)
			(h,w)=raster.read(1).shape
			profile=raster.profile
			profile.update(
				count=10
				,dtype=rasterio.uint16
				,driver='GTiff'
			)
			compimgname = os.path.join(rgbi_output, 'adj_' + imdirname + '.jp2')
			compimg=np.zeros((h,w,10),dtype=np.float64)
			
			c=0
			for layer in inlayers:
				filename=inlayers[layer].replace('/','_')[:-4] + '_crop.jp2'
				raster=rasterio.open(os.path.join(dir,filename))
				ref_raster = rasterio.open(os.path.join(refimagedir,filename))
				im=raster.read(1)
				ref_im=ref_raster.read(1)
				
				(hx,wx)=im.shape
				if (hx,wx) != (h,w):
					print (filename)
					print ( 'resizing', flush=True )
					im=cv2.resize(im,dsize=(w,h),interpolation=cv2.INTER_NEAREST)
					ref_im=ref_raster.read(1)
				#do match
				matched = exposure.match_histograms(im, ref_im)
	
			#
			#for band in [red,green,blue,ir]:
				
				#imnorm = normalize(im)
				compimg[:,:,c]+=matched #*hasdata

				c+=1

			with rasterio.open(compimgname, 'w', **profile) as dst:
				for c in range(10):
					dst.write(compimg[:,:,c].astype(rasterio.uint16), c+1)
		else:
			print ("ignoring " + 'FB_' + row[1] + '_0')

