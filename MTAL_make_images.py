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
    candidates['QUIST']    ={'color':['#9999ff','#0000ff','#0000dd','#000099'],'party':'D'}
    
    candidates['GIANFORTE']    ={'color':['#ff9999','#ff0000','#dd0000','#990000'],'party':'R'}
    
    candidates['WICKS'] ={'color':'','party':'I'}
    candidates['WRITE IN']   ={'color':'','party':'I'}
    
    for candidate in candidates:
        if(candidates[candidate]['color']==''):
            if(candidates[candidate]['party']=='D'):
                candidates[candidate]['color']=['#99f4ff','#00e6ff','#00c7dd','#008a99']
            elif(candidates[candidate]['party']=='R'):
                candidates[candidate]['color']=['#ff99f4','#ff00e6','#dd00c7','#99008a']
            else:
                candidates[candidate]['color']=['#ffd799','#ff9900','#dd8500','#995b00']
    
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
    votes_col=7
    for row in reader:
        cname=row[cand_col]
        candidate=[c for c in candidates if c in cname.upper()][0]
        county=row[prec_col]
        county=re.sub('\s+$','',county)
        votes=int(row[votes_col])
        if(county!='Marietta 5B'):
            if(county not in votes_dict):
                votes_dict[county]=dict()
            if(candidate not in votes_dict[county]):
                votes_dict[county][candidate]=votes
            else:
                votes_dict[county][candidate]=votes_dict[county][candidate]+votes
    
    im = Image.open("./data_files/MTAL_BW.png")

    size=im.size
    xsize=im.size[0]
    ysize=im.size[1]    

    img_all=im.copy() # Top individual vote getters
    img_comp_gov=im.copy() # Compare Gianforte vs 2016 gov
    img_comp_house=im.copy() # Compare Gianforte vs 2016 house
    
    mode="RGB"
    #img=img.convert(mode)
    white=ImageColor.getcolor('white',mode)
    black=ImageColor.getcolor('black',mode)
    for county in votes_dict:
        if(county in county_xy):
            all_votes=sum([votes_dict[county][candidate] for candidate in votes_dict[county]])
            order=sorted(votes_dict[county],key=votes_dict[county].get,reverse=True)
            best=order[0]
            next_best=order[1]
                
            # Color all candidates map, check if only one top votegetter, otherwise a tie
            best_votes=votes_dict[county][best]
            next_best_votes=votes_dict[county][next_best]
            best_margin=float(best_votes-next_best_votes)/all_votes
            if(best_margin>0.2):
                color=ImageColor.getcolor(candidates[best]['color'][3],mode)
            elif(best_margin>0.1):
                color=ImageColor.getcolor(candidates[best]['color'][2],mode)
            elif(best_margin>0.05):
                color=ImageColor.getcolor(candidates[best]['color'][1],mode)
            elif(best_margin>0.):
                color=ImageColor.getcolor(candidates[best]['color'][0],mode)
            elif(best_votes>0):
                color=white
            if(best_votes>0):
                ImageDraw.floodfill(img_all,(county_xy[county][0],county_xy[county][1]),color)

            gianforte_margin=float(votes_dict[county]['GIANFORTE']-votes_dict[county]['QUIST'])/all_votes
            # Comparison map, how Gianforte is doing vs 2016 GOV
            delta_gov=gianforte_margin-margins_gov_2016[county]
            if(delta_gov>0.2):
                color=ImageColor.getcolor(candidates['GIANFORTE']['color'][3],mode)
            elif(delta_gov>0.1):
                color=ImageColor.getcolor(candidates['GIANFORTE']['color'][2],mode)
            elif(delta_gov>0.05):
                color=ImageColor.getcolor(candidates['GIANFORTE']['color'][1],mode)
            elif(delta_gov>0.):
                color=ImageColor.getcolor(candidates['GIANFORTE']['color'][0],mode)
            elif(delta_gov>-0.05):
                color=ImageColor.getcolor(candidates['QUIST']['color'][0],mode)
            elif(delta_gov>-0.1):
                color=ImageColor.getcolor(candidates['QUIST']['color'][1],mode)
            elif(delta_gov>-0.2):
                color=ImageColor.getcolor(candidates['QUIST']['color'][2],mode)
            else:
                color=ImageColor.getcolor(candidates['QUIST']['color'][3],mode)
            if(all_votes>0):
                ImageDraw.floodfill(img_comp_gov,(county_xy[county][0],county_xy[county][1]),color)
            
            # Comparison map, how Gianforte is doing vs 2016 house
            delta_house=gianforte_margin-margins_house_2016[county]
            if(delta_house>0.2):
                color=ImageColor.getcolor(candidates['GIANFORTE']['color'][3],mode)
            elif(delta_house>0.1):
                color=ImageColor.getcolor(candidates['GIANFORTE']['color'][2],mode)
            elif(delta_house>0.05):
                color=ImageColor.getcolor(candidates['GIANFORTE']['color'][1],mode)
            elif(delta_house>0.):
                color=ImageColor.getcolor(candidates['GIANFORTE']['color'][0],mode)
            elif(delta_house>-0.05):
                color=ImageColor.getcolor(candidates['QUIST']['color'][0],mode)
            elif(delta_house>-0.1):
                color=ImageColor.getcolor(candidates['QUIST']['color'][1],mode)
            elif(delta_house>-0.2):
                color=ImageColor.getcolor(candidates['QUIST']['color'][2],mode)
            else:
                color=ImageColor.getcolor(candidates['QUIST']['color'][3],mode)
            if(all_votes>0):
                ImageDraw.floodfill(img_comp_house,(county_xy[county][0],county_xy[county][1]),color)

    img_combine=Image.new(mode,(2*xsize,2*ysize),"white")
    img_ddhq=Image.open('./data_files/cropped-ddhq-icon.png')

    img_combine.paste(img_all,(1*xsize/2,0,3*xsize/2,ysize))
    img_combine.paste(img_comp_gov,(0,ysize,xsize,2*ysize))
    img_combine.paste(img_comp_house,(xsize,ysize,2*xsize,2*ysize))
    ddhq_size=img_ddhq.size
    img_ddhq=img_ddhq.resize((48,48))
    img_combine.paste(img_ddhq,(0,0,48,48))
    
    draw = ImageDraw.Draw(img_combine)
    font = ImageFont.truetype("timesbi.ttf", 48)
    font_sm = ImageFont.truetype("times.ttf", 24)
    draw.text((1*xsize/2+xsize/16, ysize-ysize/4),"1",black,font=font)
    draw.text((0*xsize/2+xsize/16, 2*ysize-ysize/4),"2",black,font=font)
    draw.text((2*xsize/2+xsize/16, 2*ysize-ysize/4),"3",black,font=font)
    
    draw.text((1*xsize/2, ysize-ysize/8),"Results",black,font=font_sm)
    draw.text((0*xsize/2, 2*ysize-ysize/8),"vs 2016 GOV",black,font=font_sm)
    draw.text((2*xsize/2, 2*ysize-ysize/8),"vs 2016 House",black,font=font_sm)
    
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