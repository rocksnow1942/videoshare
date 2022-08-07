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
        videosToCompress = []
        for file in files:
            print('Scan files: ',file)
            codec = getCodec(getInfoJson(file))
            if 'H.264' in codec:
                videosToCompress.append(file)
        print(f'{len(videosToCompress)} files to compress')
        compressVideos(videosToCompress,mode='store')
    else:
        print(f"{folder} is not valid folder, exit.")
            