#!/usr/bin/env python
import configparser
from pathlib import Path
from sonyA7Cimport import getImageVides,organizeFile
from videoshare import compressVideos,uploadVideos


config = configparser.ConfigParser()
config.read(Path(__file__).parent / 'config.ini')
print(config.sections())



if __name__ == "__main__":
    images, videos = getImageVides(config['CAMERA_FOLDER']['Images'],config['CAMERA_FOLDER']['Videos'] )
    newImages = organizeFile(images, config['SAVE_FOLDER']['Images'])
    newVideos = organizeFile(videos, config['SAVE_FOLDER']['Videos'])
    compressed = compressVideos(newVideos)
    uploadVideos(compressed)
    