"""
for i in *.NEF; do sips -s format jpeg $i --out "${i%.*}.jpg"; done

# resize jpg, almost no lost in quality
for i in *.JPG; do sips -s format jpeg $i --out "${i%.*}.JPG"; done
"""
import subprocess
import os
from pathlib import Path
import shutil
from sys import prefix
import tqdm

TEMP_RAW_FOLDER = '_rawfiles'

def getRawFiles(folder, suffixes=['.NEF','.DNG']):
    "get raw image files from folder"
    output = []
    for root,_,files in os.walk(folder):
        if TEMP_RAW_FOLDER in root:
            # skip the _rawfiles folder generated by this script
            continue
        for f in files:
            for suffix in suffixes:
                if f.upper().endswith(suffix):                    
                    output.append(os.path.join(root,f))
                    break
    return output

def convertJpg(files):
    """
    use sips (scriptable image process system) to convert raw files to jpg
    then move the raw file to the same folder under /rawfiles folder.
    """
    print("Start converting raw files to jpg")
    rawFolders = []
    for file in tqdm.tqdm(files, total=len(files),unit='files'):
        fp = Path(file)
        cmd = ['sips','-s','format','jpeg',file, '--out', fp.parent / (fp.stem + '.jpg')]
        subprocess.check_call(cmd,stdout=subprocess.DEVNULL)
        tomove = fp.parent / TEMP_RAW_FOLDER
        if not tomove.exists():            
            tomove.mkdir()            
            rawFolders.append(tomove)
        shutil.move(file, tomove / fp.name)

    print("Converted {} raw files to jpg".format(len(files)))
    for r in rawFolders:
        print(r)



def main(folder):
    "main function"
    files = getRawFiles(folder)
    print('{} raw files found'.format(len(files)))
    convertJpg(files)


if __name__ == '__main__':
    folder = input('Enter folder: \n').strip()
    if folder:        
        main(folder)
    else:
        print(f"{folder} is not valid folder, exit.")




