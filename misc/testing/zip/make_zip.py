#!/usr/bin/env python

# Copyright 2009-2011 Ram Rachum.
# This program is distributed under the LGPL2.1 license.

'''
'''

# blocktodo: should work with python 3, try it

from __future__ import with_statement

import os.path
import zipfile
import contextlib
import shutil

def zip_folder(folder, zip_path, ignored_extenstions=[]):
    '''
    note: creates a folder inside the zip with the same name of the original
    folder, in contrast to other implementation which put all of the files on
    the root level of the zip.
    
    Doesn't put empty folders in the zip file.
    '''
    # blocktodo: make pretty
    assert os.path.isdir(folder)
    
    ### Ensuring ignored extensions start with '.': ###########################
    #                                                                         #
    for ignored_extenstion in ignored_extenstions:
        if not ignored_extenstion.startswith('.'):
            ignored_extenstions[
                ignored_extenstions.index(ignored_extenstion)
                ] = \
            ('.' + ignored_extenstion)
    #                                                                         #
    ### Finished ensuring ignored extensions start with '.'. ##################
            
    with contextlib.closing(
        zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
        ) as zip_file:
        
        for root, subfolders, files in os.walk(folder):
            
            for file_path in files:
                
                extension = os.path.splitext(file_path)[1]
                if extension in ignored_extenstions:
                    continue
                
                absolute_file_path = os.path.join(root, file_path)
                
                destination_file_path = \
                    absolute_file_path[(len(folder) + len(os.sep)):]
                print(absolute_file_path)
                zip_file.write(absolute_file_path, destination_file_path)

                
###############################################################################
#                                                                             #
# tododoc: helpful error messages:
assert __name__ == '__main__'
module_path = os.path.split(__file__)[0]
assert module_path.endswith(os.path.sep.join(('misc', 'testing', 'zip')))
repo_root_path = os.path.realpath(os.path.join(module_path, '../../..'))
assert os.path.realpath(os.getcwd()) == repo_root_path
assert module_path == \
    os.path.realpath(os.path.join(repo_root_path, 'misc', 'testing', 'zip'))
#                                                                             #
###############################################################################
       
### Preparing build folder: ###################################################
#                                                                             #
build_folder = os.path.join(module_path, 'build')
if os.path.exists(build_folder):
    shutil.rmtree(build_folder)
os.mkdir(build_folder)
#                                                                             #
### Finished preparing build folder. ##########################################

### Zipping packages into zip files: ##########################################
#                                                                             #
package_names = ['garlicsim', 'garlicsim_lib', 'garlicsim_wx']

for package_name in package_names:
    package_path = os.path.join(repo_root_path, package_name, package_name)
    assert os.path.isdir(package_path)
    zip_destination_path = os.path.join(build_folder,
                                        (package_name + '.zip'))    
    zip_folder(package_path, zip_destination_path,
               ignored_extenstions=['.pyc', '.pyo'])
#                                                                             #
### Finished zipping packages into zip files. #################################

# todo: can make some test here that checks that the files were zipped properly
# and no pyo or pyc files were copied.