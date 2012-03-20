#! /usr/bin/env python
#
# kif.py
#
# Created by Josh Kennedy on 9/16/11.
# Copyright 2011 Deadmeta4 Software, LLC. All rights reserved.
#
# A script to compile a KIF enabled target and then kick-off WaxSim to execute the KIF tests
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

_waxsimAppPath = "/Applications/waxsim"

def shutdownAllSimulatorInstances():
	cmd = [ "killall", "\"iPhone Simulator\"" ]
	print "Shutting down all iOS Simulator instances: " + " ".join( cmd )
	subprocess.Popen( cmd ).communicate()
	
	
	
def compileUITestsTarget( projectPath=None, target=None, tempProductsFolderPath=None):

	if( projectPath is None ):
		print "ERROR: The projectPath parameter is required"
		sys.exit( 1 )

	if( target is None ):
		print "ERROR: The target parameter is required"
		sys.exit( 1 )

	cmd = [ "xcrun" ]
	cmd.extend( [ "-sdk", "iphonesimulator" ] )
	cmd.extend( [ "xcodebuild" ] )
	cmd.extend( [ "-target", target ] )
	cmd.extend( [ "-configuration", "Debug" ] )
	cmd.extend( [ "-sdk", "iphonesimulator" ] )
	
	if( not tempProductsFolderPath is None ):
		cmd.extend( [ "BUILD_DIR=" + os.path.abspath(tempProductsFolderPath) ] )

	cmd.extend( [ "clean", "build" ] )

	print "EXECUTING BUILD: " + " ".join( cmd )
	subprocess.Popen( cmd, cwd=projectPath).communicate()



def executeWaxSim( device=None, appPath=None, outputFolderPath=None ):

	if( device is None ):
		print "ERROR: The device parameter is required"
		sys.exit( 1 )

	if( appPath is None ):
		print "ERROR: The appPath parameter is required"
		sys.exit( 1 )
		
	if( outputFolderPath is None ):
		print "ERROR: The outputFolderPath parameter is required"
		sys.exit( 1 )
		
	if not os.path.exists( outputFolderPath ):
		os.makedirs( outputFolderPath )
	
	stdOut = codecs.open( os.path.join( os.path.abspath(outputFolderPath), "std.out" ), encoding='UTF-8', mode='w+')
	stdErr = codecs.open( os.path.join( os.path.abspath(outputFolderPath), "std.err" ), encoding='UTF-8', mode='w+')

	cmd = [ _waxsimAppPath ]
	cmd.extend( [ "-f", "iphone" ] )
	cmd.extend( [ appPath ] )
	
	print "STARTING SIMULATOR: " + " ".join( cmd )
	subprocess.Popen( cmd, stderr=stdErr, stdout=stdOut ).communicate()
	
	stdOut.close()
	stdErr.close()
	
	
	
def determineIfPassedOrFailed( outputFolderPath ):

	for line in open( os.path.join( os.path.abspath(outputFolderPath), "std.err" ) ):
		if "TESTING FINISHED: 0 failures" in line:
			return 0

	return 1



def locateAppBundleInBuildDirectory( appName, buildDirectory ):
	for root, dirs, files in os.walk( buildDirectory ):
		for dir in dirs:
			if( dir == appName ):
				return os.path.join( root, dir )
	return None



# MAIN

parser = OptionParser()
parser.add_option( "-p", "--projectPath", dest="projectPath", help="Path to XCode project root" )
parser.add_option( "-t", "--target", dest="target", help="UI Automation tests target in XCode project" )
parser.add_option( "-o", "--outputFolderPath", dest="outputFolderPath", help="Path to a file (will be created) to output the simulator console" )
parser.add_option( "-i", "--tempProductsFolderPath", dest="tempProductsFolderPath", help="Path to a folder where compile products will be left" )
parser.add_option( "-a", "--appName", dest="appName", help="Name of the app bundle" )

(options, args) = parser.parse_args()

shutdownAllSimulatorInstances()
compileUITestsTarget( options.projectPath, options.target, options.tempProductsFolderPath ) 

appPath = locateAppBundleInBuildDirectory( options.appName, options.tempProductsFolderPath )
if( appPath is None ):
	print "FAILED TO LOCATE THE COMPILE APP NAMED '" + options.appName + "' IN FOLDER: " + options.tempProductsFolderPath
	sys.exit(1)
	
executeWaxSim( "iphone", appPath, options.outputFolderPath )
sys.exit( determineIfPassedOrFailed( options.outputFolderPath ) )
