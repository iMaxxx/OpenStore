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
from xml.dom.minidom import parseString, parse
import metrixTools
import shutil
import metrixCore
import metrixConnector
import datetime
import metrix_UpdateAvailable
from Tools import Notifications
import ConfigParser
import e2info



#############################################################

	
def downloadSkinPartRenderer(id):
	url = metrixDefaults.URL_GET_SKINPART_RENDERER + "&id="+id
	downloadAdditionalFiles(url,"/usr/lib/enigma2/python/Components/Renderer/","","",False)
	
def downloadSkinPartConverter(id):
	url = metrixDefaults.URL_GET_SKINPART_RENDERER + "&id="+id
	downloadAdditionalFiles(url,"/usr/lib/enigma2/python/Components/Converter/","","",False)
	
def downloadSkinPartImages(id,path):
	url = metrixDefaults.URL_GET_SKINPART_IMAGE + "&width=550&id="+id
	return downloadAdditionalFiles(url,path + "images/")

def downloadAdditionalFiles(url,target_path,searchpattern="",replacepattern="",forceOverwrite = True):
	print url
	negate = config.plugins.MyMetrix.Color.SkinPartImagesNegate.value
	greyscale = config.plugins.MyMetrix.Color.SkinPartImagesGreyscale.value
	depth = config.plugins.MyMetrix.Color.SkinPartImagesDepth.value
	
	try:
		data = metrixCore.getWeb(url,True)
		#print(data)
		
		dom = parseString(data)
		
		for design in dom.getElementsByTagName('entry'):
			url = str(design.getAttributeNode('url').nodeValue)+"&negate="+metrixTools.bool210(negate)+"&greyscale="+metrixTools.bool210(greyscale)+"&depth="+depth
			file_name = target_path+url.split('file=')[-1]
			file_name = file_name.split('&negate=')[0]
			if not os.path.exists(target_path):
				os.makedirs(target_path)
			print url+" targ: "+target_path
			if metrixTools.downloadFile(url,file_name,searchpattern,replacepattern,forceOverwrite) == None:
				return False
				metrixTools.log("Error downloading file!")
		return True
	except Exception, e:
		metrixTools.log("No additional files available!",e)
		return False
	




def installSkinPart(id,sp_type,author="",image_link="",date_modified="",isActive=True,isUpdate=False):
	downloadurl = metrixDefaults.URL_GET_SKINPART_XML + "&id="
	downloadmetaurl = metrixDefaults.URL_GET_SKINPART_META + "&id="
	if isUpdate:
		downloadmetaurl = metrixDefaults.URL_GET_SKINPART_META_UPDATE + "&id="
	
	path = config.plugins.MyMetrix.SkinPartPath.value +sp_type+"s/inactive/"+sp_type+"_"+str(id)+"/"
	if not os.path.exists(path):
		os.makedirs(path)
	datapath = metrixTools.downloadFile(downloadurl + str(id)+"&author="+author, path+"data.xml")
	metapath = metrixTools.downloadFile(downloadmetaurl + str(id)+"&author="+author, path +"meta.xml")
	imagepath = metrixTools.downloadFile(image_link+"&width=550", path +"preview.png")
	downloadSkinPartRenderer(id)
	downloadSkinPartConverter(id)
	downloadSkinPartImages(id,path)
	
	if isActive:
		enableSkinPart(path)

	
def installBundle(id,type="",author=""):
	downloadurl = metrixDefaults.URL_GET_SKINPART_BUNDLE + "&id="+id
	skinparts = str(metrixCore.getWeb(downloadurl,True,{"author":author})).split(";")
	for skinpart in skinparts:
		
		try:
			downloadmetaurl = metrixDefaults.URL_GET_SKINPART_META_UPDATE + "&id="+skinpart
			metafile = metrixCore.getWeb(downloadmetaurl,True)
			dom = parseString(metafile)
			for design in dom.getElementsByTagName('entry'):
				id = str(design.getAttributeNode('id').nodeValue)
				name = str(design.getAttributeNode('name').nodeValue)
				type = str(design.getAttributeNode('type').nodeValue)
				author = str(design.getAttributeNode('author').nodeValue)
				image_link = str(design.getAttributeNode('image_link').nodeValue)
				installSkinPart(skinpart,type,author,image_link)
		except Exception, e:
			metrixTools.log("Error getting SkinParts",e)
	
	
def enableSkinPart(file):
	if "/inactive/" in file:
		if not os.path.exists(config.plugins.MyMetrix.SkinPartPath.value + "widgets/active"):
			os.makedirs(config.plugins.MyMetrix.SkinPartPath.value + "widgets/active")
		if not os.path.exists(config.plugins.MyMetrix.SkinPartPath.value + "screens/active"):
			os.makedirs(config.plugins.MyMetrix.SkinPartPath.value + "screens/active")
		if os.path.exists(file.replace("/inactive","/active")):
			shutil.rmtree(file.replace("/inactive","/active"),True)
		shutil.move(file,file.replace("/inactive","/active"))
	
def disableSkinPart(file):
	if "/active/" in file:
		if not os.path.exists(config.plugins.MyMetrix.SkinPartPath.value + "widgets/inactive"):
			os.makedirs(config.plugins.MyMetrix.SkinPartPath.value + "widgets/inactive")
		if not os.path.exists(config.plugins.MyMetrix.SkinPartPath.value + "screens/inactive"):
			os.makedirs(config.plugins.MyMetrix.SkinPartPath.value + "screens/inactive")
		if os.path.exists(file.replace("/active","/inactive")):
			shutil.rmtree(file.replace("/active","/inactive"),True)
		shutil.move(file,file.replace("/active","/inactive"))
	

def getSkinParts(path,isactive=""):
	dirs = listdir( path )
	for dir in dirs:
		try:
			#print dir
			file = open(path+"/"+dir+"/meta.xml", "r")
			data = file.read()
			file.close()	
			dom = parseString(data)
			for design in dom.getElementsByTagName('entry'):
				id = str(design.getAttributeNode('id').nodeValue)
				name = str(design.getAttributeNode('name').nodeValue)
				author = str(design.getAttributeNode('author').nodeValue)
				version = str(design.getAttributeNode('version').nodeValue)
				description = str(design.getAttributeNode('description').nodeValue)
				date = str(design.getAttributeNode('date').nodeValue)
				try:
					date_modified = str(design.getAttributeNode('date_modified').nodeValue)
				except:
					date_modified = date
				type = str(design.getAttributeNode('type').nodeValue)
				version = str(design.getAttributeNode('version').nodeValue)
				
		except:
			pass
		
def updateSkinParts():
	checkSkinPartUpdates(config.plugins.MyMetrix.SkinPartPath.value + "screens/active/")
	checkSkinPartUpdates(config.plugins.MyMetrix.SkinPartPath.value + "widgets/active/")
	checkSkinPartUpdates(config.plugins.MyMetrix.SkinPartPath.value + "screens/inactive/",False)
	checkSkinPartUpdates(config.plugins.MyMetrix.SkinPartPath.value + "widgets/inactive/",False)
		
def checkSkinPartUpdates(path,isActive=True):
	dirs = listdir( path )
	for dir in dirs:
		try:
			#print dir
			file = open(path+"/"+dir+"/meta.xml", "r")
			data = file.read()
			file.close()	
			dom = parseString(data)
			for design in dom.getElementsByTagName('entry'):
				id = str(design.getAttributeNode('id').nodeValue)
				name = str(design.getAttributeNode('name').nodeValue)
				type = str(design.getAttributeNode('type').nodeValue)
				author = str(design.getAttributeNode('author').nodeValue)
				description = str(design.getAttributeNode('description').nodeValue)
				date = str(design.getAttributeNode('date').nodeValue)
				version = str(design.getAttributeNode('version').nodeValue)
				image_link = str(design.getAttributeNode('image_link').nodeValue)
				try:
					date_modified = str(design.getAttributeNode('date_modified').nodeValue)
				except:
					date_modified = date
				if isUpdateAvailable(id,date_modified,version):
					installSkinPart(id,type,author,image_link,date_modified,isActive,True)
					metrixConnector.showInfo(name+_(" successfully updated!"))
					config.plugins.MetrixUpdater.UpdateAvailable.value = 1
					config.plugins.MetrixUpdater.save()    
					
		except:
			pass
		
		
		


def isUpdateAvailable(id,local_data_modified,local_version):
	try:
		downloadmetaurl = metrixDefaults.URL_GET_SKINPART_META_UPDATE + "&id="+id
		metafile = metrixCore.getWeb(downloadmetaurl,True)
		dom = parseString(metafile)
		store_date_modified = ""
		for design in dom.getElementsByTagName('entry'):
			try:
				store_date_modified = str(design.getAttributeNode('date_modified').nodeValue)
			except:
				store_date_modified = local_data_modified
			version = str(design.getAttributeNode('version').nodeValue)
		if time.strptime(local_data_modified,"%Y-%m-%d") < time.strptime(store_date_modified,"%Y-%m-%d") and not local_version == version:
			print "--------------------------======================UA"
			return True
		else:
			return False
	except Exception, e:
		return False
		metrixTools.log("Error checking SkinPart updates!",e)
		traceback.print_exc()
		
		
def parseSkinPart(path,xmlfile="data.xml",configfile="config.cfg",screenname="InfoBar",isScreen=True):
	xml = ""
	try:
		raw_xml = metrixTools.getFile(path+"/"+xmlfile)
		raw_xml = replaceGlobalVariables(raw_xml)
		if isScreen:
			raw_xml = raw_xml.replace("%SCREENNAME%",screenname)
		#Read config file
		skinpartconfig = ConfigParser.RawConfigParser()
		skinpartconfig.read(path+"/"+configfile)
		tempxml = parseString(raw_xml)
		
		raw_xml = raw_xml.replace('SKINPART/', path + "/images/")
		vars = {}
		try:
			for item in skinpartconfig.items("variable"):
				raw_xml = raw_xml.replace("%"+item[0]+"%",item[1])
			
				vars[item[0]] = item[1]
		except ConfigParser.NoSectionError:
			for var in tempxml.getElementsByTagName('variable'):
				if str(var.getAttributeNode('type').nodeValue) != "static":
					variable = str(var.getAttributeNode('name').nodeValue)
					value = str(var.getAttributeNode('value').nodeValue)
					raw_xml = raw_xml.replace("%"+variable+"%",value)
					vars[variable] = value
		for var in tempxml.getElementsByTagName('variable'):
			if str(var.getAttributeNode('type').nodeValue) == "static":
				variable = str(var.getAttributeNode('name').nodeValue)
				value = str(var.getAttributeNode('value').nodeValue)
				raw_xml = raw_xml.replace("%"+variable+"%",value)
				vars[variable] = value
		
		
		### Parse XML
		xml = parseString(raw_xml)	
		try:
			skinPartNode = xml.getElementsByTagName('screen')[0]
		except:
			skinPartNode = xml.getElementsByTagName('skinpartwidget')[0]
			skinPartNode.setAttribute('screenname',getTargetScreens(skinpartconfig,skinPartNode.getAttribute('screenname')))


		for ifNode in skinPartNode.getElementsByTagName('if'):
			variable = str(ifNode.getAttributeNode('variable').nodeValue)
			value = str(ifNode.getAttributeNode('value').nodeValue)
			if value == vars[variable]:
				for child in ifNode.childNodes:
					newchild = child.cloneNode(True)
					skinPartNode.appendChild(newchild)
			skinPartNode.removeChild(ifNode)
		for ifNode in skinPartNode.getElementsByTagName('ifnot'):
			variable = str(ifNode.getAttributeNode('variable').nodeValue)
			value = str(ifNode.getAttributeNode('value').nodeValue)
			if value != vars[variable]:
				for child in ifNode.childNodes:
					newchild = child.cloneNode(True)
					skinPartNode.appendChild(newchild)
			skinPartNode.removeChild(ifNode)
		
		
		for varNode in skinPartNode.getElementsByTagName('variable'):
			skinPartNode.removeChild(varNode)
			
		## RELATIVE POSITIONING SETTINGS	
		for node in skinPartNode.childNodes:
			try:
				position = node.getAttribute('position').split(",")
				x = int(position[0]) + skinpartconfig.getint("rel_position","posx")
				y = int(position[1]) + skinpartconfig.getint("rel_position","posy")
				node.setAttribute('position',str(x)+","+str(y))
			except:
				pass
	
	except Exception, e:
		metrixTools.log("Error parsing SkinPart!",e)
		skinPartNode = None
	#print skinPartNode.toxml()
	
	
	return skinPartNode



def widgetActive(path,xmlfile="data.xml",configfile="config.cfg",screenname="InfoBar"):
	xml = ""
	print "parsing: "+path
	try:
		raw_xml = metrixTools.getFile(path+"/"+xmlfile)
		#Read config file
		skinpartconfig = ConfigParser.RawConfigParser()
		skinpartconfig.read(path+"/"+configfile)
		
		try:
			target = skinpartconfig.get("screen",screenname.lower())
			if target == "" or target == None:
				skinPartNode = False
		except Exception, e:
			metrixTools.log("No config.cfg found in "+path)	
	except Exception, e:
		metrixTools.log("Error parsing SkinPart!",e)
		skinPartNode = None
	return True
	
	
	return skinPartNode

def replaceGlobalVariables(string):
	boxinfo = e2info.getInfo()
	string = string.replace("%GLOBAL:BRAND%",boxinfo['brand'])
	string = string.replace("%GLOBAL:IMAGE%",metrixDefaults.getImageName())
	string = string.replace("%GLOBAL:MODEL%",boxinfo['model'])
	string = string.replace("%GLOBAL:NUMTUNERS%",str(len(boxinfo['tuners'])))
	return string
	
	
def getTargetScreens(skinpartconfig,targetscreens):
	### Setting target screens
	screens = ""
	try:
		for item in skinpartconfig.items("screen"):
			if item[1] != "":
				screens += item[1]+","
	except ConfigParser.NoSectionError:
		for name in targetscreens.split(","):
			if name == "InfoBar" or name == "SecondInfoBar":
				screens += name + ","
	#return "InfoBar,"
	return screens
		
def writeSkinFile(skindom):
	file = open(metrixDefaults.SKIN_DIR+"skin.xml","wb")
	skindom.writexml(file)
	file.close()
	
	