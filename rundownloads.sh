#!/bin/sh
PATH+=:/home/dan/anaconda3/envs/sentinel2/bin/python
/home/dan/anaconda3/envs/sentinel2/bin/python /home/dan/projects/Africa/code/download_tiles2.py -coord 42.02801769000007 4.205916441000056 42.10700657000007 4.111972809000065 -town Dans -scenes FB
/home/dan/anaconda3/envs/sentinel2/bin/python /home/dan/projects/Africa/code/istownclear.py