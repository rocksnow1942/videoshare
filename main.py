#!/usr/bin/env python

from pathlib import Path

from config import ExternalVolume, SaveFolder
from sonyA7Cimport import getImageVides, organizeFile
from videoshare import compressVideos, uploadVideos

if __name__ == "__main__":
    images = []
    videos = []
    for folder in ExternalVolume.folders:
        if not folder.exists():
            continue
        img, vid = getImageVides(folder)
        images.extend(img)
        videos.extend(vid)
    newImages = organizeFile(images, SaveFolder.images)
    newVideos = organizeFile(videos, SaveFolder.videos)
    # compressed = compressVideos(newVideos, mode="iphone")

    # uploadVideos(compressed)

    # also compress for storage. ~ 50% the size.
    compressVideos(newVideos, mode="storage")
