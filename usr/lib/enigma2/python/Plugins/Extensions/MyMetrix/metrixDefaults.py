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

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from twisted.web.client import downloadPage
from Screens.Console import Console
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, ConfigYesNo, ConfigSequence, ConfigSubsection, ConfigSelectionNumber, getConfigListEntry, ConfigSelection, ConfigNumber, ConfigText, ConfigInteger, ConfigBoolean
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Language import language
from os import environ, listdir, remove, rename, system
from skin import parseColor
from Components.Pixmap import Pixmap
from Components.Label import Label
import urllib
import gettext
from enigma import ePicLoad
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import time
import e2info
import os
import sys
import ConfigParser


#############################################################
VERSION = "2.1alpha"
BUILD = '131021'
PLUGIN_DIR = "/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/"
SKIN_DIR = "/usr/share/enigma2/MetrixHD/"
TEMPLATES_DIR = PLUGIN_DIR + "skintemplates/"


URL_STORE_API = "http://api.open-store.net/?q="
#URL_STORE_API = "http://connect.mymetrix.de/store/api/?q="
URL_STORE = "http://open-store.net"
URL_GET_SUITES = URL_STORE_API + 'get.xml.suites' #returns a list of suites containing skinparts
URL_GET_SCREENS = URL_STORE_API + 'get.xml.screennames'	#returns a list of used screenname for skinparts
URL_GET_SKINPARTS = URL_STORE_API + 'get.xml.skinparts' #returns skinparts list
URL_GET_SKINPART_BUNDLE = URL_STORE_API + 'get.xml.skinpartbundle' #returns list of skinpart ids
URL_GET_SKINPART_XML = URL_STORE_API + 'get.xml.skinpartxml' #returns skinparts xml data
URL_GET_SKINPART_META_UPDATE = URL_STORE_API + "get.xml.skinpartmeta-update" # returns skinparts meta info
URL_GET_SKINPART_IMAGE = URL_STORE_API + "v2.get.xml.files&type=5" # returns skinpart image &width=xxx in pixels required and id=xxx
URL_GET_SKINPART_RENDERER = URL_STORE_API + "v2.get.xml.files&type=7" # returns skinpart renderer; required and id=xxx
URL_GET_SKINPART_CONVERTER = URL_STORE_API + "v2.get.xml.files&type=8" # returns skinpart converter; required and id=xxx

URL_GET_SKINPART_META = URL_STORE_API + 'get.xml.skinpartmeta' #returns skinparts meta info and increases count for dl statistic
URL_GET_SKINPARTS_COUNT = URL_STORE_API + 'get.xml.skinparts_count' #returns amount of skinparts
URL_GET_METRIXCOLORS = URL_STORE_API + "get.xml.designs" #returns a list of metrixcolors
URL_GET_METRIXCOLORS_PREVIEW = URL_STORE_API + "get.pngresizedColors" #returns the metrixcolors preview image
URL_GET_FILES = URL_STORE_API + "v2.get.xml.files" #returns list of file urls
URL_GET_PACKAGES = URL_STORE_API + "v2.get.xml.packages" # returns a list of packages
URL_GET_CATEGORIES = URL_STORE_API + "get.xml.categories" # returns a list of categories
URL_GET_ACTIONS = URL_STORE_API + "connect.actions" # returns a list of actions push from web service triggered by user

URI_IMAGE_LOADING = PLUGIN_DIR + "images/loading.png"

CONFIG_SYSTEM_DESC = "/etc/systemdescription.cfg"
CONFIG_PROFESSIONAL = PLUGIN_DIR + "metrixProfessional.cfg"
CONFIG_INSTALLEDPACKAGES = PLUGIN_DIR + "installedPackages.cfg"

NONEINT = 999999

COLOR_INSTALLED = 0x0076CC1E
COLOR_UPDATE_AVAILABLE = 0x00FA8004

BASIC_COLORS = [
				("#00F0A30A", _("Amber")),
				("#00ffffff", _("White")),
				("#00825A2C", _("Brown")),
				("#000050EF", _("Cobalt")),
				("#00911d10", _("Crimson")),
				("#001BA1E2", _("Cyan")),
				("#00a61d4d", _("Magenta")),
				("#00A4C400", _("Lime")),
				("#006A00FF", _("Indigo")),
				("#0070ad11", _("Green")),
				("#00008A00", _("Emerald")),
				("#0076608A", _("Mauve")),
				("#006D8764", _("Olive")),
				("#00c3461b", _("Orange")),
				("#00F472D0", _("Pink")),
				("#00E51400", _("Red")),
				("#007A3B3F", _("Sienna")),
				("#00647687", _("Steel")),
				("#00149baf", _("Teal")),
				("#006c0aab", _("Violet")),
				("#00bf9217", _("Yellow"))
			]
class ConfigMetrixBarColors(ConfigSelection):
	def __init__(self, default = "#00149baf"):
		ConfigSelection.__init__(self, default=default, choices = BASIC_COLORS)
		
class ConfigMetrixColors(ConfigSelection):
	def __init__(self, default = "#00000000"):
		ConfigSelection.__init__(self, default=default, choices = BASIC_COLORS+[
				("CUSTOM", _("CUSTOM")),													
				("#00000000", _("Black")),
				("#00111111", _("PreBlack")),
				("#00444444", _("Darkgrey")),
				("#00bbbbbb", _("Lightgrey")),
				("#00999999", _("Grey")),
				("#006f0000", _("Darkred")),
				("#00295c00", _("Darkgreen")),
				("#006b3500", _("Darkbrown")),
				("#00446b00", _("Darklime")),
				("#00006b5b", _("Darkteal")),
				("#00004c6b", _("Darkcyan")),
				("#0000236b", _("Darkcobalt")),
				("#0030006b", _("Darkpurple")),
				("#006b003f", _("Darkmagenta")),
				("#0065006b", _("Darkpink"))])
		
def pathRoot():
	return PLUGIN_DIR

def loadDefaults():	
	
	
	
	
	
	config.plugins.MyMetrix = ConfigSubsection()
	config.plugins.MyMetrix.Color = ConfigSubsection()
	config.plugins.MetrixWeather = ConfigSubsection()
	config.plugins.MetrixUpdater = ConfigSubsection()
	config.plugins.MyMetrix.Store = ConfigSubsection()
	config.plugins.MetrixConnect = ConfigSubsection()
	config.plugins.MetrixCloudSync = ConfigSubsection()
	
	config.plugins.MyMetrix.image = ConfigSelection(default=getDefaultImageName(), choices = getImageNames())
	config.plugins.MyMetrix.templateFile = ConfigSelection(default="MetrixHD Default.xml", choices = getTemplateFiles())
	config.plugins.MyMetrix.showFirstRun = ConfigYesNo(default=True)
	config.plugins.MyMetrix.logLevel = ConfigSelection(default="off", choices = [
					("off", _("Off")),
					("on", _("On")),
					("debug", _("Debug"))
					])
	config.plugins.MyMetrix.showInMainMenu = ConfigYesNo(default=True)
	#CONNECT
	config.plugins.MetrixConnect.PIN = ConfigNumber()
	config.plugins.MetrixConnect.auth_session = ConfigText()
	config.plugins.MetrixConnect.auth_token = ConfigText(default="None")
	config.plugins.MetrixConnect.auth_id = ConfigText()
	config.plugins.MetrixConnect.username = ConfigText(default=_("Not connected"))

	#General
	
	config.plugins.MetrixUpdater.refreshInterval = ConfigSelectionNumber(10,1440,10,default=30)
	config.plugins.MetrixUpdater.UpdateAvailable = ConfigNumber(default=0)
	config.plugins.MetrixUpdater.Reboot = ConfigNumber(default=0)
	config.plugins.MetrixUpdater.Revision = ConfigNumber(default=1000)
	config.plugins.MetrixUpdater.Open = ConfigNumber(default=0)
	config.plugins.MetrixUpdater.UpdatePopup_SkinParts = ConfigYesNo(default=True)
	config.plugins.MetrixUpdater.UpdatePopup_Packages = ConfigYesNo(default=True)
	config.plugins.MyMetrix.Store.Author = ConfigText(default="Unknown",fixed_size = False)
	config.plugins.MyMetrix.Store.SkinPart_Developer = ConfigYesNo(default=False)
	config.plugins.MyMetrix.Store.Plugin_Developer = ConfigYesNo(default=False)
	config.plugins.MyMetrix.Store.Designname = ConfigText(default="MyDesign",fixed_size = False)
	
	config.plugins.MyMetrix.Color.ProgressBar = ConfigMetrixBarColors("#00ffffff")
	config.plugins.MyMetrix.Color.Selection = ConfigMetrixColors("#00149baf")
	config.plugins.MyMetrix.Color.Background = ConfigMetrixColors("#00000000")
	config.plugins.MyMetrix.Color.Foreground = ConfigMetrixColors("#00ffffff")
	config.plugins.MyMetrix.Color.Background2 = ConfigMetrixColors("#00149baf")
	config.plugins.MyMetrix.Color.Accent1 = ConfigMetrixColors("#00bbbbbb")
	config.plugins.MyMetrix.Color.Accent2 = ConfigMetrixColors("#00999999")
	config.plugins.MyMetrix.Color.BackgroundText = ConfigMetrixColors("#00ffffff")
	
	config.plugins.MyMetrix.Color.Background_Custom = ConfigSequence(seperator = ",", limits = [(0,255),(0,255),(0,255)], default = [0,0,0])
	config.plugins.MyMetrix.Color.Selection_Custom = ConfigSequence(seperator = ",", limits = [(0,255),(0,255),(0,255)], default = [20,155,175])
	config.plugins.MyMetrix.Color.Background2_Custom = ConfigSequence(seperator = ",", limits = [(0,255),(0,255),(0,255)], default = [17,17,17])
	config.plugins.MyMetrix.Color.Foreground_Custom = ConfigSequence(seperator = ",", limits = [(0,255),(0,255),(0,255)], default = [255,255,255])
	config.plugins.MyMetrix.Color.BackgroundText_Custom = ConfigSequence(seperator = ",", limits = [(0,255),(0,255),(0,255)], default = [255,255,255])
	config.plugins.MyMetrix.Color.Accent1_Custom = ConfigSequence(seperator = ",", limits = [(0,255),(0,255),(0,255)], default = [187,187,187])
	config.plugins.MyMetrix.Color.Accent2_Custom = ConfigSequence(seperator = ",", limits = [(0,255),(0,255),(0,255)], default = [153,153,153])
	
	config.plugins.MyMetrix.Color.SkinPartImagesNegate = ConfigYesNo(default=False)
	config.plugins.MyMetrix.Color.SkinPartImagesGreyscale = ConfigYesNo(default=False)
	config.plugins.MyMetrix.Color.SkinPartImagesDepth = ConfigSelection(default=getColorDepth(), choices = [
					("8bit", "8 Bit"),
					("Original","Original")
					])
	#MetrixWeather
	config.plugins.MyMetrix.Color.BackgroundTransparency = ConfigSelectionNumber(0,255,10,default=60,wraparound=False)
	config.plugins.MyMetrix.Color.SelectionTransparency = ConfigSelectionNumber(0,255,10,default=0,wraparound=False)
	config.plugins.MyMetrix.Color.BackgroundTextTransparency = ConfigSelectionNumber(0,255,10,default=220,wraparound=False)
	config.plugins.MyMetrix.Color.BackgroundMode = ConfigSelection(default="Dynamic", choices = [("Dynamic", _("Dynamic"))]+BASIC_COLORS)

	config.plugins.MyMetrix.AutoUpdate = ConfigYesNo(default=True)
	config.plugins.MyMetrix.AutoUpdateSkinParts = ConfigYesNo(default=True)
	
	config.plugins.MyMetrix.ActiveXPicon = ConfigYesNo(default=True)
	config.plugins.MyMetrix.XPiconsOverwrite = ConfigYesNo(default=False)
	config.plugins.MyMetrix.XPiconsRepository = ConfigNumber(default=611)
	config.plugins.MyMetrix.XPiconsRepositoryName = ConfigText(default="MetrixHD Default")
	config.plugins.MyMetrix.XPiconsPath = ConfigSelection(default="/usr/share/enigma2/", choices = [
					("/usr/share/enigma2/", _("Internal")),
					("/media/usb/", _("USB")),
					("/media/hdd/", _("HDD")),
					("/media/cf/", _("CF"))
					])
	config.plugins.MyMetrix.PiconSizes = ConfigSelection(default="220:XPicon/picon/", choices = [
					("220:XPicon/picon/", "XPicons"),
					("220:XPicon/picon/,100:picon/","XPicons, Picons"),
					("220:XPicon/picon/,100:picon/,50:picon5030/","XPicons, Picons, Small Picons"),
					("220:XPicon/picon/,50:picon5030/","XPicons, Small Picons")
					])
	config.plugins.MyMetrix.PiconDepth = ConfigSelection(default=getColorDepth(), choices = [
					("8bit", "8 Bit"),
					("Original","Original")
					])
	config.plugins.MyMetrix.SkinPartPath = ConfigSelection(default=PLUGIN_DIR + "skinparts/", choices = [
					(PLUGIN_DIR + "skinparts/", _("Internal")),
					("/media/usb/skinparts/", _("USB")),
					("/media/hdd/skinparts/", _("HDD")),
					("/media/cf/skinparts/", _("CF"))
					])
	config.plugins.MyMetrix.SkinXMLPath = ConfigSelection(default='/usr/share/enigma2/MetrixHD/', choices = getTargetFolders())
	
	
	
	config.plugins.MetrixCloudSync.SyncBoxInfo = ConfigYesNo(default=False)
	config.plugins.MetrixCloudSync.SyncSkinParts = ConfigYesNo(default=False)
	config.plugins.MetrixCloudSync.SyncPackages = ConfigYesNo(default=False)
	config.plugins.MetrixCloudSync.SyncEPG = ConfigYesNo(default=False)
	config.plugins.MetrixCloudSync.SyncLogs = ConfigYesNo(default=False)
	
	
	config.plugins.MetrixWeather = ConfigSubsection()
	config.plugins.MetrixWeather.woeid = ConfigNumber(default="640161") #Location (visit metrixhd.info)
	config.plugins.MetrixWeather.tempUnit = ConfigSelection(default="Celsius", choices = [
				("Celsius", _("Celsius")),
				("Fahrenheit", _("Fahrenheit"))
				])
	config.plugins.MetrixWeather.currentLocation = ConfigText(default="N/A")
	config.plugins.MetrixWeather.currentWeatherCode = ConfigText(default="(")
	config.plugins.MetrixWeather.currentWeatherText = ConfigText(default="N/A")
	config.plugins.MetrixWeather.currentWeatherTemp = ConfigText(default="0")
	
	config.plugins.MetrixWeather.forecastTodayCode = ConfigText(default="(")
	config.plugins.MetrixWeather.forecastTodayText = ConfigText(default="N/A")
	config.plugins.MetrixWeather.forecastTodayTempMin = ConfigText(default="0")
	config.plugins.MetrixWeather.forecastTodayTempMax = ConfigText(default="0")
	
	config.plugins.MetrixWeather.forecastTomorrowCode = ConfigText(default="(")
	config.plugins.MetrixWeather.forecastTomorrowText = ConfigText(default="N/A")
	config.plugins.MetrixWeather.forecastTomorrowTempMin = ConfigText(default="0")
	config.plugins.MetrixWeather.forecastTomorrowTempMax = ConfigText(default="0")
	
	
	
	
	config.plugins.save()    
	configfile.save()
	
	return config


def getTemplateFiles():
	templates = []
	dirs = listdir(TEMPLATES_DIR)
	for dir in dirs:
		try:
			templates.append((dir,dir.split("/")[-1].replace(".xml","")))
		except: 
			pass
	return templates

def getTargetFolders():
	templates = []
	dirs = listdir('/usr/share/enigma2/')
	for dir in dirs:
		try:
			if os.path.isdir('/usr/share/enigma2/'+dir+'/'):
				if not dir in ("XPicon","XPicons","po","picon","display","extensions","rc_models","spinner","picon5030","skin_default"):
					templates.append(('/usr/share/enigma2/'+dir+'/',dir))
		except: 
			pass
	return templates


def getImageNames():
	if cfg(CONFIG_SYSTEM_DESC,"image","name") == "":
		boxinfo = e2info.getInfo()
		if boxinfo['brand'] == "Dream Multimedia":
			imagenames = [
						"Dream Multimedia Original",
						"Merlin", "iCVS","Newnigma2","Gemini","Oozoon","PBNigma","ZebraDem","HDF-Image",
						"Neutrino HD", "Power-Board Enigma2","PeterPan-Neverland","Infinity-X","LT-Image","openMips","Persian Empire"
						"EDG Nemesis","Open AAF","Other","VTI","OpenPLi","BlackHole","openATV","Vu+ Original","OpenVix","OpenRSi"
						]
		elif boxinfo['brand'] == "Vuplus":
			imagenames = [
				"VTI","OpenPLi","BlackHole","openATV","Vu+ Original","OpenVix",
					"iCVS","Newnigma2","Gemini","Oozoon","PBNigma","ZebraDem","Merlin", "Neutrino HD","Dream Multimedia Original","HDF-Image",
					"Power-Board Enigma2","PeterPan-Neverland","Infinity-X","LT-Image","openMips","OpenRSi","Persian Empire"
					"EDG Nemesis","Open AAF","Other"
				]
		else:
			imagenames = [
			"OpenPLi","BlackHole","openATV","openMips","OpenRSi",
				"iCVS","Newnigma2","Gemini","Oozoon","PBNigma","ZebraDem","Merlin", "Neutrino HD","HDF-Image",
				"Power-Board Enigma2","PeterPan-Neverland","Infinity-X","LT-Image","OpenVix","Persian Empire"
				"EDG Nemesis","Open AAF","Other","VTI","Vu+ Original","Dream Multimedia Original"
			]	
		return imagenames
	else:
		return [cfg(CONFIG_SYSTEM_DESC,"image","name")]



def getDefaultImageName():
	if cfg(CONFIG_SYSTEM_DESC,"image","name") == "":
		boxinfo = e2info.getInfo()
		if boxinfo['brand'] == "Dream Multimedia":
			imagename = "Dream Multimedia Original"
		elif boxinfo['brand'] == "Vuplus":
			imagename = "VTI"
		elif boxinfo['brand'] == "AZBOX":
			imagename = "openATV"
		else:
			imagename = "OpenPLi"
		return imagename
	else:
		return cfg(CONFIG_SYSTEM_DESC,"image","name")
	
def cfg(configfile,sectionname,keyname,type="string"):
	section = str(sectionname)
	key = str(keyname)
	try:
		conf = ConfigParser.RawConfigParser()
		conf.read(configfile)
		if type == "string":
			value = conf.get(section,key)
			return value
		elif type == "int":
			value = conf.getint(section,key)
			return value
	except:
		if type == "string":
			return ""
		elif type == "int":
			return NONEINT

				
def cfgset(configfile,sectionname,keyname,keyvalue):
	section = str(sectionname)
	key = str(keyname)
	value = str(keyvalue)
	try:
		conf = ConfigParser.RawConfigParser()
		conf.read(configfile)
		try:
			conf.set(section, key, value)
		except ConfigParser.NoSectionError:
		 	conf.add_section(section)
		 	conf.set(section, key, value)
		with open(configfile, 'wb') as file:
  			conf.write(file)
		return True
	except Exception, e:
		print str(e)
		return False
	
def cfgremovesection(configfile,sectionname):
	section = str(sectionname)
	try:
		conf = ConfigParser.RawConfigParser()
		conf.read(configfile)
		try:
			conf.remove_section(section)
		except:
			pass
		with open(configfile, 'wb') as file:
  			conf.write(file)
		return True
	except Exception, e:
		print str(e)
		return False

def getOEVersion():
	if sys.version_info < (2, 7):
		oeversion = "1.6"
	else:
		oeversion = "2.0"
	return oeversion

def getColorDepth():
	if getOEVersion == "1.6":
		return "8bit"
	else:
		return "Original"
	
