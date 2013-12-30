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
from metrixTools import getHex, getHexColor,skinPartIsCompatible
from ServiceReference import ServiceReference
from os import environ, listdir, remove, rename, system
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.EpgSelection import EPGSelection
from Components.config import config, configfile, ConfigYesNo, ConfigSequence, ConfigSubsection, ConfigSelectionNumber, getConfigListEntry, ConfigSelection, ConfigNumber, ConfigText, ConfigInteger
from Components.ConfigList import ConfigListScreen
from Screens.ChannelSelection import ChannelSelection, BouquetSelector
from Screens.TimerEntry import TimerEntry
from Plugins.Plugin import PluginDescriptor
from Screens.Standby import TryQuitMainloop
from enigma import eTimer, eDVBDB,eConsoleAppContainer
from enigma import eEPGCache, eListbox, eServiceCenter, eServiceReference
from Components.Input import Input
from Components.Pixmap import Pixmap
from Components.Label import Label
from Components.config import config
from Components.UsageConfig import preferredInstantRecordPath, defaultMoviePath
from Components.EpgList import EPGList, Rect
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.ServiceList import ServiceList
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.Button import Button
from Components.config import config, ConfigClock, ConfigSubsection, ConfigInteger, ConfigSelection, ConfigText, ConfigEnableDisable, KEY_LEFT, KEY_RIGHT, KEY_0, getConfigListEntry, ConfigNumber, ConfigBoolean
from uuid import getnode as get_id
from encode import multipart_encode
from streaminghttp import register_openers
from Components.ServiceList import ServiceList
import cookielib
from xml.dom.minidom import parseString
import gettext
import MultipartPostHandler
from xml.dom.minidom import parseString, parse
import os
import urllib2
import socket
import e2info
import metrixDefaults
import metrixTools
import time
import threading
import base64
import traceback
import metrixWeatherUpdater
import shutil
import metrixCore
import metrix_SkinPartTools
import metrixCloudSync
import random
import metrix_Intro
import metrix_PackageTools
from Tools import Notifications
import metrix_UpdateAvailable
import metrix_MetrixColorsTools
import metrix_GenerateSkin
#from xml.etree.ElementTree import parse


config = metrixDefaults.loadDefaults()

def syncStart(session):
	global global_session
	global_session = session
	config.plugins.MetrixUpdater.Reboot.value = 0
	config.plugins.MetrixUpdater.UpdateAvailable.value = 0
	config.plugins.MetrixUpdater.Open.value = 0
	config.plugins.MetrixUpdater.save() 
	
	threadUpdater = threading.Thread(target=syncHourly,  args=())
	threadUpdater.daemon = True
	threadUpdater.start()	
	
	threadUpdaterGeneral = threading.Thread(target=syncGeneral,  args=())
	threadUpdaterGeneral.daemon = True
	threadUpdaterGeneral.start()	
	
	threadUpdaterDaily = threading.Thread(target=daily,  args=())
	threadUpdaterDaily.daemon = True
	threadUpdaterDaily.start()	
	
	threadActions = threading.Thread(target=syncActions,  args=())
	threadActions.daemon = True
	threadActions.start()	
	
	try:
		if config.plugins.MyMetrix.showFirstRun.value:
			metrixTools.callOnMainThread(Notifications.AddNotification,metrix_Intro.OpenScreen)
	except:
		pass
		#global_session.open(metrix_Intro.OpenScreen)
		
	
		
def syncGeneral():
	while(1):
		if metrixCore.isLoggedIn():
			try:
				prepareInfoGeneral(global_session)
			except:
				traceback.print_exc()
			try:
				postBackup()
			except:
				traceback.print_exc()
		time.sleep(30*60)

def syncHourly():
	while(1):
		try:
			metrixWeatherUpdater.GetWeather()
		except Exception, e:
			metrixTools.log("Error downloading weather!",e)
			traceback.print_exc()
		if metrixCore.isLoggedIn():
			try:
				prepareInfo(global_session)
			except:
				traceback.print_exc()
			try:
				if config.plugins.MetrixCloudSync.SyncPackages.value:
					metrix_PackageTools.syncPackages()
			except:
				traceback.print_exc()
		time.sleep(60*60)
		
def daily():
	while(1):
		metrixCore.setInfo()  # Send general info to MetrixCloud
		"""
		try:
			if config.plugins.MyMetrix.AutoUpdateSkinParts.value:
				# Auto-Update vorrübergehend außer Funktion
				pass
				#metrix_SkinPartTools.updateSkinParts()
				#if config.plugins.MetrixUpdater.UpdateAvailable.value == 1:
				#	metrixTools.callOnMainThread(Notifications.AddNotification,metrix_UpdateAvailable.OpenScreen)
		except:
			traceback.print_exc()
		try:
			if config.plugins.MyMetrix.AutoUpdate.value:
				# Auto-Update vorrübergehend außer Funktion
				pass
				#getPackageUpdates()
		except:
			traceback.print_exc()
		"""
		time.sleep(24*60*60)
		
def syncActions():
	syncinterval =1200
	while(1):
		if metrixCore.isLoggedIn():
			try:
				getActions()
				syncinterval = getInterval()
			except:
				metrixTools.log("Error getting interval")
		time.sleep(syncinterval)
		
def runAction(item_id,action,actiontype,param):
	#print "============ ACTIONPARAMS: "+param
	checkAction(item_id)
	if action == "install":
		if actiontype == "SkinPart":
			installSkinPart(param,item_id)
		elif actiontype == "MetrixColors":
			metrix_MetrixColorsTools.installMetrixColors(param)
		elif actiontype == "Package":
			installPackage(param,item_id)
		elif actiontype == "PackageURL":
			data = param.split(";")
			if len(data) == 1:
				metrix_PackageTools.installPackage(data[0],True)
			else:
				metrix_PackageTools.installPackage(data[0],True,False,data[1],data[2])
		elif actiontype == "PiconRepo":
			params = param.split(";")
			config.plugins.MyMetrix.XPiconsRepository.value = params[0]
			config.plugins.MyMetrix.XPiconsRepositoryName.value = params[1]
			config.plugins.MyMetrix.save()    
			configfile.save()
	if action == "uninstall":
		if actiontype == "Package":
			metrix_PackageTools.uninstallPackage(param)
	elif action == "generateSkin":
		generateSkin(item_id)
	elif action == "disable":
		if actiontype == "SkinPart":
			success = False
			try:
				metrix_SkinPartTools.disableSkinPart(config.plugins.MyMetrix.SkinPartPath.value + "screens/active/screen_"+param)
				postBackup()
				success = True
			except:
				pass
			try:
				metrix_SkinPartTools.disableSkinPart(config.plugins.MyMetrix.SkinPartPath.value + "widgets/active/widget_"+param)
				success = True
				postBackup()
			except:
				pass
			if success:
				showInfo(_("SkinPart successfully disabled!"))
	elif action == "enable":
		if actiontype == "SkinPart":
			success = False
			try:
				metrix_SkinPartTools.enableSkinPart(config.plugins.MyMetrix.SkinPartPath.value + "screens/active/screen_"+param)
				postBackup()
				success = True
			except:
				pass
			try:
				metrix_SkinPartTools.enableSkinPart(config.plugins.MyMetrix.SkinPartPath.value + "widgets/active/widget_"+param)
				postBackup()
				success = True
			except:
				pass
			if success:
				showInfo(_("SkinPart successfully enabled!"))
	elif action == "generateRestart":
		generateSkin(item_id)
		time.sleep(1)
		rebootGui(item_id)
	elif action == "restartGui":
		rebootGui(item_id)
	elif action == "command":
		runCommand(actiontype,param,item_id)
	checkAction(item_id)
	
			
	
def prepareInfo(session):
	try:
		statusinfo = e2info.getStatusInfo2(session)
		sync_data = []
		if config.plugins.MetrixCloudSync.SyncBoxInfo.value:
			try:
				sync_data.append(metrixCloudSync.getSyncRow("Box Info","General","inStandby","Standby status",statusinfo['inStandby'],8))	
			except:
				pass
			try:
				sync_data.append(metrixCloudSync.getSyncRow("Box Info","Current Service","currservice_name","Program",statusinfo['currservice_name'],1))
			except:
				pass
			try:
				sync_data.append(metrixCloudSync.getSyncRow("Box Info","Current Service","currservice_description","Description",statusinfo['currservice_description'],2))
			except:
				pass
			try:
				sync_data.append(metrixCloudSync.getSyncRow("Box Info","Current Service","currservice_station","Channel",statusinfo['currservice_station'],3))
			except:
				pass
			try:
				sync_data.append(metrixCloudSync.getSyncRow("Box Info","Current Service","currservice_serviceref","ID",statusinfo['currservice_serviceref'],4))
			except:
				pass
			try:
				sync_data.append(metrixCloudSync.getSyncRow("Box Info","Current Service","currservice_begin","Begin",statusinfo['currservice_begin'],5))
			except:
				pass
			try:
				sync_data.append(metrixCloudSync.getSyncRow("Box Info","Current Service","currservice_end","End",statusinfo['currservice_end'],6))
			except:
				pass
			metrixCloudSync.syncNow(sync_data)
	except:
		pass
	
	
def prepareInfoGeneral(session):
	#print "MetrixSync"
	try:
		prepareInfo(session)
	except:
		pass
	try:
		boxinfo = e2info.getInfo()
		sync_data = []
		if config.plugins.MetrixCloudSync.SyncBoxInfo.value:
			sync_data.append(metrixCloudSync.getSyncRow("Box Info","Software","mymetrix_version","MyMetrix version",metrixDefaults.VERSION,0))
			sync_data.append(metrixCloudSync.getSyncRow("Box Info","Software","image_version","Image version",metrixDefaults.getImageName(),2))
			sync_data.append(metrixCloudSync.getSyncRow("Box Info","Software","mymetrix_build","MyMetrix build",metrixDefaults.BUILD,1))
			try:
				sync_data.append(metrixCloudSync.getSyncRow("Box Info","Software","enigmaver","GUI version",boxinfo['enigmaver'],3))
			except:
				pass
			try:
				sync_data.append(metrixCloudSync.getSyncRow("Box Info","Software","imagever","Firmware version",boxinfo['imagever'],4))
			except:
				pass
			try:
				sync_data.append(metrixCloudSync.getSyncRow("Box Info","Software","kernelver","Kernel version",boxinfo['kernelver'],5))
			except:
				pass
			try:
				for item in boxinfo["ifaces"]:
					sync_data.append(metrixCloudSync.getSyncRow("Box Info","Network Interface "+item["name"],item["name"]+"dhcp","DHCP status",item["dhcp"],1))
					sync_data.append(metrixCloudSync.getSyncRow("Box Info","Network Interface "+item["name"],item["name"]+"ip","IP address",item["ip"],2))
					sync_data.append(metrixCloudSync.getSyncRow("Box Info","Network Interface "+item["name"],item["name"]+"mac","MAC address",item["mac"],3))
					sync_data.append(metrixCloudSync.getSyncRow("Box Info","Network Interface "+item["name"],item["name"]+"mask","Net mask",item["mask"],4))
					sync_data.append(metrixCloudSync.getSyncRow("Box Info","Network Interface "+item["name"],item["name"]+"gw","Gateway",item["gw"],5))
			except:
				pass
			try:
				for item in boxinfo["tuners"]:
					sync_data.append(metrixCloudSync.getSyncRow("Box Info","Tuners",item["name"],item["name"],item["type"])	)
			except:
				pass	
			try:
				for item in boxinfo["hdd"]:
					sync_data.append(metrixCloudSync.getSyncRow("Box Info","Hard disk "+item["model"],"hddcapacity","Capacity",item["capacity"],1))	
					sync_data.append(metrixCloudSync.getSyncRow("Box Info","Hard disk "+item["model"],"hddfree","Free",item["free"],2))	
			except:
				pass
			try:
				sync_data.append(metrixCloudSync.getSyncRow("Box Info","General","brand","Brand",boxinfo['brand'],2))
			except:
				pass
			try:
				sync_data.append(metrixCloudSync.getSyncRow("Box Info","General","model","Model",boxinfo['model'],3))
			except:
				pass
			try:
				sync_data.append(metrixCloudSync.getSyncRow("Box Info","General","chipset","Chipset",boxinfo['chipset'],4))
			except:
				pass
			try:
				sync_data.append(metrixCloudSync.getSyncRow("Box Info","General","mem1","Total memory",boxinfo['mem1'],5))
			except:
				pass
			try:
				sync_data.append(metrixCloudSync.getSyncRow("Box Info","General","mem2","Free memory",boxinfo['mem2'],6))
			except:
				pass
			try:
				sync_data.append(metrixCloudSync.getSyncRow("Box Info","General","uptime","Uptime",boxinfo['uptime'],7))
			except:
				pass
			metrixCloudSync.syncNow(sync_data)
	except:
		pass
	
def postBackup():
	if config.plugins.MetrixCloudSync.SyncSkinParts.value:
		postSkinParts(config.plugins.MyMetrix.SkinPartPath.value + "widgets/active/","Active")
		postSkinParts(config.plugins.MyMetrix.SkinPartPath.value + "screens/active/","Active")
		postSkinParts(config.plugins.MyMetrix.SkinPartPath.value + "widgets/inactive/","Inactive")
		postSkinParts(config.plugins.MyMetrix.SkinPartPath.value + "screens/inactive/","Inactive")
		
			
def postSkinParts(path,isActive="Active"):
	dirs = listdir( path )
	sync_data = []
	for dir in dirs:
		try:
			file = open(path+"/"+dir+"/meta.xml", "r")
			data = file.read()
			file.close()	
			dom = parseString(data)
			for design in dom.getElementsByTagName('entry'):
				id = str(design.getAttributeNode('id').nodeValue)
				name = str(design.getAttributeNode('name').nodeValue)
				type = str(design.getAttributeNode('type').nodeValue)
				sync_data.append(metrixCloudSync.getSyncRow("SkinParts",isActive,"skinpart_"+id,name + " ["+type+"]",id))
		except:
			pass
	metrixCloudSync.syncNow(sync_data)

		
	
	
def postAnonymous(keyname="status",value=""):
	try:
		url = metrixDefaults.URL_STORE_API + 'connect.statistic'
		params = {'keyname':keyname,
				'value':value}
		metrixCore.getWeb(url,True,params)
	except:
		pass

def getActions(url=metrixDefaults.URL_GET_ACTIONS):
	try:
		data = metrixCore.getWeb(url,True)
		dom = parseString(data)
		
		for entry in dom.getElementsByTagName('entry'):
			item_id = str(entry.getAttributeNode('id').nodeValue)
			action = str(entry.getAttributeNode('action').nodeValue)
			actiontype = str(entry.getAttributeNode('type').nodeValue)
			param = str(entry.getAttributeNode('param').nodeValue)
			runAction(item_id,action,actiontype,param)
	except:
		pass
			
def getInterval(url=metrixDefaults.URL_STORE_API + 'connect.activity'):
	#print "-----------------------------getting interval"
	try:
		data = metrixCore.getWeb(url,True)
		dom = parseString(data)
		for entry in dom.getElementsByTagName('entry'):
			return int(str(entry.getAttributeNode('interval').nodeValue))
	except:
		return 320
	

	
def installSkinPart(param,actionId):
	metrixTools.log("Installing skinpart: "+param)
	item_id = ""
	item_name = ""
	item_type = ""
	author = ""
	date_modified = ""
	try:
		data = metrixCore.getWeb(metrixDefaults.URL_GET_SKINPART_META_UPDATE + "&id=" + str(param),False)
		dom = parseString(data)
		for entry in dom.getElementsByTagName('entry'):
			item_id = str(entry.getAttributeNode('id').nodeValue)
			item_name = str(entry.getAttributeNode('name').nodeValue)
			item_type = str(entry.getAttributeNode('type').nodeValue)
			author = str(entry.getAttributeNode('author').nodeValue)
			image_link = str(entry.getAttributeNode('image_link').nodeValue)
			date = str(entry.getAttributeNode('date').nodeValue)
			date_modified = str(entry.getAttributeNode('date_modified').nodeValue)
			if item_type == "bundle":
				metrix_SkinPartTools.installBundle(item_id,type,author)
			else:
				metrix_SkinPartTools.installSkinPart(item_id,item_type,author,image_link)
				showInfo(item_name+" "+_("successfully installed!"))
			
	except Exception, e:
		metrixTools.log("Error installing SkinPart",e)
		traceback.print_exc()

	

def checkAction(actionId):
	if not metrixCore.getWeb(metrixDefaults.URL_STORE_API + "connect.actioncheck",True,{'id':actionId}):
		metrixTools.log("Error checking action")


#---------PACKAGES
def getPackageUpdates():
	try:
		updates_available = False
		data = metrixCore.getWeb(metrixDefaults.URL_STORE_API + "get.xml.packages&category_id=%",True)
		if not data:
			metrixTools.log("Error getting package updates")
			
			
		dom = parseString(data)
		for design in dom.getElementsByTagName('entry'):
			item_id = str(design.getAttributeNode('id').nodeValue)
			name = str(design.getAttributeNode('name').nodeValue)
			author = str(design.getAttributeNode('author').nodeValue)
			version = str(design.getAttributeNode('version').nodeValue)
			rating = str(design.getAttributeNode('rating').nodeValue)
			date = str(design.getAttributeNode('date_created').nodeValue)
			item_type = str(design.getAttributeNode('type').nodeValue)
			file_id = str(design.getAttributeNode('file_id').nodeValue)
			file_token = str(design.getAttributeNode('file_token').nodeValue)
			image_id = str(design.getAttributeNode('image_id').nodeValue)
			image_token = str(design.getAttributeNode('image_token').nodeValue)
			total_votes = str(design.getAttributeNode('total_votes').nodeValue)
			description = str(design.getAttributeNode('description').nodeValue)
			previouspackage = str(design.getAttributeNode('previouspackage').nodeValue)
			path = metrixDefaults.pathRoot()+"packages/"+item_id
			if not os.path.exists(path):
				if previouspackage != "0":
					path = metrixDefaults.pathRoot()+"packages/"+previouspackage
					if os.path.exists(path):
						metrixTools.log("Update found: "+name+" Version: "+version)
						installPackage(item_id+";"+file_id+";"+file_token,0)	
						updates_available = True
		if updates_available == True:
			getPackageUpdates()
	except:
		metrixTools.log("Error getting updates.")


def installPackage(param,actionId,isUpdate=False):
	params = param.split(";")
	packageId = params[0]
	metrixTools.log("Installing package "+packageId)
	downloadurl = metrixDefaults.URL_STORE_API + "get.xml.packagefile&file_id="+params[1]+"&token="+params[2]
	if isUpdate:
		downloadurl = metrixDefaults.URL_STORE_API + "get.xml.packagefile-update&file_id="+params[1]+"&token="+params[2]
	localPath = "/tmp/metrixPackage.ipk"
	instSuccess = metrix_PackageTools.installPackage(downloadurl,True)
	if instSuccess:
		config.plugins.MetrixUpdater.Reboot.value = 1
		config.plugins.MetrixUpdater.save()    
		configfile.save()
		path = metrixDefaults.pathRoot()+"packages/"+packageId
		if not os.path.exists(path):
			os.makedirs(path)
		showInfo(_("Package successfully installed!"))
	else:
		showInfo(_("Error installing package!"),MessageBox.TYPE_ERROR)
		metrixTools.log("Error installing package "+params[0])



def generateSkin(actionId):
	metrixTools.callOnMainThread(Notifications.AddNotification,metrix_GenerateSkin.OpenScreen, 3)

def rebootGui(actionId):
	metrixTools.log("Restarting GUI via web")
	showInfo(_("Restarting GUI!"))
	metrixTools.callOnMainThread(Notifications.AddNotification,TryQuitMainloop, 3)
	
	
def runCommand(cmd_type,param,actionId):
	metrixTools.log("Starting action via web")
	try:
		cmdStatus = metrix_PackageTools.runCommand(str(base64.b64decode(cmd_type)+" "+base64.b64decode(param)))
		if cmdStatus[0] == True:
			showInfo(_("Action successfully executed!"))
		else:
			showInfo(_("Error executing action!"),MessageBox.TYPE_ERROR)
			
	except Exception, e:
		metrixTools.log("Error on action via web",e)
	

def showInfo(text,msg_type=MessageBox.TYPE_INFO):
	try:
		metrixTools.callOnMainThread(Notifications.AddNotification,MessageBox, _(text), type=msg_type,timeout=3)
	except Exception, e:
		metrixTools.log("Error",e)

