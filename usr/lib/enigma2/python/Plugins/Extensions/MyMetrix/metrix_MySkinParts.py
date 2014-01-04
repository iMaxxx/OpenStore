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
import shutil
import os
import time
import threading
import traceback
import metrixTools
import metrix_SkinPartTools
import metrix_MySkinParts_Settings

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
<screen name="MyMetrix-MySkinParts" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="#b0ffffff">
<eLabel position="40,40" size="620,640" backgroundColor="#40111111" zPosition="-1" />
<eLabel position="660,70" size="575,580" backgroundColor="#40222222" zPosition="-1" />
  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="690,614" size="100,33" text="%s" transparent="1" />
 <widget name="mainmenu" backgroundColorSelected="#00282828" foregroundColorSelected="#00ffffff" position="55,122" scrollbarMode="showOnDemand" size="590,541" transparent="1" foregroundColor="#00ffffff" backgroundColor="#40000000" />
  <widget position="55,55" size="589,50" foregroundColor="#00ffffff" name="title" font="SetrixHD; 40" valign="center" transparent="1" backgroundColor="#40000000" />
  
  <eLabel position="676,610" size="5,40" backgroundColor="#00ff0000" />
<widget position="679,496" size="532,112" name="description" foregroundColor="#00ffffff" font="Regular; 17" valign="center" halign="left" transparent="1" backgroundColor="#40000000" />

  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="819,613" size="100,33" text="%s" transparent="1" />
<widget name="helperimage" position="671,181" size="550,310" zPosition="1" alphatest="blend" />
<widget position="674,82" size="546,50" name="itemname" foregroundColor="#00ffffff" font="SetrixHD; 35" valign="center" transparent="1" backgroundColor="#40000000" noWrap="1" />
 <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="949,613" size="103,33" text="%s" transparent="1" />
<eLabel position="805,611" zPosition="1" size="5,40" backgroundColor="#0000ff00" />
<widget position="675,132" size="341,50" name="author" foregroundColor="#00bbbbbb" font="Regular; 28" valign="center" backgroundColor="#40000000" transparent="1" halign="left" />

<eLabel position="1064,610" zPosition="1" size="5,40" backgroundColor="#000000ff" />

<widget position="1019,135" size="200,40" name="date" foregroundColor="#00999999" font="Regular; 25" valign="center" backgroundColor="#40000000" transparent="1" halign="right" zPosition="1" />
 <eLabel position="934,610" zPosition="1" size="5,40" backgroundColor="#00ffff00" />
<eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="1079,613" size="149,33" text="%s" transparent="1" />
</screen>
""" %(_("Delete"), _("On"), _("Off"), _("Settings"))

	

	def __init__(self, session, args = None, picPath = None):
		self["title"] = Label("MyMetrix // "+_("My SkinParts"))
		self.skin_lines = []
		Screen.__init__(self, session)
		self.session = session
		self.picPath = picPath
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self["helperimage"] = Pixmap()
		self["itemname"] = Label()
		self["author"] = Label()
		self["date"] = Label()
		self["description"] = Label()
		self.setTitle(_("My SkinParts"))
		self.thread_updater = threading.Thread(target=self.threadworker,  args=())
		
		self.getCatalog = True
		self.getEntry = False
		self.finished = False
		
		self["mainmenu"] =  StoreList([])
		
		menu = []
		menu.append(self.StoreMenuEntry("No SkinParts installed!"))
		self["mainmenu"].setList(menu)
		
		

		
		self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions"], {
			"right": self.pageDown,
			"left": self.pageUp,
			"down": self.keyDown,
			"up": self.keyUp,
			"ok": self.openSettings,
			"red": self.deleteSkinPart,
			"green": self.enableSkinPart,
			"yellow": self.disableSkinPart,
			"blue": self.openSettings,
			"cancel": self.exit}, -1)
		self.UpdatePicture()
		self.onLayoutFinish.append(self.startThread)
		
	def startThread(self):	
		self.thread_updater.daemon = True
		self.thread_updater.start()
		
	#THREAD WORKER
	def threadworker(self):
		while(self.finished == False):
			if self.getCatalog == True:
				self.getCatalog = False
				menu = []
				menu = menu + self.getSkinParts(config.plugins.MyMetrix.SkinPartPath.value + "widgets/active/","-on")
				menu = menu + self.getSkinParts(config.plugins.MyMetrix.SkinPartPath.value + "screens/active/","-on")
				menu = menu + self.getSkinParts(config.plugins.MyMetrix.SkinPartPath.value + "widgets/inactive/")
				menu = menu + self.getSkinParts(config.plugins.MyMetrix.SkinPartPath.value + "screens/inactive/")
				metrixTools.callOnMainThread(self.setList,menu)
			if self.getEntry == True:
				self.getEntry = False
				metrixTools.callOnMainThread(self.refreshMeta)
			time.sleep(1)
			
	def getSkinParts(self,path,isactive=""):
		dirs = listdir( path )
		entries = []
		for dir in dirs:
			try:
				#print dir
				file = open(path+"/"+dir+"/meta.xml", "r")
				data = file.read()
				file.close()	
				dom = parseString(data)
				for entry in dom.getElementsByTagName('entry'):
					id = str(entry.getAttributeNode('id').nodeValue)
					name = str(entry.getAttributeNode('name').nodeValue)
					author = str(entry.getAttributeNode('author').nodeValue)
					version = str(entry.getAttributeNode('version').nodeValue)
					description = str(entry.getAttributeNode('description').nodeValue)
					date = str(entry.getAttributeNode('date').nodeValue)
					type = str(entry.getAttributeNode('type').nodeValue)
					version = str(entry.getAttributeNode('version').nodeValue)
					entries.append(self.StoreMenuEntry(name, path+dir,type,author,version,description,isactive,id))
			except:
				pass
		return entries
		
	def setList(self,menu):
		self["mainmenu"].setList(menu)
		self.getEntry = True
		
	def refreshMeta(self):
		self.updateMeta()
		self.ShowPicture()
	
	
	def StoreMenuEntry(self,name,value="",type="screen",author="",version="",description="",isactive="",id=""):
		res = [[value,name,type,author,version,description,isactive,id]]
		pngtype = metrixDefaults.PLUGIN_DIR + "images/"+type+isactive+".png"
		if isactive == "":
			res.append(MultiContentEntryText(pos=(40, 4), size=(455, 45), font=0, text=name))
		else:
			res.append(MultiContentEntryText(pos=(40, 4), size=(455, 45), font=0, text=name,color=metrixDefaults.COLOR_INSTALLED))
		res.append(MultiContentEntryPixmapAlphaTest(pos=(3, 7), size=(32, 32), png=loadPNG(pngtype)))
		
		return res
	
	def updateMeta(self):
		try:
			self["itemname"].setText(str(self["mainmenu"].l.getCurrentSelection()[0][1]))
			self["author"].setText(_("by " + str(self["mainmenu"].l.getCurrentSelection()[0][3])))
			#self["votes"].setText(_(str(self["menu"].l.getCurrentSelection()[0][6])))
			self["date"].setText(str(self["mainmenu"].l.getCurrentSelection()[0][4]))
			self["description"].setText(str(self["mainmenu"].l.getCurrentSelection()[0][5]))
		
		except:
			pass
		
	def openSettings(self):
		item_id = self["mainmenu"].l.getCurrentSelection()[0][7]
		name = self["mainmenu"].l.getCurrentSelection()[0][1]
		author = self["mainmenu"].l.getCurrentSelection()[0][3]
		version = self["mainmenu"].l.getCurrentSelection()[0][4]
		description = self["mainmenu"].l.getCurrentSelection()[0][5]
		item_type = self["mainmenu"].l.getCurrentSelection()[0][2]
		path = self["mainmenu"].l.getCurrentSelection()[0][0]
		self.session.open(metrix_MySkinParts_Settings.OpenScreen,path,name,author,str(version),description)
		#self.session.open(metrix_Settings_SkinParts_Settings.OpenScreen)
			
	def disableSkinPart(self):
		try:
			file = self["mainmenu"].l.getCurrentSelection()[0][0]
			metrix_SkinPartTools.disableSkinPart(file)
		except Exception, e:
			metrixTools.log("Error disabling SkinPart!",e)
		self.getCatalog = True
		
	def deleteSkinPart(self):
		try:
			file = self["mainmenu"].l.getCurrentSelection()[0][0]
			shutil.rmtree(file)
		except Exception, e:
			metrixTools.log("Error deleting SkinPart!",e)
		self.getCatalog = True
		
	def enableSkinPart(self):
		try:
			sp_file = self["mainmenu"].l.getCurrentSelection()[0][0]
			metrix_SkinPartTools.enableSkinPart(sp_file)
		except Exception, e:
			metrixTools.log("Error enabling SkinPart!",e)
		self.getCatalog = True

	

	def GetPicturePath(self):
		config.plugins.MyMetrix.Color.save()
		try:
			self.picPath = self["mainmenu"].l.getCurrentSelection()[0][0] +"/preview.png"
		except:
			self.picPath = metrixDefaults.PLUGIN_DIR + "images/nopreview.png"
		return self.picPath 
		
	def UpdatePicture(self):
		self.PicLoad.PictureData.get().append(self.DecodePicture)
		self.onLayoutFinish.append(self.ShowPicture)
	
	def ShowPicture(self):
		self.PicLoad.setPara([self["helperimage"].instance.size().width(),self["helperimage"].instance.size().height(),self.Scale[0],self.Scale[1],0,1,"#002C2C39"])
		self.PicLoad.startDecode(self.GetPicturePath())
		#print "showing image"
		
	def DecodePicture(self, PicInfo = ""):
		#print "decoding picture"
		ptr = self.PicLoad.getData()
		self["helperimage"].instance.setPixmap(ptr)	

	def UpdateComponents(self):
		self.UpdatePicture()
				

	def keyLeft(self):	
		self.exit()
		

	def keyRight(self):
		self.getEntry = True
		
	
	def pageUp(self):
		self["mainmenu"].instance.moveSelection(self["mainmenu"].instance.pageUp)
		self.getEntry = True
		
	def pageDown(self):
		self["mainmenu"].instance.moveSelection(self["mainmenu"].instance.pageDown)	
		self.getEntry = True
		
	def keyDown(self):
		self["mainmenu"].instance.moveSelection(self["mainmenu"].instance.moveDown)
		self.getEntry = True
		
	def keyUp(self):
		self["mainmenu"].instance.moveSelection(self["mainmenu"].instance.moveUp)
		self.getEntry = True

	def showInfo(self):
		self.session.open(MessageBox, _("Information"), MessageBox.TYPE_INFO)

	def save(self):
		self.exit()

	
	def exit(self):
		self.finished = True
		self.thread_updater.join()
		self.close()
		
class StoreList(MenuList):
	def __init__(self, list):
		MenuList.__init__(self, list, False, eListboxPythonMultiContent)
		self.l.setItemHeight(50)
		self.l.setFont(0, gFont("SetrixHD", 26))
		self.l.setFont(1, gFont("Regular", 22))
