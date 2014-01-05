#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#######################################################################
#
#    MyMetrix for VU+
#    Coded by iMaxxx (c) 2013
#    Support: www.vuplus-support.com
#
#
#  This plugin is licensed under the Creative Commons
#  Attribution-NonCommercial-ShareAlike 3.0 Unported License.
#  To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/
#  or send a letter to Creative Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.
#
#
#
#  This plugin is NOT free software. It is open source, you are allowed to
#  modify it (if you keep the license), but it may not be commercially
#  distributed other than under the conditions noted above.
#
#
#######################################################################

#import xml.etree.cElementTree
from Tools.Import import my_import
from Screens.Screen import Screen
from Components.Sources.Source import Source, ObsoleteSource
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from twisted.web.client import downloadPage
from Screens.Console import Console
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, ConfigYesNo, ConfigSequence, ConfigSubsection, ConfigSelectionNumber, getConfigListEntry, ConfigSelection, ConfigNumber, ConfigText, ConfigInteger
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Language import language
from os import environ, listdir, remove, rename, system
from skin import parseColor
import e2info
from Components.Pixmap import Pixmap
from Components.Label import Label
import gettext
from enigma import ePicLoad
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import os
import shutil
import traceback
import md5
import metrixDefaults
import time
from streaminghttp import register_openers
from encode import multipart_encode
import urllib, urllib2
from xml.dom.minidom import parseString
import metrixCore
import ConfigParser



#############################################################


def getHexColor(rgbColor, alpha = 0):
	return "#" + getHex(alpha) + getHex(rgbColor[0]) + getHex(rgbColor[1]) + getHex(rgbColor[2])

def getHex(number):
	return str(hex(int(number))).replace("0x","").zfill(2)

def skinPartIsCompatible(dom):
	isvalid = True
	try:
		for widget in dom.getElementsByTagName('widget'):
			isvalid = True
			#get_attr = widget.attrib.get
			renderer = None
			try:
				renderer = str(widget.getAttributeNode('render').nodeValue)
			except:
				pass
			if not renderer is None:
				try:
					renderer_class = my_import('.'.join(("Components", "Renderer", renderer))).__dict__.get(renderer)
					#try:
					for convert in dom.getElementsByTagName('convert'):
						ctype = None
						try:
							ctype = str(convert.getAttributeNode('type').nodeValue)
						except:
							pass
						if not ctype is None:
							try:
								converter_class = my_import('.'.join(("Components", "Converter", ctype))).__dict__.get(ctype)
							except Exception, e:
								isvalid = False 
								log("Missing converter '"+ctype+"'",solution="MetrixGSP")
								break
					
				except Exception, e:
					log("Missing renderer '"+renderer+"'",solution="MetrixGSP")
					isvalid = False
			
			if isvalid == False:
				dom.removeChild(widget)	
	except:
		pass
	return dom



def downloadFile(webURL,localPath = '/tmp/metrixPreview.png',searchpattern="",replacepattern="",forceOverwrite = True):
	#print localPath
	try:
		if "http" in webURL:
			webFile = urllib2.urlopen(webURL)
			if searchpattern == "":
				if not os.path.isfile(localPath) or forceOverwrite:
					localFile = open(localPath, 'w')
					localFile.write(webFile.read())
			else:
				localFile = open(localPath, 'w')
				for line in webFile:
						localFile.write(line.replace(searchpattern,replacepattern))
			webFile.close()
			localFile.close()
			return localPath
		else:
			return None
	except Exception, e:
		return None
		log("Error downloading file!",e)
		
def webPixmap(url,image_id="openStoreImage",params={}):
	uri = ""
	try:
		urlparams = urllib.urlencode(params)
		if urlparams != "":
			requesturl = url+'&'+urlparams
		else:
			requesturl = url
		uri = downloadFile(requesturl,'/tmp/'+image_id+".png")
	except Exception, e:
		log("Error downloading pixmap",e)
	if uri is None:
		uri = metrixDefaults.PLUGIN_DIR + "images/missing.png"
	return uri

def log(errormessage,e=None,solution="MyMetrix"):
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	# Log file output
	from time import gmtime, strftime
	time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
	err_str = "["+solution+"] " + time + ' -- ' + errormessage
	
	print OKBLUE+ err_str+ENDC
	if config.plugins.MyMetrix.logLevel.value in ["on","debug"]:
		if e:
			print WARNING+"["+solution+"] " + time + ' -- ' + "/*-Exception------------------------"
			print "["+solution+"] " + time + ' -- ' + str(e)+ENDC
			if config.plugins.MyMetrix.logLevel.value == "debug":
				print FAIL+"["+solution+"] " + time + ' -- ' + "---------------TRACE----------------"
				traceback.print_exc()	
			print "["+solution+"] " + time + ' -- ' + "---Exception----------------------*/"+ENDC
			
		f = None
		try:
			f = open('/tmp/metrixerror.log', 'a')
			f.write(err_str + '\n')
		except Exception, e:
			print "[skinError] Can not write skin file: " + str(e)
		finally:
			if f:
				f.close()
			
from threading import currentThread
from twisted.internet import reactor, defer
from twisted.python import failure
import Queue

def blockingCallOnMainThread(func, *args, **kwargs):
	"""
	  Modified version of twisted.internet.threads.blockingCallFromThread
	  which waits 30s for results and otherwise assumes the system to be shut down.
	  This is an ugly workaround for a twisted-internal deadlock.
	  Please keep the look intact in case someone comes up with a way
	  to reliably detect from the outside if twisted is currently shutting
	  down.
	"""
	def blockingCallFromThread(f, *a, **kw):
		queue = Queue.Queue()
		def _callFromThread():
			result = defer.maybeDeferred(f, *a, **kw)
			result.addBoth(queue.put)
		reactor.callFromThread(_callFromThread)

		result = None
		while True:
			try:
				result = queue.get(True, 30)
			except Queue.Empty as qe:
				if True: #not reactor.running: # reactor.running is only False AFTER shutdown, we are during.
					raise ValueError("Reactor no longer active, aborting.")
			else:
				break

		if isinstance(result, failure.Failure):
			result.raiseException()
		return result

	if currentThread().getName() == 'MainThread':
		return func(*args, **kwargs)
	else:
		return blockingCallFromThread(func, *args, **kwargs)
	reactor.wakeUp()

def callOnMainThread(func, *args, **kwargs):
	"""
	  Ensures that a method is being called on the main-thread.
	  No return value here!
	"""
	if currentThread().getName() == 'MainThread':
		#call on next mainloop interation
		reactor.callLater(0, func, *args, **kwargs)
	else:
		#call on mainthread
		reactor.callFromThread(func, *args, **kwargs)
	reactor.wakeUp()
	
def str2bool(text):
	return text.lower() in ("yes", "true", "t", "1")

def bool210(bool):
	if bool:
		return str(1)
	else:
		return str(0)

def toRGB(text):
	rgb = []
	textar = str(text.replace("[","").replace("]","")).split(",")
	rgb.append(int(textar[0]))
	rgb.append(int(textar[1]))
	rgb.append(int(textar[2]))
	return rgb
	
def getFile(filepath):
	f = open(filepath, 'r')
	content = f.read()
	f.close()
	return content

def getBrand():
	boxinfo = e2info.getInfo()
	return boxinfo['brand']

def getRestrictions():
	CONFIG_SYSTEM_DESC = "/etc/systemdescription.cfg"
	restriction = "%image::"+ metrixDefaults.getImageName() +"%"
	restriction = restriction + "%oe::"+metrixDefaults.getOEVersion()+"%"
	return restriction

def getFileDiff(oldfile,newfile):
	old_lines = set((line.strip() for line in open(oldfile, 'r+')))
	file_new = open(newfile, 'r+')
	 
	for line in file_new:
	    if line.strip() not in old_lines:
	        return line
	return ""

def checkComponents(sourceRoot,targetRoot, transferPath, filename=None, force=False):
	for file in os.listdir(sourceRoot+transferPath):
	    full_file_name = os.path.join(sourceRoot+transferPath, file)
	    if (os.path.isfile(full_file_name)):
	    	if filename is None:
	    		if not os.path.isfile(targetRoot+transferPath+file) or force:
	        		shutil.copy(full_file_name, targetRoot+transferPath)
	        else:
	        	if file == filename:
	        		if not os.path.isfile(targetRoot+transferPath+file) or force:
	        			shutil.copy(full_file_name, targetRoot+transferPath)

		