from PIL import Image
import numpy as np
from cv2 import cv2 
import time
import math
import os

def drawpts(pts,h,w,imgname):
    pixels=np.full((h,w),255)
    for pt in pts:
        pixels[pt[0]][pt[1]]=0
    new_img = Image.fromarray(pixels.astype(np.uint8))
    new_img.save(imgname)

def finddensities(img,sumdict,vregs,h,w,numpts):
    for reg in range(numpts):
        sumdict[reg+1]=0
    for x in range(h):
        for y in range(w):
            sumdict[vregs[x][y]]+=img[x][y] 
    #normalize depths to 0-255 scale
    for pt in sumdict.keys():
        sumdict[pt]/=255.0
#Fastest centroid finder
def findcentroidsfast(vregs,h,w,numpts):
    cents = []
    for x in range(numpts):
        cents.append([0,0,0]) #sumx,sumy, total summed
    for x in range(len(vregs)):
        for y in range(len(vregs[x])):
            cents[vregs[x][y]-1][0]+=x
            cents[vregs[x][y]-1][1]+=y
            cents[vregs[x][y]-1][2]+=1
    for reg in range(len(cents)):
        if cents[reg][2]!=0:
            cents[reg][0]/=cents[reg][2]
            cents[reg][1]/=cents[reg][2]
            cents[reg][0]=int(cents[reg][0])
            cents[reg][1]=int(cents[reg][1])
    return cents

def findbounds(vregs,h,w,needsplit):
    bounds = []
    for x in range(max(needsplit)):
        bounds.append([])
    for x in range(h):
        for y in range(w):
            if vregs[x][y] in needsplit:
                if x==0 or x==h-1 or y==0 or y==w-1:
                    bounds[vregs[x][y]-1].append((x,y))
                elif vregs[x][y] != vregs[x+1][y] or vregs[x][y] != vregs[x-1][y] or vregs[x][y] != vregs[x][y+1] or vregs[x][y] != vregs[x][y-1]:
                    bounds[vregs[x][y]-1].append((x,y))
    return bounds

def splitter(bounds,centlist,vregs,needsplit):
    newpts= []
    for pt in needsplit:
        biggestd = 0
        bigcoor = []
        for x in range(len(bounds[pt-1])):
            disx = bounds[pt-1][x][0]-centlist[pt-1][0]
            disy = bounds[pt-1][x][1]-centlist[pt-1][1]
            if centlist[pt-1][1]-disy < len(vregs[0]) and centlist[pt-1][0]-disx < len(vregs):
                if vregs[centlist[pt-1][0]-disx][centlist[pt-1][1]-disy]==pt:
                    dis = math.sqrt(disx**2+disy**2)
                    if dis>biggestd:
                        biggestd = dis
                        bigcoor = [disx,disy]
        if bigcoor != []:
            newpts.append((int(centlist[pt-1][0]+bigcoor[0]/2),int(centlist[pt-1][1]+bigcoor[1]/2)))
            newpts.append((int(centlist[pt-1][0]-bigcoor[0]/2),int(centlist[pt-1][1]-bigcoor[1]/2)))
        else:
            newpts.append((centlist[pt-1][0],centlist[pt-1][1]))
    return newpts

def splitmerge(depthmap,lower,upper,vregs,numpts,h,w):
    centlist = findcentroidsfast(vregs,h,w,numpts)
    needsplit = []
    newpts = []
    for pt in depthmap.keys():
        if depthmap[pt]>upper:
            needsplit.append(pt)
            #split em
        elif depthmap[pt]>lower:
            newpts.append((centlist[pt-1][0],centlist[pt-1][1]))
            #center then keep em
        #otherwise delete em
    #bounds = [[(x,y),(x,y)],[(x,y),(x,y)]...] each index corresponds to point #
    if len(needsplit)!=0:
        bounds = findbounds(vregs,h,w,needsplit)
        splitted = splitter(bounds,centlist,vregs,needsplit)
        for pt in splitted:
            newpts.append(pt)
    return newpts

fullstart = time.time()
openf = "glong.png"
path = "./samples/"+openf
img = cv2.imread(path,cv2.IMREAD_GRAYSCALE)
height,width = img.shape[:2]
print (height,width)

#invert the image
img = np.float32([[(255-img[x,y]) for y in range(width)] for x in range(height)])
pts=[]

#initial set of points
for x in range(1,height,50):
    for y in range(1,width,50):
        pts.append((x,y))

lbound = 5 #increases amount of points
ubound = 8 #increases density

despts = 8000 #target #
while len(pts)<despts:
    start = time.time()
    drawpts(pts,height,width,'new.png')
    ptimg= cv2.imread('new.png',cv2.IMREAD_GRAYSCALE)
    dist1,vregs = cv2.distanceTransformWithLabels(ptimg,cv2.DIST_L2,5,labelType=cv2.DIST_LABEL_CCOMP)
    depthmap = {}
    #turn vregs into a list because ndarray is somehow much slower
    vregs=vregs.tolist()
    end = time.time()
    print ("INTIALIZE IMAGE:",end-start)

    start =time.time()
    finddensities(img,depthmap,vregs,height,width,len(pts))
    end=time.time()
    print ("DENSITIES:",end-start)
    opts = len(pts)
    print ("# of points:", len(pts))
    bo = []
    start=time.time()
    pts = splitmerge(depthmap,lbound,ubound,vregs,len(pts),height,width)
    if len(pts)<opts:
        print ("ERROR: DESIRED POINTS NOT ACHIEVABLE WITH SPECIFIED PARAMETERS")
        break
    end=time.time()
    print ("SPLITTING:",end-start)

print ("Total points:", len(pts))
fname = openf[0:-4]+'L'+str(lbound)+'U'+str(ubound)+'Pts'+str(len(pts))+'.png'
drawpts(pts,height,width,fname)
os.remove("new.png")

fullstop=time.time()
print ("TIME ELAPSED:",fullstop-fullstart)
