# -*- coding: utf-8 -*-
"""
Created on Thu May 25 14:17:05 2017

@author: MGuidry
"""
import csv, re
import PIL
from PIL import Image,ImageColor, ImageDraw, ImageFont

county_xy=dict()
with open('./data_files/MTAL_coords.csv','rb') as csvfile:
    reader=csv.reader(csvfile)
    for row in reader:
        county=row[0]
        county=re.sub(' and ',' & ',county)
        s=row[1]
        s=re.sub('M ','',s)
        s=re.sub('L ','',s)
        s=re.sub(' z','',s)
        nums=[float(x) for x in s.split(' ')]
        xs=nums[0::2]
        ys=nums[1::2]
        #county_xy[county]=int(nums[0]+0.5),int(nums[1]+0.5)

county_xy['Powder River']=(628,313)
county_xy['Carter']=(628,292)
county_xy['Madison']=(324,303)
county_xy['Beaverhead']=(248,333)
county_xy['Big Horn']=(607,250)
county_xy['Carbon']=(504,311)
county_xy['Ravalli']=(193,298)
county_xy['Treasure']=(607,229)
county_xy['Deer Lodge']=(248,250)
county_xy['Custer']=(628,208)
county_xy['Park']=(471,282)
county_xy['Fallon']=(628,187)
county_xy['Stillwater']=(481,187)
county_xy['Jefferson']=(324,219)
county_xy['Silver Bow']=(283,270)
county_xy['Granite']=(250,187)
county_xy['Wibaux']=(628,166)
county_xy['Rosebud']=(607,166)
county_xy['Wheatland']=(481,166)
county_xy['Sweet Grass']=(460,166)
county_xy['Gallatin']=(395,261)
county_xy['Prairie']=(607,145)
county_xy['Golden Valley']=(481,145)
county_xy['Meagher']=(460,145)
county_xy['Powell']=(250,145)
county_xy['Judith Basin']=(460,124)
county_xy['Broadwater']=(357,143)
county_xy['Missoula']=(156,194)
county_xy['Mineral']=(61,124)
county_xy['Dawson']=(609,122)
county_xy['Garfield']=(586,103)
county_xy['Lake']=(93,114)
county_xy['McCone']=(586,82)
county_xy['Chouteau']=(460,82)
county_xy['Sanders']=(51,93)
county_xy['Richland']=(626,82)
county_xy['Petroleum']=(565,61)
county_xy['Yellowstone']=(544,155)
county_xy['Roosevelt']=(609,42)
county_xy['Musselshell']=(523,40)
county_xy['Teton']=(336,42)
county_xy['Lewis and Clark']=(303,109)
county_xy['Sheridan']=(628,19)
county_xy['Daniels']=(607,19)
county_xy['Phillips']=(565,19)
county_xy['Blaine']=(523,19)
county_xy['Fergus']=(483,63)
county_xy['Hill']=(471,30)
county_xy['Liberty']=(439,19)
county_xy['Cascade']=(402,82)
county_xy['Toole']=(355,19)
county_xy['Pondera']=(313,19)
county_xy['Glacier']=(271,22)
county_xy['Flathead']=(109,51)
county_xy['Lincoln']=(30,30)
county_xy['Valley']=(586,19)


# Grab coordinates for each county
county_geo_xy=dict()
with open('./data_files/MT_geo.csv','rb') as csvfile:
    reader=csv.reader(csvfile)
    for row in reader:
        county=row[0]
        county=re.sub(' and ',' & ',county)
        s=row[1]
        s=re.sub('[\[\]]','',s)
        nums=[float(x) for x in s.split(',')]
        x=min(int(nums[0]),646-10)
        x=int(round(float(nums[0])*617/649))
        y=min(int(nums[1]),376-10)
        county_geo_xy[county]=x,y

im = Image.open("./data_files/MTAL_BW.png")
im2 = Image.open("./data_files/MT_geo.png")

size=im.size
xsize=size[0]
ysize=size[1]    

size=im2.size
xsize_geo=size[0]
ysize_geo=size[1]    

img=im.copy() # 

img_geo=im2.convert('1') # Geographic accurate
img_geo=img_geo.convert('RGB') # Geographic accurate

font = ImageFont.truetype("micross.ttf", 24)
font2 = ImageFont.truetype("micross.ttf", 24)

img=img.resize((xsize*2,ysize*2), PIL.Image.ANTIALIAS)
draw=ImageDraw.Draw(img)

img_geo=img_geo.resize((xsize_geo*2,ysize_geo*2), PIL.Image.ANTIALIAS)
draw_geo=ImageDraw.Draw(img_geo)

for k,county in enumerate(sorted(county_xy.keys())):
    draw.text((2*county_xy[county][0]-5,2*county_xy[county][1]),str(k+1),'#00ff00',font=font)

for k,county in enumerate(sorted(county_geo_xy.keys())):
    draw_geo.text((2*(county_geo_xy[county][0]-2),2*(county_geo_xy[county][1]-9)),str(k+1),'#00ff00',font=font2)

f=open('cheat_sheet.txt','wb')
for k,county in enumerate(sorted(county_xy.keys())):
    print k+1,county
    f.write(str(k+1)+' '+county+'\r\n')
    
f.close()

img.save('MT_cheat_sheet.png')
img_geo.save('MT_geo_cheat_sheet.png')