"""
Import sony A7C videos and images

How to use:
1. Inserset SD card to MAC.
2. Run the script.
"""
import shutil
import os
from datetime import datetime
import glob
from pathlib import Path




def getImageVides(A7PathImage,A7PathVideo):
    images = glob.glob(A7PathImage + '/*.JPG') + glob.glob(A7PathImage + '/*.ARW')
    videos = glob.glob(A7PathVideo + '/*.MP4') + glob.glob(A7PathVideo + '/*.MOV')
    print(f"{len(images)} images found")
    print(f"{len(videos)} videos found")
    return images, videos


def getModifiedTime(f):
    date = datetime.fromtimestamp(os.stat(f).st_mtime)
    return date.strftime('%Y'),date.strftime('%m-%d')
 
def organizeFile(files, destination):
    "move all files in source folder to destination foler, in sub folders with date"
    print(f"Start organizing {len(files)} to {destination} folder")
    newPaths = []
    for f in files:            
        year, date = getModifiedTime(f)
        newfolder = os.path.join(destination, year, date)
        if not os.path.exists(newfolder):
            os.makedirs(newfolder)
        target = os.path.join(newfolder, Path(f).name)
        while os.path.exists(target):
            target = target.split('.')[0] + '_' + '.' + target.split('.')[1]
        shutil.move(f, target)
        newPaths.append(target)
    print(f"Organized {len(files)} to {destination} folder")
    return newPaths
        

def main():    
    images, videos = getImageVides(A7PathImage,A7PathVideo)    
    organizeFile(images, imageFolder)
    organizeFile(videos, videoFolder)
    
if __name__ == "__main__":    
    A7PathImage = '/Volumes/Untitled/DCIM/100MSDCF'
    A7PathVideo = '/Volumes/Untitled/PRIVATE/M4ROOT/CLIP'
    imageFolder = '/Volumes/store/Pictures'
    videoFolder = '/Volumes/store/Videos'
    main()
 