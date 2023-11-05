import argparse
import io
import os
import shutil
from datetime import datetime

import exifread
import pyheif


def set_modified_time(file: str, t: datetime):
    """Set the modified time of the given file to the given time."""
    os.utime(file, (t.timestamp(), t.timestamp()))


def parse_heic_time(s: str) -> datetime:
    try:
        return datetime.strptime(s, "%Y:%m:%d %H:%M:%S")
    except ValueError:
        return datetime.strptime(s, "%Y:%m:%d %H:%M:%S%p")


def get_heic_create_time(file):
    "get the heic file content create time"
    heif_file = pyheif.read(file)
    for meta in heif_file.metadata or []:
        file_stream = io.BytesIO(meta["data"][6:])
        tags = exifread.process_file(file_stream, details=False)
        if tags.get("EXIF DateTimeOriginal", None):
            return parse_heic_time(str(tags["EXIF DateTimeOriginal"]))
        elif tags.get("Image DateTime", None):
            return parse_heic_time(str(tags["Image DateTime"]))

    raise ValueError(f"No EXIF DateTimeOriginal found")


def organize_heic_file(source, dest):
    file_count = 0
    for root, dirs, files in os.walk(source):
        for f in files:
            file_count += 1
            if file_count % 1000 == 0:
                print(f"Processed {file_count} files")
            if f.endswith(".HEIC") or f.endswith(".heic"):
                file_path = os.path.join(root, f)
                try:
                    date = get_heic_create_time(file_path)
                    set_modified_time(file_path, date)
                    year = date.strftime("%Y")
                    month = date.strftime("%m")
                    newfolder = os.path.join(dest, year, month)
                    if not os.path.exists(newfolder):
                        os.makedirs(newfolder)
                    target = os.path.join(newfolder, f)

                    count = 0
                    while os.path.exists(target):
                        count += 1
                        target = (
                            target.rsplit(".", 1)[0]
                            + f"_{count}"
                            + "."
                            + target.rsplit(".", 1)[1]
                        )
                    shutil.move(os.path.join(root, f), target)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", help="source folder")
    parser.add_argument("-d", "--destination", help="destination folder")
    args = parser.parse_args()
    organize_heic_file(args.source, args.destination)
