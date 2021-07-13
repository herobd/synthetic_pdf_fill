import os
from synthetic_text_gen.synthetic_text_gen import synthetic_text
import sys
import json
import re
import os.path

import img_f

import pdfplumber
import numpy as np

# reads in provided file name and, if specified, a resolution
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


# takes PDF file and converts it to a numpy array, and saves it page by page in a .PNG file
def create_image(pdfName, imageRes, resolutionSpecified):
	with pdfplumber.open(pdfName) as pdf:
		pageCount = 0
		size = len(pdfName)
		dirName = pdfName[:size - 4] # removes .pdf file extension

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

		for page in pdf.pages:
			if generateNew:
				print("converting page number " + str(pageCount) + " to .png...")
				im = page.to_image(resolution=imageRes)
				# places page images in the newly created directory
				im.save(dirName + "/page" + str(pageCount) + ".png", format="PNG")
			pageCount += 1
	return pageCount


# to remove lines for text containing only the text found with the '[]'
def string_match(string, search=re.compile(r'[^_ .()•[\]]').search):
	return not bool(search(string))


# pulls box and field data from generated JSON file
def process_data(pdfName, pageCount):
	print("\nloading json file...")
	with open(pdfName[:len(pdfName)-4] + ".json", "r") as f:
		pdfInfo = json.load(f)
	
	fieldData = []
	i = 0
	#pageWidth = pdfInfo['formImage']['Width']
	pageHeights = []
	while i < pageCount:
		pageHeight = pdfInfo['formImage']['Pages'][i]['Height']
		pageHeights.append(pageHeight)

		# text data from pdf2json is jumbled, not particularly useful

		#for text in pdfInfo['formImage']['Pages'][i]['Texts']:
			#for textInfo in text['R']:
				#h = textInfo['TS'][1] # obtains height of text
				#info = textInfo['T']
			# replace the most common HTML encodings to make the text more legible
			#info = info.replace("%20", " ")
			#info = info.replace("%3A", ":")
			#info = info.replace("%2C", ",")
			#info = info.replace("%2F", "/")
			#include = string_match(info)

			# does the text contain only dashes and/or spaces? if so, don't add
			#if not include:
				#tuple = (i, "text", text['x'], text['y'], text['w'], h, info)
				#list.append(tuple) # what is height here?

		for field in pdfInfo['formImage']['Pages'][i]['Fields']:
			# some fields do not have names
			try:
				fieldName = field['TU']
				#print(str(i) + ". FIELD: " + field['TU'])
			except:
				fieldName = None
				#print(str(i) + ". FIELD name does not exist!")
			tuple = (i, fieldName, field['x'], field['y'], field['w'], field['h'])
			fieldData.append(tuple)

		for boxset in pdfInfo['formImage']['Pages'][i]['Boxsets']:
			for box in boxset['boxes']:
				try:
					boxName = box['TU']
					#print(str(i) + ". BOX: " + box['TU'])
				except:
					boxName = None
					#print(str(i) + ". BOX name does not exist!")
				tuple = (i, boxName, box['x'], box['y'], box['w'], box['h'])
				fieldData.append(tuple)

		i += 1

	return fieldData, pageHeights


# old print function to make sure that all data that can be pulled from JSON is pulled... needs updating
def print_list(list):
	counter = 0
	for dim in list:
		if dim[1] != "text":
			print(str(counter) + ".) page" + str(dim[0]) + ":" + dim[1] + ": x=" + str(dim[2]) + ", y=" +
		  		str(dim[3]) + ", w=" + str(dim[4]) + ", h=" + str(dim[5]))
		else:
			print(str(counter) + ".) page" + str(dim[0]) + ", text says: " + dim[6])

		counter += 1


# takes field and text data, along with page information, to draw bounding boxes
def draw_bounding_boxes(fieldData, textData, pageWidths, pageHeights):
	i = 0
	dataIndex = 0
	boxIndex = 0
	while i < pageCount:
		imageName = (pdfName[:len(pdfName)-4] + "/page" + str(i) + ".png")
		img = img_f.imread(imageName,color=True)
		imageHeight = img.shape[0]
		imageWidth = img.shape[1]

		heightMultiplier = imageHeight / pageHeights[i]
		widthMultiplier = imageWidth / pageWidths[i]
		# ^^^^^ why is there only one page width??

		print("drawing field boxes...")
		currPage = i
		while currPage == i and dataIndex < len(fieldData):
			currPage = fieldData[dataIndex][0]
			if currPage == i: # draw
				x = fieldData[dataIndex][2] * widthMultiplier
				y = fieldData[dataIndex][3] * heightMultiplier
				w = fieldData[dataIndex][4] * widthMultiplier
				h = fieldData[dataIndex][5] * heightMultiplier 

				leftX = int(x)
				leftY = int(y)
				rightX = int(x + w)
				rightY = int(y + h)

				# draw bounding boxes for fields and boxes
				img_f.rectangle(img,(leftX, leftY),(rightX, rightY),color=(255,0,0),thickness=3)
			else:
				break
			dataIndex += 1

		print("drawing text boxes...")
		currPage = i
		while currPage == i and boxIndex < len(textData):
			# box: (pageNum, x0, x1, text, textHeight, topY)
			currPage = textData[boxIndex][0]
			if currPage == i:
				leftX = int(textData[boxIndex][1] * imageWidth)
				leftY = int(textData[boxIndex][5] * imageHeight)
				rightX = int(textData[boxIndex][2] * imageWidth)
				rightY = int((textData[boxIndex][4] * imageHeight) + leftY)

				img_f.rectangle(img,(leftX, leftY),(rightX, rightY),color=(0,220,30),thickness=3)
			else:
				break
			boxIndex += 1

		editedImageName = imageName[:len(imageName)-4] + "_edited.png"
		print("writing to " + editedImageName + "...")
		img_f.imwrite(imageName[:len(imageName)-4] + "_edited.png", img)
		i += 1


# creates a numpy array image of text that can be inserted into the form
def create_text(width, height):
	generator = synthetic_text.SyntheticText("fonts", ".",line_prob=0.0,line_thickness=70,line_var=0,mean_pad=10,
		pad=0,gaus_noise=0,gaus_std=0.0000001,blur_std=0.01,hole_prob=0.0, hole_size=400,neighbor_gap_var=0,rot=0.1, 
		use_warp=0.0,warp_std=[1,1.4], linesAboveAndBelow=False,useBrightness=False)

	#Logic for getting strings to be the correct length - or at least a length that looks good!
	widthHeightRatio = width / height
	# print("width to height ratio is " + str(widthHeightRatio)) # bigger means squatter, less letters

	numChars = int(widthHeightRatio * 1.5)

	img,text,fnt = generator.getSample(numChars)

	img = 255 - (img * 255)
	img = img_f.resize(img, (int(height), int(width)))
	return img
	

# finds and draws boxes around text entity... needs work with multiline texts
def extract_text_boxes(pdfName):
	print("extracting text...")
	pdf = pdfplumber.open(pdfName)
	pageNum = 0
	boxList = []
	pageWidths = []
	for page in pdf.pages:
		wordList = page.extract_words()
		pageHeight = page.height
		pageWidth = page.width
		pageWidths.append(pageHeights[pageNum] * float(pageWidth / pageHeight))
		#print("height and width of page is " 
		#+ str(pageHeight) + " and " + str(pageWidth))

		lastWord = wordList[0]
		box_x0 = lastWord['x0']
		box_x1 = lastWord['x1']
		textLine = lastWord['text']
		lastWordHeight = lastWord['bottom'] - lastWord['top']
		height = lastWordHeight
		top = lastWord['top']

		for word in wordList[1:]:
			lastWordHeight = lastWord['bottom'] - lastWord['top']
			wordHeight = word['bottom'] - word['top']
			if(lastWordHeight < wordHeight):
				height = wordHeight

			#print("the space between '" + word['text'] + "' and '" + lastWord['text'] + "' is "
			#+ str(word['x0'] - lastWord['x1']))
			#print("pageHeight: "+str(pageHeight)+", wordHeight: "+str(wordHeight)+
			#	", word['x0']-word['x1: " + str(float(word['x0'] - lastWord['x1'])))
			if float(word['x0'] - lastWord['x1']) == 0.0:
				heightsToGapRatio = float(wordHeight)
			else:
				heightsToGapRatio = float(wordHeight) / float(word['x0'] - lastWord['x1'])

			### x[0] matching for multiline text? --maps of dictionaries w/ ranges for indicies?
			### ---> consider x[0], top, and textHeight (i.e., left aligned? are lines appropriately close?)
			
			#print("page height to wordHeight to wordGap ratio is " +
			#str(heightsToGapRatio))

			if string_match(word['text']):
				continue
			elif heightsToGapRatio > 2.3: # ratio maybe should be tweaked to better detect word spacing?
				# CONTINUE box... append word, change x1
				textLine = textLine + " " + word['text']
				box_x1 = word['x1']
			else:
				# CREATE box
				boxInfo = (pageNum, (float(box_x0) / float(pageWidth)), (float(box_x1) / float(pageWidth)), 
						textLine, (float(height) / float(pageHeight)), (float(top) / float(pageHeight)))
				# boxInfo = pageNum, x0, x1, text, height, top(y)
				#print("text is: " + textLine + " with height " + str(height))
				boxList.append(boxInfo)
				# create new bounding box
				#lineSpacing = word['top'] - (top + height)
				#if word['top'] < top:
				#	lineSpacingRatio = float(pageHeight) / float(wordHeight) / float(lineSpacing)
				#	print("'" + textLine + "'")
				#	print("\t|___.> line spacing ratio is " + str(lineSpacingRatio))
				#print("\ttextline is " + textLine)
				box_x0 = word['x0']
				box_x1 = word['x1']
				height = word['bottom'] - word['top']
				top = word['top']
				textLine = word['text']
				
			lastWord = word

		#print("  CREATE a new bounding box with '" + textLine + "'")
		boxInfo = (pageNum, (float(box_x0) / float(pageWidth)), (float(box_x1) / float(pageWidth)), 
				textLine, (float(height) / float(pageHeight)), (float(top) / float(pageHeight)))
		#print(boxInfo)
		boxList.append(boxInfo)

		pageNum += 1
		
	return boxList, pageWidths


# seeks to find the connection between text and associated fields and boxes
def field_text_relations(fieldData, textData, pageWidths, pageHeights):
	print("finding the relationship between boxes, fields, and text!") 
	totalTextCount = 0
	pageTextCount = 0
	currPage = 0

	# don't want to constantly be reading in an image
	imageName = (pdfName[:len(pdfName)-4] + "/page" + str(currPage) + ".png")
	img = img_f.imread(imageName,color=True)
	imageHeight = img.shape[0]
	imageWidth = img.shape[1]
	#print("Page " + str(currPage) + " has height " + str(imageHeight) + " & width " + str(imageWidth))

	for field in fieldData:
		print("\n------ new field ------\n")
		# should be ordered by page, so iterating through will work
		if field[0] != currPage:
			print("\n------ new page ------\n")
			currPage = field[0]
			imageName = (pdfName[:len(pdfName)-4] + "/page" + str(currPage) + ".png")
			img = img_f.imread(imageName,color=True)
			imageHeight = img.shape[0]
			imageWidth = img.shape[1]

			#print("Page " + str(currPage) + " has height " + str(imageHeight) + " & width " + str(imageWidth))
			pageTextCount = totalTextCount
		else:
			# gotta keep textCount to iterate through until a new page
			totalTextCount = pageTextCount

		pageHeight = pageHeights[currPage]	
		pageWidth = pageWidths[currPage]
		heightMultiplier = imageHeight / pageHeight
		widthMultiplier = imageWidth / pageWidth

		field_x = int(field[2] * widthMultiplier)
		field_y = int(field[3] * heightMultiplier)
		field_w = int(field[4] * widthMultiplier)
		field_h = int(field[5] * heightMultiplier) 

		#leftX = int(x)
		#leftY = int(y)
		#rightX = int(x + w)
		#rightY = int(y + h)

		if field[1] == None:
			for text in textData:
				#tuple = (i, boxName, box['x'], box['y'], box['w'], box['h'])
				#boxInfo = (pageNum, (float(box_x0) / float(pageWidth)), (float(box_x1) / float(pageWidth)), 
				#textLine, (float(height) / float(pageHeight)), (float(top) / float(pageHeight)))
				#print(str(field) + str(text))
				# TEXT INFO (ratios) -> [0]:pageNum, [1]:x0, [2]:x1, [3]:textLine, [4]:height, [5]:top
				# BOX INFO -> [0]:pageNum, [1]:boxName, [2]:x, [3]:y, [4]:w, [5]:h
				if text[0] == field[0]:
					# this is where all the work should happen
					totalTextCount += 1

					# TEXT INFO
					text_x0 = int(text[1] * imageWidth)
					text_x1 = int(text[2] * imageWidth)
					text_h = int(text[4] * imageHeight)
					text_top = int(text[5] * imageHeight)

					leftMargin = text_x1 - (field_x + field_w)
					rightMargin = text_x0 - field_x
					topMargin = field_y - (text_top + text_h)
					bottomMargin = text_top - (field_y + field_h)

					# convert to ratio to disregard differences in page size/resolution
					print("FIELD: x=" + str(field_x) + ", y=" + str(field_y) + ", w=" + str(field_w) + ", h=" + str(field_h))
					print("TEXT: x0=" + str(text_x0) + ", x1=" + str(text_x1) + ", h=" + str(text_h) + ", top=" + str(text_top))
					print("LEFT:" + str(leftMargin) + ", RIGHT:" + str(rightMargin) + 
						", TOP:" + str(topMargin) + ", BOTTOM:" + str(bottomMargin))
					print("---> '" + text[3] + "'\n")

					# bunch of ifs to check conditions?


args = read_args()
pdfName = args[0]
imageRes = args[1]
if imageRes == 0:
	print("no resolution specified")
	resolutionSpecified = False
else:
	resolutionSpecified = True

pageCount = create_image(pdfName, imageRes, resolutionSpecified)
fieldData, pageHeights = process_data(pdfName, pageCount)
textData, pageWidths = extract_text_boxes(pdfName)
draw_bounding_boxes(fieldData, textData, pageWidths, pageHeights)
field_text_relations(fieldData, textData, pageWidths, pageHeights)