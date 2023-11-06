import argparse
import multiprocessing
import os
import shutil

import pytesseract


def imageHasText(file):
    text = pytesseract.image_to_string(file)
    return len(text) > 0


def main(source, dest):
    """Recursively scan source folder for jpg, jpeg, png files.
    if the image has text, move it to dest folder.
    """
    for root, dirs, files in os.walk(source):
        for f in files:
            file = f.lower()
            if file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith(".png"):
                file_path = os.path.join(root, f)
                if imageHasText(file_path):
                    print(f"Found text in {file_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", help="Source folder to scan")
    parser.add_argument("-d", help="Destination folder to move files to")
    args = parser.parse_args()
    main(args.s, args.d)
