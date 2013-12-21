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

import xml.etree.cElementTree
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
from Components.Pixmap import Pixmap
from Components.Label import Label
import gettext
from enigma import ePicLoad
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import os
import traceback
import md5
import metrixDefaults
import time
from streaminghttp import register_openers
from encode import multipart_encode
import urllib2
from xml.dom.minidom import parseString
import metrixTools
import shutil
import metrixCore
import metrixConnector
import datetime
import subprocess
import metrixCloudSync
from enigma import eTimer, eDVBDB,eConsoleAppContainer


#############################################################

def syncPackages():
	try:
		sync_data = []
		cmdStatus = runCommand("opkg list-installed enigma2-p* > /tmp/packages.log")
		f = open('/tmp/packages.log')
		lines = f.readlines()
		f.close()
		for package in lines:
			infos = package.split(" - ")
			sync_data.append(metrixCloudSync.getSyncRow("Packages","Packages",infos[0],infos[0],infos[1].replace("\n","")))
		metrixCloudSync.syncNow(sync_data)
	except:
		pass
	
def uninstallPackage(packageName):
	metrixTools.log("Uninstalling package "+packageName,None,"OpenStore")
	cmdStatus = runCommand("opkg remove '"+packageName+"'")
	if cmdStatus[0] == True: #Command without errorcode
		metrixConnector.showInfo(cmdStatus[1])
	else:
		metrixConnector.showInfo(_("Error uninstalling Package!"),MessageBox.TYPE_ERROR)
	syncPackages()
	
def installPackage(url,force=False,silent=False):
	metrixTools.log("Installing package "+url,None,"OpenStore")
	if force:
		cmdStatus = runCommand("opkg install --force-overwrite '"+url+"'")
	else:
		cmdStatus = runCommand("opkg install '"+url+"'")
	if cmdStatus[0] == True:
		#

		config.plugins.MetrixUpdater.Reboot.value = 1
		config.plugins.MetrixUpdater.save()    
		configfile.save()
		if not silent:
			metrixConnector.showInfo(_("Package successfully installed!"))
		return True
	else:
		if not silent:
			metrixConnector.showInfo(_("Error installing Package!"),MessageBox.TYPE_ERROR)
		return False
	syncPackages()
	
def runCommand(command):
	try:
		process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		process.wait()
		stdout, stderr = process.communicate(str.encode('utf-8'))
		if(stderr!=""):
			return [False,stderr]
		else:
			return [True,stdout]
	except Exception, e:
		metrixTools.log("Error running command",e,"OpenStore")
		return 0
	
	