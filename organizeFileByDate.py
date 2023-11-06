"""Oraganize files by date.

Usage:
    python organizeFileByDate.py 
    -s: /path/to/source/folder
    -d: /path/to/destination/folder 
    -y --by: organize by day or month or year. Default is month
    -t jpg,jpeg,png,mp4,mov,avi,mp3


"""

import argparse
import os
import pathlib
import shutil
from datetime import datetime
from typing import Callable

from PIL import Image


def is_image(f: str) -> bool:
    "check if file is image"
    suffixes = [".jpg", ".jpeg", ".png"]
    s = pathlib.Path(f).suffix
    return s.lower() in suffixes


def get_file_create_time(f: str) -> datetime:
    "get file create time"
    return datetime.fromtimestamp(os.stat(f).st_mtime)


def get_image_create_time(f: str) -> datetime:
    "get image create time"
    # first try use PIL
    try:
        img = Image.open(f)
        exif_data = img._getexif()
        if exif_data:
            if exif_data.get(271, None) == "HUAWEI":
                # Huawei phone image, use file create time
                time_str = exif_data[306]
            else:
                time_str = exif_data[36867]

            date = datetime.strptime(time_str, "%Y:%m:%d %H:%M:%S")
            return date
        else:
            raise ValueError(f"No EXIF content created found")
    except Exception as e:
        # then use image created time
        return get_file_create_time(f)


def get_create_time(f) -> datetime:
    "get create time"
    if is_image(f):
        return get_image_create_time(f)

    return get_file_create_time(f)


def get_file_filter(file_type):
    "return a function to filter file type"
    suffixes = set("." + i.strip().lower() for i in file_type.split(","))

    def wrap(f: str):
        if file_type == "*":
            return True
        else:
            s = pathlib.Path(f).suffix
            return s.lower() in suffixes

    return wrap


def organizeFile(
    source,
    destination: pathlib.Path,
    by: str,
    file_filter: Callable[[str], bool],
):
    "move all files in source folder to destination foler, in sub folders with date"
    for root, dirs, files in os.walk(source):
        for f in files:
            if not file_filter(f):
                continue
            if by == "none":
                subfolder = ""
            else:
                create_time = get_create_time(os.path.join(root, f))
                if by == "day":
                    subfolder = create_time.strftime("%Y/%m-%d")
                elif by == "month":
                    subfolder = create_time.strftime("%Y/%m")
                elif by == "year":
                    subfolder = create_time.strftime("%Y")
                else:
                    raise ValueError(f"by should be day, month or year, but got {by}")

            newfolder = destination / subfolder
            if not newfolder.exists():
                newfolder.mkdir(parents=True, exist_ok=True)
            target = newfolder / f
            dup_count = 0
            while target.exists():
                dup_count += 1
                target = target.parent / f"{target.stem}_{dup_count}{target.suffix}"
            shutil.move(os.path.join(root, f), target)


if __name__ == "__main__":
    source = "/Volumes/store/temp"
    destination = "/Volumes/store/Pictures"
    # take source and dest folder as arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", help="source folder", default=source)
    parser.add_argument("-d", "--destination", help="destination folder", default=destination)
    parser.add_argument(
        "-y",
        "--by",
        help="Organize by day or month or year. Default is month",
        default="month",
        choices=["month", "day", "year", "none"],
    )
    parser.add_argument(
        "-t",
        "--type",
        help="file type to organize. Default is all files",
        default="jpg,jpeg,png,mp4,mov,avi,mp3",
    )
    args = parser.parse_args()
    dest = pathlib.Path(args.destination)
    if not dest.exists():
        dest.mkdir(parents=True, exist_ok=True)
    file_filter = get_file_filter(args.type)
    organizeFile(args.source, dest, args.by, file_filter)
