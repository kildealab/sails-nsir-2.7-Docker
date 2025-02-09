#------------------------------------------------------------------------------------
# This script is to be run at the time of installation of SaILS. It will replace
# pertinent files within dependencies that were downloaded via pip install (i.e. in 
# the virutal environment), with custom files stored in the custom_dependencies/ 
# directory.
#------------------------------------------------------------------------------------
from shutil import copyfile
import os
from os import listdir
from os.path import isfile, join

SOURCE_DIR = 'custom_dependencies'
VENV_PATH = '/usr/local/lib/python2.7/dist-packages/'

# Get all custom files
custom_files = [f for f in listdir(SOURCE_DIR) if isfile(join(SOURCE_DIR, f))]

# Convert custom file names to paths, prepend the venv path, and copy each file
for cfile in custom_files:
    cpath = cfile.replace('_','/')
    cpath = cpath.replace('-','_')
    if isfile(VENV_PATH+cpath):
        copyfile(SOURCE_DIR+'/'+cfile, VENV_PATH+cpath)