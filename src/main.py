from readJson import read_json_file
from readResults import readAllDepth
import os
name = input('Please Input Project Name: ')
readAllDepth(name,os.path.join( os.getcwd(), 'data',name), name+'.tif', 1200)