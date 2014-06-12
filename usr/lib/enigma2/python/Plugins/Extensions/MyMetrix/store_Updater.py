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
from Screens.Screen import Screen
from Components.Label import Label
from Components.ActionMap import ActionMap
import threading
from Tools import Notifications
from Screens.Standby import TryQuitMainloop
from Components.ConfigList import ConfigListScreen
import gettext
import metrixDefaults
import metrixTools
import metrix_PackageTools
from os import environ, listdir, remove, rename, system
from skin import parseColor
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
from Tools.Directories import fileExists

#############################################################

config = metrixDefaults.loadDefaults()







def getUpdatedFiles():
	metrixTools.log("Searching update for build "+metrixDefaults.BUILD+ "...")
	data = metrixCore.getWeb(metrixDefaults.URL_GET_UPDATE_FILES,True)
	dom = parseString(data)
	for update in dom.getElementsByTagName('update'):
		build = str(update.getAttributeNode('build').nodeValue)
		metrixTools.log("Lastest release: build "+build)
		if build > metrixDefaults.BUILD:
			for files in update.getElementsByTagName('file'):
				update = False
				path = str(files.getAttributeNode('path').nodeValue)
				url = str(files.getAttributeNode('url').nodeValue)
				date_modified = int(files.getAttributeNode('date_modified').nodeValue)
				if not fileExists(path):
					update = True
				else:
					if int(date_modified) > int(os.path.getmtime(path)):
						update = True
				if update:
					metrixTools.downloadFile(url,path,forceOverwrite=True)
					config.plugins.MetrixUpdater.RebootRequired.value = True
					config.plugins.MetrixUpdater.UpdatePopup_Self.value = True
	metrixTools.downloadFile(metrixDefaults.URL_IMAGE_LOADING,metrixDefaults.URI_IMAGE_LOADING,forceOverwrite = True)
	metrixTools.downloadFile(metrixDefaults.URL_IMAGE_SPONSOR,metrixDefaults.URI_IMAGE_SPONSOR,forceOverwrite = True)


def getUpdatedPackages():
		menu = []
		try:
			params = {'restriction-oe':metrixTools.getOERestriction(),
					'restriction-image':metrixTools.getImageRestriction(),
					  'category_id':"%"}
			data = metrixCore.getWeb(metrixDefaults.URL_GET_PACKAGES,True,params)
			if "<exception status=""error""" in data:
				raise Exception("Error loading data")
			dom = parseString(data)
			for package in dom.getElementsByTagName('entry'):
				isinstalled = False
				updateavailable = False
				item_id = str(package.getAttributeNode('id').nodeValue)
				file_link = str(package.getAttributeNode('file_link').nodeValue)
				build = int(package.getAttributeNode('build').nodeValue)
				localbuild = int(metrixDefaults.cfg(metrixDefaults.CONFIG_INSTALLEDPACKAGES,item_id,"build","int"))
				# add when not only updates or (only updates and online build is higher)
				if (not localbuild == metrixDefaults.NONEINT):
					isinstalled = True
				if build > localbuild:
					updateavailable = True
					metrix_PackageTools.installPackage(file_link,True,True,item_id,build)
					config.plugins.MetrixUpdater.RebootRequired.value = True
		except Exception, e:
			metrixTools.log('Error getting packages via web',e)





