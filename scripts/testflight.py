#! /usr/bin/env python
#
# testflight.py
#
# Created by Josh Kennedy on 9/1/11.
# Copyright 2011 Deadmeta4 Software, LLC. All rights reserved.
#
# A simple script to upload a given .ipa to testflight.  Also embeds change
# history into testflight build comments.  Script currently supports Git or 
# Perforce but can be modified to support other version control systems.
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
import httplib, urllib, mimetypes
import mmap

_testFlightAPIUrl = "http://testflightapp.com/api/builds.json"
_p4Path = "/usr/local/bin/p4"


def retrievePerforceHistory( depotPath, user ):
	cmd = [ _p4Path, "-u", user, "changes" ]
	cmd.extend( [ "-m", "5" ] )				# last 5 records
	cmd.extend( [ "-t" ] )					# also show time
	cmd.extend( [ "-l" ] )					# return full change text
	cmd.extend( [ "-s", "submitted" ] )		# limit to only submitted changes
	cmd.extend( [ depotPath ] )				

	print "EXECUTING: " + " ".join( cmd )

	(stdOut, stdErr) =  subprocess.Popen( cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE ).communicate()
	return stdOut



def retrieveGitHistory( workspacePath ):
	cmd = [ "git", "log", "-n", "5" ]
    
	print "EXECUTING: " + " ".join( cmd )
    
	(stdOut, stdErr) =  subprocess.Popen( cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=workspacePath ).communicate()
	return stdOut



def uploadIpa( ipaPath=None, dsymPath=None, apiToken=None, teamToken=None, releaseNotes=None, distributionLists=None, notifiy=False ):

	if( ipaPath is None ):
		print "You must supply a full path to an IPA file as the last parameter."
		sys.exit( 1 )
        
	if( apiToken is None ):
		print "api_token is a required input"
		sys.exit( 1 )
		
	if( teamToken is None ):
		print "team_token is a required input"
		sys.exit( 1 )

	cmd = [ "curl" ]
	cmd.extend( [ "-F", buildCurlIpaFile( ipaPath ) ] )
	if( dsymPath is not None ):
		cmd.extend( [ "-F", buildCurlDsymFile( dsymPath ) ] )

	cmd.extend( [ "--form-string", buildCurlParamter( "api_token", apiToken ) ] )
	cmd.extend( [ "--form-string", buildCurlParamter( "team_token", teamToken ) ] )
	
	if( not releaseNotes is None ):
		cmd.extend( [ "--form-string", buildCurlParamter( "notes", releaseNotes ) ] )
		
	if( not distributionLists is None ):
		cmd.extend( [ "--form-string", buildCurlParamter( "distribution_lists", distributionLists ) ] )

	if( notifiy ):
		cmd.extend( [ "--form-string", buildCurlParamter( "notify", "True" ) ] )

	
	cmd.extend( [ _testFlightAPIUrl ] )
	cmd.extend( [ "-v", "--trace", "output.txt" ] ) # verbose
	
	print "EXECUTING: " + " ".join( cmd )
	subprocess.Popen( cmd ).communicate()



def buildCurlParamter( parameterName, parameterValue ):
	return parameterName + "=" + parameterValue
	
	
	
def buildCurlIpaFile( filePath ):
	return "file=@" + filePath


def buildCurlDsymFile( filePath ):
	return "dsym=@" + filePath



	
# MAIN

parser = OptionParser()
parser.add_option( "-a", "--api_token", dest="api_token", help="The API token from the testflight website." )
parser.add_option( "-t", "--team_token", dest="team_token", help="The team token from the testflight website." )
parser.add_option( "-d", "--distribution_list", dest="distribution_list", help="The name of the distribution list in testflight which should have access to this build." )
parser.add_option( "-n", "--notify", dest="notify", action="store_true", default=False, help="True if the distribution list should be notified for new builds." )
parser.add_option( "-p", "--path_in_depot", dest="path_in_depot", help="Path to subfolder in depot for which changes should be retrieve as release notes or path to git workspace" )
parser.add_option( "-b", "--build_number", dest="build_number", help="Jenkins build number" )
parser.add_option( "-u", "--user", dest="user", help="Perforce Username" )

(options, args) = parser.parse_args()


# get perforce history for depot path
releaseNotes = [ "Jenkins automated build #", str(options.build_number) ]

if( not options.path_in_depot is None ):
	releaseNotes.extend( [ "from: ", options.path_in_depot ] )
	releaseNotes.extend( [ "\n-------------------------------------------------------------------------------\n" ] )
	releaseNotes.extend( [ retrieveGitHistory( options.path_in_depot ) ] )



# send data to TestFlightApp
uploadIpa( args[0], None, options.api_token, options.team_token, " ".join( releaseNotes ), options.distribution_list, options.notify )
