import json
import sys

if __name__ == "__main__":
	for i, arg in enumerate(sys.argv):
		if i == 1:
			fileName = arg
			print("\nfile name is " + fileName)

with open(fileName) as read_file:
	print("Reading " + fileName + " in...")
	progress = json.load(read_file)
	size = len(fileName)

	newFileName = fileName[:size - 5] + "PrettyPrinted.json" 
	prettyPrintedJSon = open(newFileName, "w")
	print("Writing to " + newFileName + "...")
	prettyPrintedJSon.write(json.dumps(progress, indent=4, separators=(',', ': '), sort_keys=True))
	prettyPrintedJSon.close()