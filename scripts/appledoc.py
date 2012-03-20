#! /usr/bin/env python
#
# appledoc.py
#
# Created by Josh Kennedy on 9/1/11.
# Copyright 2011 Deadmeta4 Software, LLC. All rights reserved.
#
# A simple script to execute Appledoc against an iOS project.
#
# Users should modify the [PROJECT_NAME] & [PROJECT_COMPANY] values in this script.
# -------------------------------------------------------------------------

import sys
from optparse import OptionParser
import subprocess
import glob
import os
import re
import copy
from optparse import OptionParser

_appledocCommand = "/usr/local/bin/appledoc"	# path to your appledoc binary
_projectName = "[PROJECT_NAME]" 				# shows up on upper left of generated documentation
_projectCompany = "[PROJECT_COMPANY]" 			# shows up on upper right of generated documentation


def executeAppleDoc( inputPath=None, outputPath=None ):

    if( inputPath is None ):
        print "the input parameter is required"
        sys.exit( 1 )
        
    if( outputPath is None ):
        print "the output parameter is required"
        sys.exit( 1 )
    
    cmd = [ _appledocCommand ]
    cmd.extend( [ "-o", outputPath ] )
    cmd.extend( [ "-p", _projectName ] )
    cmd.extend( [ "-c", _projectCompany ] )
    cmd.extend( [ "--no-create-docset" ] ) 	# supresses docset creation
    cmd.extend( [ "-h" ] ) 					# make Appledoc only generate HTML
    cmd.extend( [ "-v", "6" ] ) 			# verbosity: 0-6
    cmd.extend( [ inputPath ] )
    
    print "EXECUTING: " + " ".join( cmd )
    subprocess.Popen( cmd ).communicate()



# MAIN

parser = OptionParser()
parser.add_option( "-o", "--output", dest="output", help="Path to folder where output should be created." )
parser.add_option( "-i", "--input", dest="input", help="Path to folder where source code to scan lives." )
(options, args) = parser.parse_args()

executeAppleDoc( options.input, options.output )
