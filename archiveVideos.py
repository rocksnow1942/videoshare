from videoshare import compressVideos
import glob
import ffmpeg
import subprocess
import json
import os
from pathlib import Path

def getInfoJson(file):
    cmd = ["ffprobe", "-show_format", "-show_streams",
         "-loglevel", "quiet", "-print_format", "json", file]
    res = subprocess.check_output(cmd).decode('utf-8')
    return json.loads(res)
    
def getCodec(j):
    return j['streams'][0]['codec_long_name']



def getFiles(folder):
    videos = []
    for root,folder,files in os.walk(folder):
        for f in files:
            if f.lower().endswith('.mp4'):
                videos.append(os.path.join(root,f))
    return videos


if __name__ == '__main__':
    folder = input('Enter folder: \n').strip()
    if folder:        
        files = getFiles(folder)
        print(f'{len(files)} videos found in folder: {folder}')
        videosToCompress = []
        skipStore = 0
        skipNon264 = 0
        for file in files:
            # skip video in "store folder"
            if '/storage/' in file:
                skipStore += 1
                continue            
            codec = getCodec(getInfoJson(file))
            if 'H.264' in codec:
                videosToCompress.append(file)
            else:
                skipNon264 += 1
        print(f'{len(videosToCompress)} files to compress')
        print(f'{skipStore} files skipped because in "storage" folder')
        print(f'{skipNon264} files skipped because not H.264')
        makeStorage = input('Compress videos for storage? (y/n) \n').strip()
        makeIphone = input('Compress videos for iphone? (y/n) \n').strip()
        if makeIphone.lower() == 'y':
            print('Compressing videos for iphone...')
            compressVideos(videosToCompress,mode='iphone')
        if makeStorage.lower() == 'y':
            print('Compressing videos for storage...')
            compressVideos(videosToCompress,mode='storage')        
    else:
        print(f"{folder} is not valid folder, exit.")
            