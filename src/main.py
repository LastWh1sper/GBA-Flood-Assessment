from readJson import read_json_file
from readResults import readAllDepth
import os

readAllDepth('shenzhen',os.path.join( os.getcwd(), 'data','shenzhen'), 'shenzhen.tif', 1200)