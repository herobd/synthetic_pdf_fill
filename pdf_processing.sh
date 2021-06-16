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

json_file="${file::-4}.json"

if [[ ! -f "${file::-4}.json" ]] # only creates json file if it does't already exist
then
	pdf2json -f $file
else
	echo "${file::-4}.json already exists, no need to do it again!"
fi

if [[ ! -f "${file::-4}PrettyPrinted.json" ]]
then
	python3 pretty_printing.py $json_file
else
	echo "${file::-4}PrettyPrinted.json already exists, no need to do it again!"
fi

python3 pdf_to_image.py $file $image_res