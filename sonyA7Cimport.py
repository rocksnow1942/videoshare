"""
Import sony A7C videos and images

How to use:
1. Inserset SD card to MAC.
2. Run the script.
"""

import itertools
import os
import pathlib
import shutil
from datetime import datetime
from pathlib import Path


def getImageVides(folder: pathlib.Path):
    images = list(itertools.chain.from_iterable(folder.rglob(f"*.{s}") for s in ["JPG", "ARW"]))
    videos = list(itertools.chain.from_iterable(folder.rglob(f"*.{s}") for s in ["MP4", "MOV"]))
    print(f"{len(images)} images found in {folder}")
    print(f"{len(videos)} videos found in {folder}")
    return images, videos


def getModifiedTime(f: pathlib.Path):
    date = datetime.fromtimestamp(os.stat(f).st_mtime)
    return date.strftime("%Y"), date.strftime("%m-%d")


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
            target = target.split(".")[0] + "_" + "." + target.split(".")[1]
        shutil.move(f, target)
        newPaths.append(target)
    print(f"Organized {len(files)} to {destination} folder")
    return newPaths
