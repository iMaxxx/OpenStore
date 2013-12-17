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

import thread
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from twisted.web.client import downloadPage
from Screens.Console import Console
from Screens.Standby import TryQuitMainloop
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, ConfigYesNo, ConfigSequence, ConfigSubsection, ConfigSelectionNumber, getConfigListEntry, ConfigSelection, ConfigNumber, ConfigText, ConfigInteger
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Language import language
from uuid import getnode as get_mac
from os import environ, listdir, remove, rename, system
from skin import parseColor
from Components.Pixmap import Pixmap
from Components.Label import Label
import urllib2
import urllib
from xml.dom.minidom import parseString
import gettext
from Components.GUIComponent import GUIComponent
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText,MultiContentEntryPixmapAlphaTest
from enigma import eListbox, RT_HALIGN_LEFT, RT_HALIGN_RIGHT
from enigma import ePicLoad,eListboxPythonMultiContent,gFont,addFont, loadPic, loadPNG
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import metrix_MetrixColors
import metrixDefaults
import store_SubmitRating
import threading
import time
import metrixTools
import metrixCore
import metrix_MetrixColorsTools

#############################################################

config = metrixDefaults.loadDefaults()

def _(txt):
	t = gettext.dgettext("MyMetrix", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t



#######################################################################		
		

class OpenScreen(ConfigListScreen, Screen):
	skin = """
<screen name="MyMetrix-Store-Browse" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">
<eLabel position="0,0" size="1280,720" backgroundColor="#b0ffffff" zPosition="-50" />
<eLabel position="40,40" size="620,640" backgroundColor="#40111111" zPosition="-1" />
<eLabel position="660,70" size="575,580" backgroundColor="#40222222" zPosition="-1" />
  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="695,608" size="250,33" text="%s" transparent="1" />
 <widget name="menu" position="55,122" scrollbarMode="showNever" size="605,555" transparent="1" foregroundColor="#00ffffff" backgroundColor="#40000000" />
  <widget position="55,55" size="558,50" name="title" foregroundColor="#00ffffff" font="SetrixHD; 40" valign="center" transparent="1" backgroundColor="#40000000" />
  
  <eLabel position="681,610" size="5,40" backgroundColor="#0000ff00" />
<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/star.png" position="1177,549" size="32,34" zPosition="1" alphatest="blend" />
  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="1009,608" size="200,33" text="%s" transparent="1" />
<widget name="helperimage" position="671,206" size="550,310" zPosition="1" alphatest="blend" />
<widget position="674,82" size="546,50" name="designname" foregroundColor="#00ffffff" font="SetrixHD; 35" valign="center" transparent="1" backgroundColor="#40000000" />
 <widget position="679,542" size="491,50" name="votes" foregroundColor="#00ffffff" font="Regular; 30" valign="center" halign="right" transparent="1" backgroundColor="#40000000" />
<eLabel position="995,610" zPosition="1" size="5,40" backgroundColor="#00ffff00" />
<widget position="675,142" size="341,50" name="author" foregroundColor="#00bbbbbb" font="Regular; 28" valign="center" backgroundColor="#40000000" transparent="1" halign="left" />
<widget position="1019,145" size="200,40" name="date" foregroundColor="#00999999" font="Regular; 25" valign="center" backgroundColor="#40000000" transparent="1" halign="right" zPosition="1" />

 </screen>
""" %(_("Install "), _("Vote"))

	def __init__(self, session, args = None):
		self["title"] = Label(_("OpenStore // MetrixColors"))
		self.screenshotpath = metrixDefaults.URL_GET_METRIXCOLORS_PREVIEW + "&width=550&name="
		Screen.__init__(self, session)
		self.session = session
		self["designname"] = Label()
		self["author"] = Label()
		self["votes"] = Label()
		self["date"] = Label()
		self.currentid = 1
		self.currentgroup = 'DesignStore_'
		self.currentname = ""
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self.picPath = metrixDefaults.URI_IMAGE_LOADING
		self["helperimage"] = Pixmap()
		self.thread_getDesigns = threading.Thread(target=self.threadworker,  args=())
		
		#THREAD ACTIONS
		self.getCatalog = True
		self.getEntry = False
		self.finished = False
		
		self["menu"] =  SkinPartsList([])
		menu = []
		menu.append(self.DesignsListEntry("-",_("loading, please wait...")))
		self["menu"].setList(menu)



		self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions"], {
			"up": self.keyUp,
			"ok": self.selectItem,
			"down": self.keyDown,
			"green": self.applyDesign,
			"yellow": self.openRating,
			"right": self.pageDown,
			"left": self.pageUp,
			"cancel": self.save}, -1)
		self.UpdatePicture()
		self.onLayoutFinish.append(self.startThread)
		
	def startThread(self):	
		self.thread_getDesigns.daemon = True
		self.thread_getDesigns.start()
		
	#THREAD WORKER
	def threadworker(self):
		while(self.finished==False):
			if self.getCatalog == True:
				self.getCatalog = False
				self.getDesigns()
			if self.getEntry == True:
				self.getEntry = False
				returnValue = self.currentname
				self.picPath = metrixTools.webPixmap(self.screenshotpath + returnValue)
				#print returnValue
				metrixTools.callOnMainThread (self.refreshMeta)
			time.sleep(1)
		
	def getDesigns(self):
		menu = []
		try:
			data = metrixCore.getWeb(metrixDefaults.URL_GET_METRIXCOLORS,True,{'name':self.currentname})
			#print data
			dom = parseString(data)
			for design in dom.getElementsByTagName('design'):
				name = str(design.getAttributeNode('name').nodeValue)
				title = str(design.getAttributeNode('title').nodeValue)
				author = str(design.getAttributeNode('author').nodeValue)
				rating = str(design.getAttributeNode('rating').nodeValue)
				date = str(design.getAttributeNode('date').nodeValue)
				total_votes = str(design.getAttributeNode('total_votes').nodeValue)
				menu.append(self.DesignsListEntry(name,title,author,rating,date,total_votes))
				metrixTools.callOnMainThread (self.setList,menu)
		except Exception, e:
			metrixTools.log("Error getting MetrixColor via web!",e)
			menu.append(self.DesignsListEntry("-",_("Error loading data!")))
			metrixTools.callOnMainThread (self.setList,menu)
	
	def setList(self,menu):
		self["menu"].setList(menu)
		self.currentname = str(self["menu"].l.getCurrentSelection()[0][0])
		self.getEntry = True
		
	def updateSelection(self):
		self.currentname = str(self["menu"].l.getCurrentSelection()[0][0])
		
	def refreshMeta(self):
		self.updateMeta()
		self.ShowPicture()
	
	def DesignsListEntry(self,name,title="",author="",rating="",date="",total_votes=""):
		res = [[name,title,author,rating,date,total_votes]]
		png = metrixDefaults.PLUGIN_DIR + "images/vote"+rating+".png"
		pngtype = metrixDefaults.PLUGIN_DIR + "MyMetrix/images/brush.png"
		res.append(MultiContentEntryPixmapAlphaTest(pos=(412, 9), size=(170, 32), png=loadPNG(png)))
		res.append(MultiContentEntryPixmapAlphaTest(pos=(3, 7), size=(32, 32), png=loadPNG(pngtype)))
		res.append(MultiContentEntryText(pos=(40, 4), size=(367, 45), font=0, text=title))
		return res
		
	def updateMeta(self):
		try:
			self["designname"].setText(str(self["menu"].l.getCurrentSelection()[0][1]))
			self["author"].setText(_("by " + str(self["menu"].l.getCurrentSelection()[0][2])))
			self["votes"].setText(str(self["menu"].l.getCurrentSelection()[0][5]))
			self["date"].setText(str(self["menu"].l.getCurrentSelection()[0][4]))
			self.currentid = 1
			self.currentgroup = 'DesignStore_'+str(self["menu"].l.getCurrentSelection()[0][0])
		except:
			pass
	
	def UpdatePicture(self):
		self.PicLoad.PictureData.get().append(self.DecodePicture)
		self.onLayoutFinish.append(self.ShowPicture)
	
	def ShowPicture(self):
		self.PicLoad.setPara([self["helperimage"].instance.size().width(),self["helperimage"].instance.size().height(),self.Scale[0],self.Scale[1],0,1,"#30000000"])
		self.PicLoad.startDecode(self.picPath)
		#print "showing image"
		
	def DecodePicture(self, PicInfo = ""):
		#print "decoding picture"
		ptr = self.PicLoad.getData()
		self["helperimage"].instance.setPixmap(ptr)	
		
	

	def UpdateComponents(self):
		self.UpdatePicture()
		
	def selectItem(self):
		self.getEntry = True
		
		
	def keyDown(self):
		self["menu"].instance.moveSelection(self["menu"].instance.moveDown)
		self.updateSelection()
		self.getEntry = True
		
	def keyUp(self):
		self["menu"].instance.moveSelection(self["menu"].instance.moveUp)
		self.updateSelection()
		self.getEntry = True
		
	def pageUp(self):
		self["menu"].instance.moveSelection(self["menu"].instance.pageUp)
		self.updateSelection()
		self.getEntry = True
		
	def pageDown(self):
		self["menu"].instance.moveSelection(self["menu"].instance.pageDown)	
		self.updateSelection()
		self.getEntry = True
	
	def save(self):
		config.plugins.MyMetrix.Color.save()
		configfile.save()
		self.exit()

	
	def exit(self):
		self.finished = True
		self.thread_getDesigns.join()
		self.close()
		
	def applyDesign(self):
		if metrix_MetrixColorsTools.installMetrixColors(self.currentname):
			self.showInfo(_("MetrixColors successfully installed!\nSave skin to apply!"))
		else:
			self.showInfo(_("Error installing MetrixColors!"))

	def openRating(self):
		metrixTools.callOnMainThread(self.session.open,store_SubmitRating.OpenScreen,self.currentid,self.currentgroup)
	
					

	def showInfo(self, text=_("Information")):
		metrixTools.callOnMainThread (self.session.open,MessageBox, _(text), MessageBox.TYPE_INFO)
			

		
class SkinPartsList(MenuList):
	def __init__(self, list):
		MenuList.__init__(self, list, False, eListboxPythonMultiContent)
		self.l.setItemHeight(50)
		self.l.setFont(0, gFont("SetrixHD", 26))
		self.l.setFont(1, gFont("Regular", 22))
		
	