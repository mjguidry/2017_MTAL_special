# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 13:00:42 2017

@author: MGuidry
"""
import sys
from distutils.core import setup
import py2exe

sys.setrecursionlimit(1500)
data_file_dir=r'C:\Users\MGUIDRY\Documents\GitHub\2017_MTAL_special\data_files'
data_files=[('data_files',[data_file_dir+r'\2016_MTAL_margins.csv',
data_file_dir+r'\2016_MTGOV_margins.csv',
data_file_dir+r'\cropped-ddhq-icon.png',
data_file_dir+r'\MTAL_BW.png',
data_file_dir+r'\MTAL_coords.csv',
data_file_dir+r'\MT_geo.csv',
data_file_dir+r'\MT_geo.png'])]


setup(
    console=['MTAL_make_images.py'],
    data_files=data_files,
    options={
        "py2exe":{
            "includes":"PIL,PyQt4,sip",
            "dll_excludes": ["MSVCP90.dll"],
            "unbuffered":True,
            "optimize":2}}
    )