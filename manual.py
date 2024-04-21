#!/usr/bin/env python
import configparser
from pathlib import Path
from sonyA7Cimport import getImageVides,organizeFile
from videoshare import compressVideos,uploadVideos
import glob
import os
from datetime import datetime
from dateutil import parser

config = configparser.ConfigParser()
config.read(Path(__file__).parent / 'config.ini')

videoPath = config['SAVE_FOLDER']['Videos']

def getVideos(startDate,endDate,path,suffix='.MP4',fileDepth=6):
    startDate = parser.parse(startDate)
    endDate = parser.parse(endDate)    
    newPaths = []
    for root,_,file in os.walk(path):
        for f in file:
            if not f.lower().endswith(suffix.lower()):
                continue
            
            filePath = os.path.join(root,f)
            if fileDepth != len(Path(filePath).parts) - 1:
                continue
            date = datetime.fromtimestamp(os.stat(filePath).st_mtime)
            if startDate <= date <= endDate:
                newPaths.append(filePath)    
    print('\n'.join(newPaths))
    return newPaths


if __name__ == "__main__":
    # newVideos=glob.glob('/Volumes/store/Videos/2021/12-30/*.MP4')
    # print(newVideos)
    # compressed = compressVideos(newVideos,mode='iphone')    
    toCompress = getVideos('2021-12-21','2021-12-25',videoPath)
    compressVideos(toCompress,mode='iphone')
    