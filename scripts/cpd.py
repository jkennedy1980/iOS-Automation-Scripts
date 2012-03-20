#! /usr/bin/env python
#
# cpd.py
#
# Created by Josh Kennedy on 9/16/11.
# Copyright 2011 Deadmeta4 Software, LLC. All rights reserved.
#
# A simple script to execute CPD against an iPhone project.  This script requires
# that the PMD and ObjCLanguage jars are installed in a Libraries folder which is a 
# sibling to this script.  Here is an example directory listing:
#
# .../cpd.py
# .../Libraries/ObjCLanguage-0.0.6-SNAPSHOT.jar
# .../Libraries/pmd-4.2.5.jar
#
# NOTE: versions numbers will need to be changed in this file if you are using different
#		versions of PMD jar and/or the ObjCLanguage jar.
#
# -------------------------------------------------------------------------

import sys
from optparse import OptionParser
import subprocess
import glob
import os
import re
import copy
from optparse import OptionParser
import codecs

def executeCPD( inputPath=None, outputPath=None, minimumTokens=None, debug=None ):

	if( inputPath is None ):
		print "the input parameter is required"
		sys.exit( 1 )

	if( outputPath is None ):
		print "the output parameter is required"
		sys.exit( 1 )

	outputFile = codecs.open( outputPath, encoding='UTF-8', mode='w+') #open( outputPath, 'w' )

	cmd = [ "java", "-Xmx512m", "-Dfile.encoding=UTF-8" ]

	if( debug is not None ):
		cmd.extend( [ "-DObjC-CPD-LoggingEnabled=YES" ] )

	cmd.extend( [ "-classpath", sys.path[0] + "/Libraries/pmd-4.2.5.jar:" + sys.path[0] + "/Libraries/ObjCLanguage-0.0.6-SNAPSHOT.jar" ] )
	cmd.extend( [ "net.sourceforge.pmd.cpd.CPD" ] ) # executable CPD class
	cmd.extend( [ "--minimum-tokens", minimumTokens ] )
	cmd.extend( [ "--files", inputPath ] )
	cmd.extend( [ "--language", "ObjectiveC" ] )
	cmd.extend( [ "--encoding", "UTF-8" ] )
	cmd.extend( [ "--format", "net.sourceforge.pmd.cpd.XMLRenderer" ] )

	print "EXECUTING: " + " ".join( cmd )
	subprocess.Popen( cmd, stderr=subprocess.STDOUT, stdout=outputFile ).communicate()

	outputFile.close()


# MAIN

parser = OptionParser()
parser.add_option( "-o", "--output", dest="output", help="Path to file where output should be created." )
parser.add_option( "-i", "--input", dest="input", help="Path to folder where source code to scan lives." )
parser.add_option( "-d", "--debug", dest="debug", help="Enabled additional console output but render invalid XML" )
parser.add_option( "-m", "--minimumTokens", dest="minimumTokens", help="The minimum number of repeated tokens which will count as a duplication." )
(options, args) = parser.parse_args()

executeCPD( options.input, options.output, options.minimumTokens, options.debug )