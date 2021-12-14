#!/usr/bin/env python
import configparser
from pathlib import Path
from sonyA7Cimport import getImageVides,organizeFile
from videoshare import compressVideos,uploadVideos
import glob


config = configparser.ConfigParser()
config.read(Path(__file__).parent / 'config.ini')
print(config.sections())



if __name__ == "__main__":
    newVideos=glob.glob('/Volumes/store/Videos/2021/12-12/*.MP4')
    print(newVideos)
    compressed = compressVideos(newVideos)
    compressed = glob.glob('/Volumes/store/Videos/2021/12-12/compressed/*.MP4')
    print(compressed)
    uploadVideos(compressed)
    