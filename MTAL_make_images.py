# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 21:24:05 2017

@author: mike
"""
import csv, re
from PIL import Image,ImageColor, ImageDraw, ImageFont
import sys, os
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import *
import ctypes

myappid = u'DDHQ.2017.MTAL' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

input_csv_def=os.path.expanduser("~/Desktop/Sample MTAL.csv")
output_png_def=os.path.expanduser("~/Desktop/MTAL.png")


qt_app = QApplication(sys.argv)

def color_maps(input_csv,output_png):
    
    #Candidate profiles
    candidates={}
    candidates['QUIST']    ={'color':['#ccccff',
                                      '#9999ff',
                                      '#6666ff',
                                      '#0000ff', 
                                      '#0000cc', 
                                      '#000099',
                                      '#000077',
                                      '#000055'], 
                             'party':'D'}
    
    candidates['GIANFORTE'] ={'color':['#ffcccc',
                                       '#ff9999',
                                       '#ff6666',
                                       '#ff0000',
                                       '#cc0000',
                                       '#990000',
                                       '#770000',
                                       '#550000'],
                              'party':'R'}
    
    candidates['WICKS'] ={'color':'','party':'L'}
    #candidates['WRITE IN']   ={'color':'','party':'I'}
    
    for candidate in candidates:
        if(candidates[candidate]['color']==''):
            if(candidates[candidate]['party']=='L'):                
                candidates[candidate]['color']=['#f8edcc',
                                                '#f1db99',
                                                '#eac966',
                                                '#dd8500',
                                                '#b08400',
                                                '#846300',
                                                '#695300',
                                                '#473100']
    
    # Grab coordinates for each county
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
            county_xy[county]=int(nums[0]+0.5),int(nums[1]+0.5)
    
    # Get the 2016 gov results for comparison
    margins_gov_2016=dict()
    with open('./data_files/2016_MTGOV_margins.csv','rb') as csvfile:
        reader=csv.reader(csvfile)
        for row in reader:
            margins_gov_2016[row[0]]=float(row[1])
    
    # Get the 2016 house results for comparison
    margins_house_2016=dict()
    with open('./data_files/2016_MTAL_margins.csv','rb') as csvfile:
        reader=csv.reader(csvfile)
        for row in reader:
            margins_house_2016[row[0]]=float(row[1])
    
    # Grab votes from CSV input file
    votes_dict=dict()
    votes_file=open(input_csv,'rb')
    reader=csv.reader(votes_file)

    #headers = reader.next()
    #cand_col=[i for i,x in enumerate(headers) if 'CandidateName' in x][0]
    #prec_col=[i for i,x in enumerate(headers) if 'countyName' in x][0]
    #votes_col=[i for i,x in enumerate(headers) if 'Votes' in x][0]
    cand_col=5
    prec_col=4
    county_col=3
    votes_col=7
    precinct_dict=dict()
    for row in reader:
        precinct=row[county_col] + ' ' + row[prec_col]
        if(precinct not in precinct_dict):
            precinct_dict[precinct]=0
        cname=row[cand_col]
        candidate=[c for c in candidates if c in cname.upper()][0]
        county=row[county_col]
        county=re.sub('\s+$','',county)
        votes=int(row[votes_col])
        precinct_dict[precinct]+=votes
        if(county not in votes_dict):
            votes_dict[county]=dict()
        if(candidate not in votes_dict[county]):
            votes_dict[county][candidate]=votes
        else:
            votes_dict[county][candidate]=votes_dict[county][candidate]+votes
    
    precincts_reporting=len([precinct for precincts in precinct_dict if precinct_dict[precinct]>0])
    precincts=len(precinct_dict)
    
    im = Image.open("./data_files/MTAL_BW.png")
    im2 = Image.open("./data_files/MT_geo.png")

    size=im.size
    xsize=size[0]
    ysize=size[1]    

    size=im2.size
    xsize_geo=size[0]
    ysize_geo=size[1]    

    img_all=im.copy() # Top individual vote getters
    img_comp_gov=im.copy() # Compare Gianforte vs 2016 gov
    img_comp_house=im.copy() # Compare Gianforte vs 2016 house
    img_geo=im2.copy() # Geographic accurate
    
    mode="RGB"
    #img=img.convert(mode)
    white=ImageColor.getcolor('white',mode)
    black=ImageColor.getcolor('black',mode)
    gray=ImageColor.getcolor('gray',mode)
    for county in votes_dict:
        if(county in county_xy):
            all_votes=sum([votes_dict[county][candidate] for candidate in votes_dict[county]])
            order=sorted(votes_dict[county],key=votes_dict[county].get,reverse=True)
            best=order[0]
            next_best=order[1]
                
            # Color all candidates map, check if only one top votegetter, otherwise a tie
            best_votes=votes_dict[county][best]
            next_best_votes=votes_dict[county][next_best]
            if(all_votes>0):
                best_margin=float(best_votes-next_best_votes)/all_votes
            else:
                best_margin=0
            if(best_margin>0.5):
                color=ImageColor.getcolor(candidates[best]['color'][7],mode)
            elif(best_margin>0.4):
                color=ImageColor.getcolor(candidates[best]['color'][6],mode)
            elif(best_margin>0.3):
                color=ImageColor.getcolor(candidates[best]['color'][5],mode)
            elif(best_margin>0.2):
                color=ImageColor.getcolor(candidates[best]['color'][4],mode)
            elif(best_margin>0.15):
                color=ImageColor.getcolor(candidates[best]['color'][3],mode)
            elif(best_margin>0.1):
                color=ImageColor.getcolor(candidates[best]['color'][2],mode)
            elif(best_margin>0.05):
                color=ImageColor.getcolor(candidates[best]['color'][1],mode)
            elif(best_margin>0.):
                color=ImageColor.getcolor(candidates[best]['color'][0],mode)
            elif(best_votes>0):
                color=gray
            if(best_votes>0):
                ImageDraw.floodfill(img_all,(county_xy[county][0],county_xy[county][1]),color)
            
            if(all_votes>0):
                gianforte_margin=float(votes_dict[county]['GIANFORTE']-votes_dict[county]['QUIST'])/all_votes
            else:
                gianforte_margin=0.
            # Comparison map, how Gianforte is doing vs 2016 GOV
            delta_gov=gianforte_margin-margins_gov_2016[county]
            if(delta_gov>0):
                cand_color='GIANFORTE'
            else:
                cand_color='QUIST'
            if(abs(delta_gov)>0.5):
                color=ImageColor.getcolor(candidates[cand_color]['color'][7],mode)
            elif(abs(delta_gov)>0.4):
                color=ImageColor.getcolor(candidates[cand_color]['color'][6],mode)
            elif(abs(delta_gov)>0.3):
                color=ImageColor.getcolor(candidates[cand_color]['color'][5],mode)
            elif(abs(delta_gov)>0.2):
                color=ImageColor.getcolor(candidates[cand_color]['color'][4],mode)
            elif(abs(delta_gov)>0.15):
                color=ImageColor.getcolor(candidates[cand_color]['color'][3],mode)
            elif(abs(delta_gov)>0.1):
                color=ImageColor.getcolor(candidates[cand_color]['color'][2],mode)
            elif(abs(delta_gov)>0.05):
                color=ImageColor.getcolor(candidates[cand_color]['color'][1],mode)
            elif(abs(delta_gov)>0.):
                color=ImageColor.getcolor(candidates[cand_color]['color'][0],mode)
            elif(best_votes>0):
                color=gray
            if(all_votes>0):
                ImageDraw.floodfill(img_comp_gov,(county_xy[county][0],county_xy[county][1]),color)
            
            # Comparison map, how Gianforte is doing vs 2016 house
            delta_house=gianforte_margin-margins_house_2016[county]
            if(delta_house>0):
                cand_color='GIANFORTE'
            else:
                cand_color='QUIST'
            if(abs(delta_house)>0.5):
                color=ImageColor.getcolor(candidates[cand_color]['color'][7],mode)
            elif(abs(delta_house)>0.4):
                color=ImageColor.getcolor(candidates[cand_color]['color'][6],mode)
            elif(abs(delta_house)>0.3):
                color=ImageColor.getcolor(candidates[cand_color]['color'][5],mode)
            elif(abs(delta_house)>0.2):
                color=ImageColor.getcolor(candidates[cand_color]['color'][4],mode)
            elif(abs(delta_house)>0.15):
                color=ImageColor.getcolor(candidates[cand_color]['color'][3],mode)
            elif(abs(delta_house)>0.1):
                color=ImageColor.getcolor(candidates[cand_color]['color'][2],mode)
            elif(abs(delta_house)>0.05):
                color=ImageColor.getcolor(candidates[cand_color]['color'][1],mode)
            elif(abs(delta_house)>0.):
                color=ImageColor.getcolor(candidates[cand_color]['color'][0],mode)
            elif(best_votes>0):
                color=gray
            if(all_votes>0):
                ImageDraw.floodfill(img_comp_house,(county_xy[county][0],county_xy[county][1]),color)
        
    all_votes_dict=dict()
    for cand in candidates:
        all_votes_dict[cand]=sum([votes_dict[county][cand] for county in votes_dict])
    all_votes=sum(all_votes_dict[cand] for cand in candidates)
    order=sorted(all_votes_dict,key=all_votes_dict.get,reverse=True)
    
    img_combine=Image.new(mode,(1530,986),"white")
    yt=58+377/2
    yb=58+377+58*2+377/2
    xl=58+649/2
    xr=58+649+58*2+649/2
    xc=58+649+58
    yc=58+377+58
    
    img_ddhq=Image.open('./data_files/cropped-ddhq-icon.png')
    img_combine.paste(img_geo,(xl-xsize_geo/2,yt-ysize_geo/2,xsize_geo+(xl-xsize_geo/2),ysize_geo+(yt-ysize_geo/2)))
    img_combine.paste(img_all,(xr-xsize/2,yt-ysize/2,xsize+(xr-xsize/2),ysize+(yt-ysize/2)))
    img_combine.paste(img_comp_gov,(xl-xsize/2,yb-ysize/2,xsize+(xl-xsize/2),ysize+(yb-ysize/2)))
    img_combine.paste(img_comp_house,(xr-xsize/2,yb-ysize/2,xsize+(xr-xsize/2),ysize+(yb-ysize/2)))
    ddhq_size=img_ddhq.size
    img_ddhq=img_ddhq.resize((48,48))
    img_combine.paste(img_ddhq,(0+10,0+10,48+10,48+10))
    
    draw = ImageDraw.Draw(img_combine)
    font = ImageFont.truetype("FRAHVIT.TTF", 48)
    font_sm = ImageFont.truetype("micross.ttf", 24)
    font_half = ImageFont.truetype("micross.ttf", 16)
    
    # Title
    title="2017 MT-AL Special Election"
    draw.text((xc-64*len(title)/4+174, 10),title,black,font=font)    
    
    draw.text(( 0+10+xsize/16, yt+ysize/2-ysize/4),"1",black,font=font)
    draw.text(( 0+10+xsize/16, yb+ysize/2-ysize/4),"2",black,font=font)
    draw.text((xc+10+xsize/16, yb+ysize/2-ysize/4),"3",black,font=font)
    
    draw.text((0+10, yt+ysize/2-ysize/8),"Results",black,font=font_sm)
    draw.text((0+10, yb+ysize/2-ysize/8),"vs 2016 GOV",black,font=font_sm)
    draw.text((xc+10, yb+ysize/2-ysize/8),"vs 2016 House",black,font=font_sm)
    
    margins=['> 0%','> 5%','>10%','>15%','>20%','>30%','>40%','>50%']
    for k in range(8):
        draw.rectangle((xr-4*50+50*k,yc-25,xr-4*50+50*(k+1),yc),fill=candidates['QUIST']['color'][k],outline=black)
        draw.rectangle((xr-4*50+50*k,yc,xr-4*50+50*(k+1),yc+25),fill=candidates['GIANFORTE']['color'][k],outline=black)
        draw.text((xr-4*50+50*k,yc-50),margins[k],black,font=font_half)
    
    for k,cand in enumerate(order):
        draw.text((xl-125,yc-50+25*k),cand+' ('+candidates[cand]['party']+')',candidates[cand]['color'][3],font=font_half)
        if(all_votes>0):
            draw.text((xl,yc-50+25*k),'%5s' % str(100*round(float(all_votes_dict[cand])/all_votes,3))+'%',black,font=font_half)
        else:
            draw.text((xl,yc-50+25*k),'%5s' % str(0.0)+'%',black,font=font_half)
            
    draw.text((xc-90,986-38),str(precincts_reporting)+'/'+str(precincts)+' precincts reporting',black,font=font_half)    
    
    img_combine.save(output_png)

    img_all.close()
    img_comp_gov.close()
    img_comp_house.close()
    img_combine.close()
    
class LayoutExample(QWidget):
    ''' An example of PySide/PyQt absolute positioning; the main window
        inherits from QWidget, a convenient widget for an empty window. '''
 
    def __init__(self):
        # Initialize the object as a QWidget and
        # set its title and minimum width
        QWidget.__init__(self)
        self.setWindowTitle('2017 MTAL Special Election')
        self.setWindowIcon(QIcon('./data_files/cropped-ddhq-icon.png'))
        self.setMinimumWidth(600)
 
        self.color_maps=color_maps 
 
        # Create the QVBoxLayout that lays out the whole form
        self.layout = QVBoxLayout()
 
        # Create the form layout that manages the labeled controls
        self.form_layout = QFormLayout()
 
        # Create the entry control to specify a csv_input
        # and set its placeholder text
        self.csv_input = QLineEdit(self)
        self.csv_input.setPlaceholderText('CSV file')
        self.csv_input.setText(input_csv_def)
 
        # Add it to the form layout with a label
        self.form_layout.addRow('Input CSV file:', self.csv_input)

        # Add empty row

        # Create the entry control to specify an R vs D PNG
        # and set its placeholder text
        self.output = QLineEdit(self)
        self.output.setPlaceholderText('Output PNG file')
        self.output.setText(output_png_def)
 
        # Add it to the form layout with a label
        self.form_layout.addRow('Output PNG:', self.output)
  
        # Add the form layout to the main VBox layout
        self.layout.addLayout(self.form_layout)
 
        # Add stretch to separate the form layout from the button
        self.layout.addStretch(1)
 
        # Create a horizontal box layout to hold the button
        self.button_box = QHBoxLayout()
 
        # Add stretch to push the button to the far right
        self.button_box.addStretch(1)
 
        # Create the build button with its caption
        self.build_button = QPushButton('Generate PNG', self)

        # Add it to the button box
        self.button_box.addWidget(self.build_button)
        
        # Connect signal to button
        self.build_button.clicked.connect(self.on_click)
 
        # Add the button box to the bottom of the main VBox layout
        self.layout.addLayout(self.button_box)
 
        # Set the VBox layout as the window's main layout
        self.setLayout(self.layout)
        
    @pyqtSlot()
    def on_click(self):
        input_csv=str(self.csv_input.text())
        output_png=str(self.output.text())
        if(not os.path.isfile(input_csv)):
            self.error_message=QErrorMessage()
            self.error_message.setWindowTitle('File not found!')
            self.error_message.setWindowIcon(QIcon('./data_files/cropped-ddhq-icon.png'))
            self.error_message.showMessage('File '+input_csv+' not found!')
        else:
#            try:
            self.color_maps(input_csv,output_png)
#            except:
#                self.error_message=QErrorMessage()
#                self.error_message.setWindowTitle('Error!')
#                self.error_message.setWindowIcon(QIcon('cropped-ddhq-icon.png'))
#                self.error_message.showMessage(str(sys.exc_info()[0]))

                    
            
    def run(self):
        # Show the form
        self.show()
        # Run the qt application
        qt_app.exec_()
 
# Create an instance of the application window and run it
app = LayoutExample()
app.run()