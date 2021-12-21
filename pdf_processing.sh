#!/bin/bash

# converts pdf2json, generates a human-readable form of that,
# then converts the pdf to an image with the specified resolution
file=""
image_res=150
pretty_print=0
while [[ $1 != "" ]]; do
	case $1 in
	-f | --file )			shift
							file="$1"
							;;
	-r | --resolution )		shift
							image_res="$1"
							;;
	-p | --prettyprint )	pretty_print=1
							;;
	esac
	shift
done


if [[ ! -f $file ]]
then
	echo "${file} does not exist!"
	exit
fi


json_file="${file::-4}.json"
# convert PDF to JSON if the JSON doesn't already exist
if [[ ! -f "${file::-4}.json" ]]
then
	pdf2json -f $file
	echo "creating ${file::-4}.json..."
else
	echo "${file::-4}.json already exists!"
fi


# convert JSON to human readable form if not already done (if flag -p = true)
if [[ $pretty_print == 1 ]]
	then
		if [[ ! -f "${file::-4}PrettyPrinted.json" ]]
			then
			python3 pretty_printing.py $json_file
			echo "creating ${file::-4}PrettyPrinted.json..." echo echo
		else
			echo "${file::-4}PrettyPrinted.json already exists!"
		fi
else
	echo "pretty_print flag was not set"
fi

python3 paragraph_parser.py $file
python3 pdf_to_image.py $file $image_res