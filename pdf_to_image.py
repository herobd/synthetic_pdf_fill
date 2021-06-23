import os
from synthetic_text_gen.synthetic_text_gen import synthetic_text
import sys
import json
import re
import os.path

import img_f

import pdfplumber
import numpy as np


def read_args():
	if __name__ == "__main__":
		imageRes = 0 # if no command line argument passed, resolution is 0
		for i, arg in enumerate(sys.argv):
			if i == 1:
				fileName = arg # commandline argument specifies PDF to convert to PNG
				print("\nfile name is " + fileName)
			if i == 2:
				imageRes = int(arg)
				print("imageRes is " + str(imageRes))

	return (fileName, imageRes)


def create_image(fileName, imageRes, resolutionSpecified):
	with pdfplumber.open(fileName) as pdf:
		pageCount = 0
		size = len(fileName)
		dirName = fileName[:size - 4] # removes .pdf file extension

		if not os.path.exists(dirName):
			os.mkdir(dirName) # if directory doesn't exist, create one to store new images

		if not resolutionSpecified:
			imageRes = 72
			# if a resolution was not specified and the PDF has not been processed before,
			# assign a default value to the resolution

		# check if the images have already been generated by checking log
		logName = dirName + "/info.txt"
		alreadyGenerated = True
		if not os.path.exists(logName): # has not been created before
			print("creating info.txt...")
			f = open(logName, "w")
			f.write(str(imageRes))
			f.close()
			alreadyGenerated = False

		f = open(logName, "r")
		lastRes = int(f.readline())
		f.close()
		if not alreadyGenerated or (imageRes != lastRes and resolutionSpecified):
			f = open(logName, "w")
			generateNew = True
			f.write(str(imageRes))
			f.close()
			print("printing with resolution of " + str(imageRes))
		else:
			generateNew = False
			print("no file updates necessary! Images with resolution of " 
				+ str(lastRes) + " should already exist!")

		#### perhaps create overwrite option that allows to draw again with the same resolution
		#### in case something were to be deleted but the same resolution is wanted?

		for page in pdf.pages:
			if generateNew:
				print("converting page number " + str(pageCount) + " to .png...")
				im = page.to_image(resolution=imageRes)
				# places page images in the newly created directory
				im.save(dirName + "/page" + str(pageCount) + ".png", format="PNG")
			pageCount += 1
	return pageCount


# to remove lines for text containing only '_' or ' '
def string_match(string, search=re.compile(r'[^_ ]').search):
	return not bool(search(string))


def process_data(fileName, pageCount):
	print("\nloading json file...")
	with open(fileName[:len(fileName)-4] + ".json", "r") as f:
		pdfInfo = json.load(f)
	
	list = []
	i = 0
	pageWidth = pdfInfo['formImage']['Width']
	pageHeights = []
	while i < pageCount:
		pageHeight = pdfInfo['formImage']['Pages'][i]['Height']
		pageHeights.append(pageHeight)

		for text in pdfInfo['formImage']['Pages'][i]['Texts']:
			for textInfo in text['R']:
				h = textInfo['TS'][1] # obtains height of text
				info = textInfo['T']
			
			# replace the most common HTML encodings to make the text more legible
			info = info.replace("%20", " ")
			info = info.replace("%3A", ":")
			info = info.replace("%2C", ",")
			info = info.replace("%2F", "/")
			include = string_match(info)

			# does the text contain only dashes and/or spaces? if so, don't add
			if not include:
				tuple = (i, "text", text['x'], text['y'], text['w'], h, info)
				list.append(tuple) # what is height here?

		for field in pdfInfo['formImage']['Pages'][i]['Fields']:
			tuple = (i, "field", field['x'], field['y'], field['w'], field['h'])
			list.append(tuple)

		for boxset in pdfInfo['formImage']['Pages'][i]['Boxsets']:
			for box in boxset['boxes']:
				tuple = (i, "box", box['x'], box['y'], box['w'], box['h'])
				list.append(tuple)

		i += 1
	
	return list, pageWidth, pageHeights


def print_list(list):
	counter = 0
	for dim in list:
		if dim[1] != "text":
			print(str(counter) + ".) page" + str(dim[0]) + ":" + dim[1] + ": x=" + str(dim[2]) + ", y=" +
		  		str(dim[3]) + ", w=" + str(dim[4]) + ", h=" + str(dim[5]))
		else:
			print(str(counter) + ".) page" + str(dim[0]) + ", text says: " + dim[6])

		counter += 1


def draw_bounding_boxes(list, pageWidth, pageHeights):
	i = 0
	dataIndex = 0
	while i < pageCount:
		imageName = (fileName[:len(fileName)-4] + "/page" + str(i) + ".png")
		img = img_f.imread(imageName,color=True)
		imageHeight = img.shape[0]
		imageWidth = img.shape[1]

		# print(str(imageHeight) + "," + str(imageWidth))

		heightMultiplier = imageHeight / pageHeights[i]
		widthMultiplier = imageWidth / pageWidth

		currPage = i
		while currPage == i and dataIndex < len(list):
			currPage = list[dataIndex][0]
			if currPage == i: # draw
				x = list[dataIndex][2] * widthMultiplier
				y = list[dataIndex][3] * heightMultiplier
				w = list[dataIndex][4] * widthMultiplier

				if(list[dataIndex][1] == "text"):
					img_f.line(img,(int(x),int(y)),(int(x)+int(w),int(y)),color=(0,200,40),thickness=3)
				else:
					h = list[dataIndex][5] * heightMultiplier 

					if(list[dataIndex][1] == "field"):
						textImage = create_text(w, h)
						textImage = np.stack((textImage,textImage,textImage),axis=2)
						# print("adding an image to page " + str(i) + " w/ shape " + str(textImage.shape))
						# print("y=" + str(int(x)+textImage.shape[0]) + ",=" + str(int(y)+textImage.shape[1]))
						img[int(y):int(y)+textImage.shape[0], int(x):int(x)+textImage.shape[1]] = textImage

					leftX = int(x)
					leftY = int(y)
					rightX = int(x + w)
					rightY = int(y + h)

					# draw bounding boxes for fields and boxes
					img_f.rectangle(img,(leftX, leftY),(rightX, rightY),color=(255,0,0),thickness=3)
			else:
				break
			dataIndex += 1

		editedImageName = imageName[:len(imageName)-4] + "_edited.png"
		print("writing to " + editedImageName + "...")
		img_f.imwrite(imageName[:len(imageName)-4] + "_edited.png", img)
		i += 1


def create_text(width, height):
	generator = synthetic_text.SyntheticText("fonts", ".",line_prob=0.0,line_thickness=70,line_var=0,mean_pad=10,
	pad=0,gaus_noise=0,gaus_std=0.0000001,blur_std=0.01,hole_prob=0.0, hole_size=400,neighbor_gap_var=0,rot=0.1, 
	use_warp=0.0,warp_std=[1,1.4], linesAboveAndBelow=False,useBrightness=False)

	#Logic for getting strings to be the correct length - or at least a length that looks good!
	widthHeightRatio = width / height
	# print("width to height ratio is " + str(widthHeightRatio)) # bigger means squatter, less letters

	numChars = int(widthHeightRatio * 1.5)

	img,text,fnt = generator.getSample(numChars)
	#img_f.imwrite("TEXT_IMG.png", img)	

	img = 255 - (img * 255)
	img = img_f.resize(img, (int(height), int(width)))
	return img
	

def extract_pdf_text(pdfName):
	print("extracting text...")
	pdf = pdfplumber.open(pdfName)
	for page in pdf.pages:
		text = page.extract_text()
		wordList = page.extract_words()
		lineList = []
		print(text)
		print("height and width of page is " 
		+ str(page.height) + " and " + str(page.width))
		for word in wordList:
			print(word)
			print(str(word["x0"]) + "," + str(word["x1"]))
			
			# use x0, x1 data differences to find the distance between text and group them?


args = read_args()
fileName = args[0]
imageRes = args[1]
if imageRes == 0:
	print("no resolution specified")
	resolutionSpecified = False
else:
	resolutionSpecified = True

pageWidth = 0.0

pageCount = create_image(fileName, imageRes, resolutionSpecified)
data = process_data(fileName, pageCount)
drawData, pageWidth, pageHeights = data

# data is a list of tuples (page, field type, x, y, w, h, pageHeight)
# with text fields, theres a 7th element - the included text
# draw_bounding_boxes(drawData, pageWidth, pageHeights)

# using pdfplumber's built in text extraction:
extract_pdf_text(fileName)


# current struggles: pdf2json and pdfplumber consider the page in different dimensions
# how do I connect fields and text?
# |
# |
# ---> convert pdfplumber's dimensions to pdf2json dimensions, then consider position
#	   of nearest text?
#
# how do I draw more correct bounding boxes?
# |
# |
# ---> extract words and then group words at the same x level
#	 |
#	 |
#	 ---> if the x difference between the last and this oen passes a certain ratio
#		  then they are probably different texts. All of this is given in the dict
#		  that is returned by extract_words()