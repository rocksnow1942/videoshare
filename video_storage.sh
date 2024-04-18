#!/bin/bash

# compress.sh
# Compress all MP4 files in a directory using ffmpeg
# The script uses parallel to compress multiple files in parallel
# The number of parallel processes is equal to the number of CPU cores
# The script only looks for files with the .MP4 or .mp4 extension
# under directory that don't contain the word "storage"
# the compressed files are saved in the same directory under the
# 'storage' subdirectory

tmp_file="/tmp/files_to_compress.txt"
cpu_count=$(sysctl -n hw.ncpu)
script="$(dirname $0)/run_ffmpeg.sh"

# prompt user for input directory
echo "Enter the directory to search for files to compress:"
read input_dir

find $input_dir -type f -regex "*.(MP4|mp4|MOV|mov)$" -not -regex '.*storage.*' >${tmp_file}

# print the number of files to compress
file_count=$(wc -l ${tmp_file} | awk '{print $1}')
echo "Found ${file_count} files to compress"

# compress files in parallel
parallel -j ${cpu_count} ${script} {} <${tmp_file}

# delete the temporary file
rm $tmp_file
