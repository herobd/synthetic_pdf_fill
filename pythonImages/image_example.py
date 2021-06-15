import numpy as np #Images are going to be numpy arrays
import img_f #This is my image processing functions
            #I originally used OpenCV, which is a very good and well used Computer Vision library
            #However, I recently have had issues installing it with Anaconda in parallel with other packages I need
            #So this wraped Scikit's image functions to have the same call signature as OpenCV


#This will walk through some basic stuff

#Read in image as grayscale
img = img_f.imread('example.png',color=False)
print(img.dtype) #this is a float image, so values of 0 to 1 (black to white)
print(img.shape) #this is a 480x480 image.
 
#draw a line (points are x,y)
img_f.line(img,(0,0),(100,200),color=0,thickness=5)

#directly change a single pixel (indexing is rows,col or y,x)
img[20,43]=0

#change region to white
img[400:460,20:80]=1 #This is numpy indexing. It broadcasts the value to all the range


#We can also do fancier broadcasting
black_white = np.array([1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1]) #alternating white and black, single vector
len_black_white = black_white.shape[0] #get it's length, because I'm lazy and don't want to count

black_white = black_white[:,None] #Add a new dimension (of length 1) which is now the x dimension

img[400:400+len_black_white, 400:460] = black_white 
#This broadcasts the black_white along it's singleton dimension (x)
#the "400:400+len_black_white" is setting it's y position (and range matched to black_white's length)
#the "400:460" is the range in the x dimension we're broadcasting too


#Make part of the image lighter
img[0:40,440:] *=2 #you can leave off the last number of a span to indicate it goes to the end of the image
#OH NO! Becuase we just multiplied, we might have some values above 1 now
#let's fix that
img[img>1] = 1 
#"img>1" is a binary array with True/1 everywhere the image has a pixel value greater than 1
#We can index an array with a binary array so we only get the values where the binary array is true
#so all together this sets all values greater than 1 to 1.

#Copy part of the image somewhere else
part = img[375:445,120:215]
img[390:390+part.shape[0], 290:290+part.shape[1]] = part


#And a quick example of drawing a bounding box (BB)
#we probably want to make the BB in color so it stands out
#Convert to color
img = np.stack((img,img,img),axis=2) #stack it into the three color channels
#OR
#img = np.repeat(img,3,axis=2) #use the repeat function

#There's a function to make drawing a BB easier, you just need to top-left and bottom-right corners (again x,y here)
#Color is now a 3-tuple for RGB (we just draw red here)
img_f.rectangle(img,(40,180),(410,360),color=(1,0,0),thickness=4)


#You can alternatively hightlight a region like this
img[63:100,282:323,0]=0 #This sets the red channel to 0, leaving the rest cyan
#Or
img[112:140,226:262,1]=1 #This sets the green channel to 1

#For documents (which mostly white backgroun) the first highlight method usuall works best

#write the image out
img_f.imwrite('edited.png',img)
#If you have any value higher than 1, it will reinturpt the max value as 255 and save it accordingly, so be careful!
