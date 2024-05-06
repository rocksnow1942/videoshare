"""
Import sony A7C videos and images

How to use:
1. Inserset SD card to MAC.
2. Run the script.
"""

import itertools
import os
import pathlib
import re
import shutil
from datetime import datetime
from pathlib import Path

PATTERNS = (
    # Osmo pocket 3 videos: DJI_20240504121852_0028_D.MP4
    re.compile(r"DJI_(?P<year>20\d{2})(?P<month>[01]\d)(?P<day>[0123]\d)"),
    # sony A7c videos: 20230716_A0638.MP4
    re.compile(r"(?P<year>20\d{2})(?P<month>[01]\d)(?P<day>[0123]\d)_A"),
)

IMAGE_SUFFIX = ("JPG", "ARW", "jpg", "arw")

VIDEO_SUFFIX = ("MP4", "MOV", "mp4", "mov")


def getImageVides(folder: pathlib.Path) -> tuple[list[pathlib.Path], list[pathlib.Path]]:
    images = list(itertools.chain.from_iterable(folder.rglob(f"*.{s}") for s in IMAGE_SUFFIX))
    videos = list(itertools.chain.from_iterable(folder.rglob(f"*.{s}") for s in VIDEO_SUFFIX))
    print(f"{len(images)} images found in {folder}")
    print(f"{len(videos)} videos found in {folder}")
    return images, videos


def getCreateTimeFromName(f: pathlib.Path) -> tuple[str, str] | None:
    """Get the creation time from file name, return YYYY and MM-DD in tuple"""
    for p in PATTERNS:
        if m := p.search(f.name):
            year = m.group("year")
            month = m.group("month")
            day = m.group("day")
            return year, f"{month}-{day}"
    return None


def getCreateTime(f: pathlib.Path) -> tuple[str, str]:
    """Get the creation time of file, return year and date in tuple"""
    # first try use Datetime string from file name
    if ct := getCreateTimeFromName(f):
        return ct
    date = datetime.fromtimestamp(os.stat(f).st_mtime)
    return date.strftime("%Y"), date.strftime("%m-%d")


def organizeFile(files: list[pathlib.Path], destination: pathlib.Path):
    "move all files in source folder to destination foler, in sub folders with date"
    print(f"Start organizing {len(files)} to {destination} folder")
    newPaths = []
    for f in files:
        year, date = getCreateTime(f)
        newfolder = destination / year / date
        newfolder.mkdir(parents=True, exist_ok=True)
        target = newfolder / f.name
        file_copy = 1
        while target.exists():
            target = newfolder / f"{f.stem}_{file_copy}{f.suffix}"
            file_copy += 1
        shutil.move(f, target)
        newPaths.append(target)
    print(f"Organized {len(files)} to {destination} folder")
    return newPaths
