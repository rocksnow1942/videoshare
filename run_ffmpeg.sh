#!/bin/bash

input=$1

output=$(dirname $input)/storage/$(basename $input)

# make sure the output directory exists
mkdir -p $(dirname $output)

echo "Compressing $input to $output"

ffmpeg -i $input -vcodec libx264 -crf 24 $output
