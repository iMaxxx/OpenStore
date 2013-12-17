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
from xml.dom.minidom import parseString
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
from Components.GUIComponent import GUIComponent
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText,MultiContentEntryPixmapAlphaTest
from enigma import eListbox, RT_HALIGN_LEFT, RT_HALIGN_RIGHT
from enigma import ePicLoad,eListboxPythonMultiContent,gFont,addFont, loadPic, loadPNG
from Components.Pixmap import Pixmap
from Components.Label import Label
import urllib
import gettext
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import metrix_MetrixColors
import metrixDefaults
import metrixTools
from xml.dom.minidom import parse
import shutil
import os
import time
import threading
import traceback
import metrix_SkinPartTools
import ConfigParser

#############################################################

config = metrixDefaults.loadDefaults()

def _(txt):
	t = gettext.dgettext("MyMetrix", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

#######################################################################		
		
#THREAD ACTIONS

		
class OpenScreen(ConfigListScreen, Screen):
	skin = """
<screen name="MyMetrix-SkinPart-Settings" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="#b0ffffff">
<eLabel position="671,77" size="550,50" foregroundColor="#00ffffff" font="SetrixHD; 35" valign="center" transparent="1" backgroundColor="#40000000" text="%s" />
<eLabel position="40,40" size="620,640" backgroundColor="#40111111" zPosition="-1" />
<eLabel position="660,70" size="575,580" backgroundColor="#40222222" zPosition="-1" />
  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="63,642" size="180,33" text="%s" transparent="1" />
 <widget name="config" itemHeight="30" position="670,136" scrollbarMode="showOnDemand" size="553,497" transparent="1" foregroundColor="#00ffffff" backgroundColor="#40000000" />
  <eLabel position="52,640" size="5,40" backgroundColor="#00ff0000" />
<widget position="53,508" size="593,119" name="description" foregroundColor="#00ffffff" font="Regular; 17" valign="center" halign="left" transparent="1" backgroundColor="#40000000" />
  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="264,642" size="182,33" text="%s" transparent="1" />
<widget name="helperimage" position="76,181" size="550,310" zPosition="1" alphatest="blend" />
<widget position="55,55" size="589,50" name="itemname" foregroundColor="#00ffffff" font="SetrixHD; 40" valign="center" transparent="1" backgroundColor="#40000000" noWrap="1" />
 
<eLabel position="252,640" zPosition="1" size="5,40" backgroundColor="#0000ff00" />
<widget position="55,116" size="341,50" name="author" foregroundColor="#00bbbbbb" font="Regular; 28" valign="center" backgroundColor="#40000000" transparent="1" halign="left" />

<widget position="444,121" size="200,40" name="date" foregroundColor="#00999999" font="Regular; 25" valign="center" backgroundColor="#40000000" transparent="1" halign="right" zPosition="1" />
 </screen>
""" %(_("Settings"),_("Cancel"), _("Save"))

	

	def __init__(self, session,path,name="",author="",version="",description=""):
		Screen.__init__(self, session)
		self.session = session
		self.picPath = path + "/preview.png"
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self["helperimage"] = Pixmap()
		
		
		
		self.path = path
		self.configpath = self.path + '/config.cfg'
		self.xml = parse(path + "/data.xml")
		
		#Read config file
		self.skinpartconfig = ConfigParser.RawConfigParser()
		self.skinpartconfig.read(self.configpath)
		
		
		self.listnames = []
		self.list = []
		self.getTargetScreens()
		self.list.append(getConfigListEntry(" "))
		self.listnames.append(["-","-"])
		self.movingOptions()
		self.list.append(getConfigListEntry(" "))
		self.listnames.append(["-","-"])
		self.getVariables()
		
		ConfigListScreen.__init__(self, self.list)
		
		
		
		self["itemname"] = Label(name)
		self["author"] = Label(author)
		self["date"] = Label(version)
		self["description"] = Label(description)
		
		self.UpdatePicture()
		
		self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions"], {
			"red": self.exit,
			"green":self.saveConfig,
			"cancel": self.saveConfig}, -1)
		
		#self.onLayoutFinish.append(self.getTargetScreens())

		
		
	def getTargetScreens(self):
		self.list.append(getConfigListEntry(_("Screens")+" ------------------------------------------------------------------------------------------"))
		self.listnames.append(["-","-"])
		for screen in self.xml.getElementsByTagName('screen'):
			for name in str(screen.getAttributeNode('name').nodeValue).split(","):
				configItem = ConfigSelection(default=self.readSettings("screen",name),choices = [("",_("Off")),(name,_("On"))])
				self.list.append(getConfigListEntry(_(str(name)),configItem))
				self.listnames.append(["screen",name])
				
		for screen in self.xml.getElementsByTagName('skinpartwidget'):
			for name in str(screen.getAttributeNode('screenname').nodeValue).split(","):
				configItem = ConfigSelection(default=self.readSettings("screen",name),choices = [("",_("Off")),(name,_("On"))])
				self.list.append(getConfigListEntry(_(str(name)),configItem))
				self.listnames.append(["screen",name])
		
	def readSettings(self,section,key,value="",type=""):
		default = ""
		if section == "screen":
			try:
				default = self.skinpartconfig.get(section,key)
			except:
				default = value
				if key == "InfoBar" or key == "SecondInfoBar":
					default = key
		elif section == "rel_position":
			try:
				default = self.skinpartconfig.getint(section,key)
			except:
				default = value
		elif section == "variable":
			if type == "text":
				try:
					default = self.skinpartconfig.get(section,key)
				except:
					default = value
			elif type == "number" or type == "range":
				try:
					default = self.skinpartconfig.getint(section,key)
				except:
					default = value
			elif type == "yesno":
				try:
					default = self.skinpartconfig.getboolean(section,key)
				except:
					default = metrixTools.str2bool(value)
			elif type == "list":
				try:
					default = self.skinpartconfig.get(section,key)
				except:
					default = value
		return default

	#Option to move relative
	def movingOptions(self):
		self.list.append(getConfigListEntry(_("Move relative (Pixels)")+" -------------------------------------------------------------------------------------------"))
		self.listnames.append(["-","-"])
		move_x = ConfigSelectionNumber(-1280,1280,1,default=self.readSettings("rel_position","posx",0),wraparound=False)
		self.list.append(getConfigListEntry(_(str("Horizontal (+-1280)")),move_x))
		self.listnames.append(["rel_position","posx"])
		move_y = ConfigSelectionNumber(-720,720,1,default=self.readSettings("rel_position","posy",0),wraparound=False)
		self.list.append(getConfigListEntry(_(str("Vertical (+-720)")),move_y))
		self.listnames.append(["rel_position","posy"])
		
	def getVariables(self):
		section = "variable"
		i = 0
		configItem = ""
		try:
			for variable in self.xml.getElementsByTagName('variable'):
				value = 0
				varname = variable.getAttributeNode('name').nodeValue
				try:
					value = variable.getAttributeNode('value').nodeValue
				except:
					pass
				if i == 0:
					self.list.append(getConfigListEntry(_("Options")+" ----------------------------------------------------------------------------------------------"))
					self.listnames.append(["-","-"])
				type = str(variable.getAttributeNode('type').nodeValue)
				if type == "text":
					configItem = ConfigText(default=self.readSettings(section,varname,value,type),fixed_size = False)
				if type == "yesno":
					configItem = ConfigYesNo(default=self.readSettings(section,varname,value,type))
				elif type == "number":
					configItem = ConfigNumber(default=self.readSettings(section,varname,value,type))
				elif type == "range":
					min = int(variable.getAttributeNode('min').nodeValue)
					max = int(variable.getAttributeNode('max').nodeValue)
					step = int(variable.getAttributeNode('step').nodeValue)
					configItem = ConfigSelectionNumber(min,max,step,default=self.readSettings(section,varname,value,type),wraparound=False)
				elif type == "list":
					options = []
					for option in variable.getElementsByTagName('option'):
						optTitle = str(option.getAttributeNode('title').nodeValue)
						optValue = str(option.getAttributeNode('value').nodeValue)
						optionItem = (optValue,_(optTitle))
						options.append(optionItem)
					configItem = ConfigSelection(default=self.readSettings(section,varname,value,type), choices = options)
				if type != "static" and type != "global":
					self.list.append(getConfigListEntry(_(str(str(variable.getAttributeNode('title').nodeValue))),configItem))
					self.listnames.append([section,varname])
					i+=1	
						
				
		except Exception, e:
			self.list.append(getConfigListEntry(_("SkinPart Error: ")))
			self.list.append(getConfigListEntry(str(e)))	
								

	def saveConfig(self):
		configcontainer = ConfigParser.RawConfigParser()
		configlist = self["config"].getList()
		for i in range(0,len(self.listnames)):
			section = self.listnames[i][0]
			variable = self.listnames[i][1]
			if section != "-":
				value = str(configlist[i][1].value)
				try:
					configcontainer.set(section, variable, value)
				except ConfigParser.NoSectionError:
				 	# Create non-existent section
				 	configcontainer.add_section(section)
				 	configcontainer.set(section, variable, value)
				
				
		
		with open(self.configpath, 'wb') as configfile:
  			configcontainer.write(configfile)
  		self.close()


	def UpdatePicture(self):
		self.PicLoad.PictureData.get().append(self.DecodePicture)
		self.onLayoutFinish.append(self.ShowPicture)
	
	def ShowPicture(self):
		self.PicLoad.setPara([self["helperimage"].instance.size().width(),self["helperimage"].instance.size().height(),self.Scale[0],self.Scale[1],0,1,"#002C2C39"])
		self.PicLoad.startDecode(self.picPath)
		#print "showing image"
		
	def DecodePicture(self, PicInfo = ""):
		#print "decoding picture"
		ptr = self.PicLoad.getData()
		self["helperimage"].instance.setPixmap(ptr)	

	def UpdateComponents(self): 
		pass


	def showInfo(self):
		self.session.open(MessageBox, _("Information"), MessageBox.TYPE_INFO)

	def save(self):
		self.close()

	
	def exit(self):
		self.close()
		
		

		