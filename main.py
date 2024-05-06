#!/usr/bin/env python

import pathlib

from config import ExternalVolume, SaveFolder
from organizeFiles import getImageVides, organizeFile

if __name__ == "__main__":
    images: list[pathlib.Path] = []
    videos: list[pathlib.Path] = []
    for folder in ExternalVolume.folders:
        if not folder.exists():
            continue
        img, vid = getImageVides(folder)
        images.extend(img)
        videos.extend(vid)

    if not images and not videos:
        print("No images or videos found in external volume")
        ans = input("Enter local folder to organize files, or enter to exit:\n")
        if ans:
            images, videos = getImageVides(pathlib.Path(ans))
        else:
            exit(0)

    newImages = organizeFile(images, SaveFolder.images)
    newVideos = organizeFile(videos, SaveFolder.videos)
