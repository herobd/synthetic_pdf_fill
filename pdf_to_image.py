import os
import sys
import json

import img_f

import numpy as np
import pdfplumber

def read_args():
	if __name__ == "__main__":
		imageRes = 150 # if no command line argument passed, resolution is 150
		for i, arg in enumerate(sys.argv):
			if i == 1:
				fileName = arg # commandline argument specifies PDF to convert to PNG
				print("\nfile name is " + fileName)
			if i == 2:
				imageRes = int(arg)

	return (fileName, imageRes)


def create_image(fileName, imageRes):
	with pdfplumber.open(fileName) as pdf:
		pageCount = 0
		size = len(fileName)
		dirName = fileName[:size - 4] # removes .pdf file extension

		if not os.path.exists(dirName):
			os.mkdir(dirName) # if directory doesn't exist, create one to store new images
		print("selected resolution is " + str(imageRes))

		for page in pdf.pages:
			print("converting page number " + str(pageCount) + " to .png...")
			im = page.to_image(resolution=imageRes) # default of 72 results in some illegible pages
			# places page images in the newly created directory
			im.save(dirName + "/page" + str(pageCount) + ".png", format="PNG")
			pageCount += 1

	return pageCount


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

		# extracts text data and puts in tuple... ignore for now!
		for text in pdfInfo['formImage']['Pages'][i]['Texts']:
			for textInfo in text['R']:
				h = textInfo['TS'][1] # obtains height of text
			tuple = (i, "text", text['x'], text['y'], text['w'], h)
			list.append(tuple) # what is height here?

		for field in pdfInfo['formImage']['Pages'][i]['Fields']:
			tuple = (i, "field", field['x'], field['y'], field['w'], field['h'])
			list.append(tuple)

		for boxset in pdfInfo['formImage']['Pages'][i]['Boxsets']:
			for box in boxset['boxes']:
				tuple = (i, "box", box['x'], box['y'], box['w'], box['h'])
				list.append(tuple)

		i += 1

	# counter = 0
	# for dim in list:
		# print(str(counter) + ".) page" + str(dim[0]) + ":" + dim[1] + ": x=" + str(dim[2]) + ", y=" +
		#  	str(dim[3]) + ", w=" + str(dim[4]) + ", h=" + str(dim[5]))
		# counter += 1
	
	return list, pageWidth, pageHeights


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
					img_f.line(img,(int(x),int(y)),(int(x)+int(w),int(y)),color=(0,1,0),thickness=4)
				else:
					h = list[dataIndex][5] * heightMultiplier # height for text is WRONG

					leftX = int(x)
					leftY = int(y)
					rightX = int(x + w)
					rightY = int(y + h)

					img_f.rectangle(img,(leftX, leftY),(rightX, rightY),color=(1,0,0),thickness=4)
			else:
				break
			dataIndex += 1

		editedImageName = imageName[:len(imageName)-4] + "_edited.png"
		print("writing to " + editedImageName + "...")
		img_f.imwrite(imageName[:len(imageName)-4] + "_edited.png", img)
		i += 1


args = read_args()
fileName = args[0]
imageRes = args[1]

pageWidth = 0.0

pageCount = create_image(fileName, imageRes)
data = process_data(fileName, pageCount)
drawData = data[0]
pageWidth = data[1]
pageHeights = data[2]

# data is a list of tuples (page, field type, x, y, w, h, pageHeight)
draw_bounding_boxes(drawData, pageWidth, pageHeights)