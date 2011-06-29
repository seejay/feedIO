#!/usr/bin/python

"""
$Id: crm.py 158 2005-06-07 17:45:47Z sam $

Python wrapper classes for the CRM114 Discriminator (http://crm114.sourceforge.net/).

Requires the crm command to be installed and in your command path.

The latest version of this file can be obtained from the Elegant Chaos subversion server (user=guest, pass=guest) at:
	$URL: http://source.elegantchaos.com/projects/com/elegantchaos/libraries/python/crm.py $

This module provides a very simplified interface to crm114. It does not attempt to expose all of crm114's power, instead it
tries to hide almost all of the gory details.

To use the module, create an instance of the Classifier class, giving it a path (where to store the data files), and a list
of category strings (these are the "labels" to classify the text with).

e.g:
	c = Classifier("/path/to/my/data", ["good", "bad"])

To teach the classifier object about some text, call the learn method passing in a category (on of the ones that you provided originally),
and the text.

e.g:
	c.learn("good", "some good text")
	c.learn("bad", "some bad text")
	
To find out what the classifier things about some text, call the classify method passing in the text. The result of this
method is a pair - the first item being the category best matching the text, and the second item being the probability of the match.

e.g:
	(classification, probability) = c.classify("some text")

TODO: use proper path separator variable in the regular expression instead of assuming that it's a slash
	
"""

__version__ = "1.0.0a1"

__license__ = """
Copyright (C) 2005 Sam Deane.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

import os;
import string;

#constants

kCrmPath = "crm"

kClassificationType = "<osb unique microgroom>"
kClassificationExtension = ".css"

kLearnCommand = " '-{ learn %s ( %s ) }'"
kClassifyCommand = " '-{ isolate (:stats:); classify %s ( %s ) (:stats:); match [:stats:] (:: :best: :prob:) /Best match to file .. \(%s\/([[:graph:]]+)\\%s\) prob: ([0-9.]+)/; output /:*:best:\\t:*:prob:/ }'"


# wrapper for crm114
class Classifier:

	def __init__( self, path, categories = [] ):
		self.categories = categories
		self.path = path
		self.makeFiles()
		
	# learn the classifier what category some new text is in 
	def learn( self, category, text ):
		command = kCrmPath + ( kLearnCommand % ( kClassificationType, os.path.join( self.path, category + kClassificationExtension ) ) )

		pipe = os.popen( command, 'w' )
		pipe.write( text )
		pipe.close()
	
	# ask the classifier what category best matches some text	
	def classify( self, text ):
		path = string.replace(self.path, "/", "\\/") # need to escape path separator for the regexp matching
		command = kCrmPath + ( kClassifyCommand % (kClassificationType, self.getFileListString(), path, kClassificationExtension) )
		(fin, fout) = os.popen2( command )
		fin.write( text )
		fin.close()
		list = string.split(fout.readline())
		fout.close()
		if list == None:
			return ("", 0.0)
		else:
			category = list[0]
			probability = float(list[1])
			return (category, probability)

	# ensure that data files exist, by calling learn with an empty string
	def makeFiles( self ):
		# make directory if necessary
		if not os.path.exists( self.path ):
				os.mkdir( self.path )

		# make category files
		for category in self.categories:
			self.learn( category, "" )
			
			
	# return a list of classification files
	def getFileList( self ):
		
		# internal method to build a file path given a category
		def getFilePath( file ):
			return os.path.join( self.path, file + kClassificationExtension )
		
		# return list of all category paths
		return map( getFilePath, self.categories )
		

	# return a list of classification files as a string
	def getFileListString( self ):
		return string.join( self.getFileList(), " " )

	# perform some self tests	
	def test( self ):
   		print self.getFileList()
    		self.learn( "good", "this is a test" )
    		self.learn( "bad", "this is very bad" )
    		print "class was: %s, prob was:%f" % ( self.classify( "this is a test" ) )
		
		
if __name__ == "__main__":
	# perform a simple test
	c = Classifier( "test/data", [ "good", "bad" ] )
 	c.test()
