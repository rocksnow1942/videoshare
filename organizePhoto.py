import os 
import shutil
from datetime import datetime
import argparse

def getModifiedTime(f):
    date = datetime.fromtimestamp(os.stat(f).st_mtime)
    return date.strftime('%Y'),date.strftime('%m-%d')



def organizeFile(source, destination):
    "move all files in source folder to destination foler, in sub folders with date"
    for root, dirs, files in os.walk(source):
        for f in files:            
            year, date = getModifiedTime(os.path.join(root, f))            
            newfolder = os.path.join(destination, year, date)
            if not os.path.exists(newfolder):
                os.makedirs(newfolder)
            target = os.path.join(newfolder, f)
            while os.path.exists(target):
                target = target.split('.')[0] + '_' + '.' + target.split('.')[1]
            shutil.move(os.path.join(root, f), target)
            print(f"{f} moved to {newfolder}")

if __name__ == "__main__":
    source = '/Volumes/store/temp'
    destination = '/Volumes/store/Pictures'
    # take source and dest folder as arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', help='source folder', default=source)
    parser.add_argument('-d', '--destination', help='destination folder', default=destination)
    args = parser.parse_args()
    organizeFile(args.source, args.destination)
