#!/bin/bash

# converts pdf2json, generates a human-readable form of that,
# then converts the pdf to an image with the specified resolution

while getopts f:r: opt; do
	case "$opt" in
		f) file=${OPTARG};;
		r) image_res=${OPTARG};;
	esac
done
echo "File: $file"

pdf2json -f $file

json_file="${file::-4}.json"
python3 pretty_printing.py $json_file;
python3 pdf_to_image.py $file $image_res