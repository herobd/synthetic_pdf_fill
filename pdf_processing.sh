#!/bin/bash

# converts pdf2json, generates a human-readable form of that,
# then converts the pdf to an image with the specified resolution

while getopts f:r: opt; do
	case "$opt" in
		f) file=${OPTARG};;
		r) image_res=${OPTARG};;
	esac
done

if [[ -f $file ]]
then
	echo "checking if ${file} exists..."
	echo "${file} exists!"
else
	echo "this file does not exist!"
	exit
fi

json_file="${file::-4}.json"

# convert PDF to JSON if the JSON doesn't already exist
if [[ ! -f "${file::-4}.json" ]]
then
	pdf2json -f $file
else
	echo "attempting to write to ${file::-4}.json..."
	echo "${file::-4}.json already exists!"
fi

# convert JSON to human readable form if not already done
if [[ ! -f "${file::-4}PrettyPrinted.json" ]]
then
	python3 pretty_printing.py $json_file
else
	echo "attempting to write to ${file::-4}PrettyPrinted.json..."
	echo "${file::-4}PrettyPrinted.json already exists!"
fi


python3 pdf_to_image.py $file $image_res