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
from xml.dom.minidom import parseString
import gettext
from Components.GUIComponent import GUIComponent
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText,MultiContentEntryPixmapAlphaTest
from enigma import eListbox, RT_HALIGN_LEFT, RT_HALIGN_RIGHT
from enigma import ePicLoad,eListboxPythonMultiContent,gFont,addFont, loadPic, loadPNG
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import metrixDefaults
import store_SubmitRating
import store_SkinParts_Browse
import store_MetrixColors_Browse
import store_Packages_Browse
import threading
import time
import metrixTools
import metrixCore
import store_Settings
import traceback

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
<screen name="OpenStore-SkinParts-Categories" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">
<eLabel position="517,43" size="611,640" backgroundColor="#40111111" zPosition="-1" />
<eLabel position="1111,43" size="5,60" backgroundColor="#000000ff" />
<widget position="942,60" size="163,40" name="sort" foregroundColor="#00bbbbbb" font="Regular; 25" valign="center" backgroundColor="#40000000" transparent="1" halign="right" />
  <widget position="528,54" size="413,50" name="title" foregroundColor="#00ffffff" font="SetrixHD; 40" valign="center" transparent="1" backgroundColor="#40000000" />
  <widget name="menu" backgroundColorSelected="#00282828" foregroundColorSelected="#00ffffff" position="506,119" scrollbarMode="showAlways" size="613,554" transparent="1" foregroundColor="#00ffffff" backgroundColor="#40000000" />
    <eLabel position="132,43" zPosition="-1" size="340,320" backgroundColor="#40000000" transparent="0" />
    <!-- /*ClockWidget-->
    <widget source="global.CurrentTime" foregroundColor="#00ffffff" render="Label" position="307,396" size="169,80" font="SetrixHD; 60" halign="left" backgroundColor="#40000000" transparent="1" valign="top">
      <convert type="ClockToText">Default</convert>
    </widget>
    <widget source="global.CurrentTime" render="Label" position="160,438" size="148,29" font="SetrixHD; 20" halign="right" backgroundColor="#40000000" foregroundColor="#00bbbbbb" transparent="1">
      <convert type="ClockToText">Format:%e. %B</convert>
    </widget>
    <widget source="global.CurrentTime" render="Label" position="183,409" size="125,30" font="SetrixHD; 20" halign="right" backgroundColor="#40000000" foregroundColor="#00bbbbbb" transparent="1">
      <convert type="ClockToText">Format:%A</convert>
    </widget>
    <eLabel position="132,405" zPosition="-1" size="340,70" backgroundColor="#40000000" transparent="0" />
    <!--ClockWidget */-->
    <ePixmap position="171,66" size="256,256" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/openstore-logo.png" alphatest="blend" />
</screen>
"""

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		
		self["sort"] = Label()
		self.sort = "screens"
		self.url = metrixDefaults.URL_GET_SUITES
		
		self["menu"] =  CategoryList([])
		self.CategoryListEntry(_("Loading..."))
		
		
		
		self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions"], {
			"right": self.pageDown,
			"left": self.pageUp,
			"up": self.keyUp,
			"upRepeated": self.keyUp,
			"ok": self.go,
			"blue": self.changeSort,
			"down": self.keyDown,
			"downRepeated": self.keyDown,
			"cancel": self.exit}, -1)
		
		self.setTitle("OpenStore")
		self["title"] = Label(_("MyMetrix // OpenStore"))
		
		menu = []
		menu.append(self.CategoryListEntry(_("Loading...")))
		metrixTools.callOnMainThread(self.setList,menu)
		self["menu"].setList(menu)
		
		self.onLayoutFinish.append(self.changeSort)
		
		
		
	
	def changeSort(self):
		if self.sort == "suite":
			self.sort = "screens"
			self.url = metrixDefaults.URL_GET_SCREENS
			self["sort"].setText(_("Screens"))
		else:
			self.sort = "suite"
			self.url = metrixDefaults.URL_GET_SUITES
			self["sort"].setText(_("Suites"))
		#self.getCategories()
		metrixTools.callOnMainThread(self.getCategories)
		
	def go(self):
		returnValue = str(self["menu"].l.getCurrentSelection()[0][0])
		
		if returnValue is not None:
			
			if returnValue is "SkinParts":
				self.session.open(store_SkinParts_Browse.OpenScreen)
			elif returnValue is "MetrixColors":
				self.session.open(store_MetrixColors_Browse.OpenScreen)
			elif returnValue == "newest":
				self.session.open(store_SkinParts_Browse.OpenScreen,"%","%",_("Newest"),"date desc",False,pagelength=20)
			elif returnValue == "modified":
				self.session.open(store_SkinParts_Browse.OpenScreen,"%","%",_("Last Modified"),"date_modified desc",False,pagelength=20)
			elif returnValue == "mostdownloaded":
				self.session.open(store_SkinParts_Browse.OpenScreen,"%","%",_("Top 50 Downloads"),"downloads desc",False,pagelength=50)
			elif returnValue == "bundle":
				self.session.open(store_SkinParts_Browse.OpenScreen,"%","%",_("Bundles"),"date desc",False,pagelength=50,type="bundle")
			elif returnValue is "Extensions":
				self.session.open(store_Packages_Browse.OpenScreen,"2017",_("Skin Extensions"))
			elif self.sort == "suite":
				self.session.open(store_SkinParts_Browse.OpenScreen,"%",self["menu"].l.getCurrentSelection()[0][0],self["menu"].l.getCurrentSelection()[0][1])
			else:
				self.session.open(store_SkinParts_Browse.OpenScreen,self["menu"].l.getCurrentSelection()[0][0],"%",self["menu"].l.getCurrentSelection()[0][1])
		else:
			pass
		

	
	def CategoryListEntry(self,name,value="0",icon = "DEFAULT"):
		if icon == "DEFAULT":
			icon = self.sort
		png = "/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/"+icon+".png"
		res = [[value,name]]
		res.append(MultiContentEntryPixmapAlphaTest(pos=(25, 6), size=(170, 32), png=loadPNG(png)))
		
		res.append(MultiContentEntryText(pos=(80, 4), size=(405, 45), font=0, text=_(name)))
		return res
	
	def getCategories(self):
		menu = []
		menu.append(self.CategoryListEntry(_("Loading...")))
		metrixTools.callOnMainThread(self.setList,menu)
		try:
			data = metrixCore.getWeb(self.url,True)
			dom = parseString(data)
			menu = []
			## ADD STATIC PSEUDO CATEGORIES
			menu.append(self.CategoryListEntry(_("MetrixColors"), "MetrixColors","brush"))
			menu.append(self.CategoryListEntry(_("Newest SkinParts"), "newest","new"))
			menu.append(self.CategoryListEntry(_("Last Modified"), "modified","recent"))
			menu.append(self.CategoryListEntry(_("Top 50 Downloads"), "mostdownloaded","download"))
			menu.append(self.CategoryListEntry(_("Skin Extensions"), "Extensions","extensions"))
			menu.append(self.CategoryListEntry(_("Bundles"), "bundle","bundle"))
			metrixTools.callOnMainThread(self.setList,menu)
			for entry in dom.getElementsByTagName('entry'):
				item_id = str(entry.getAttributeNode('id').nodeValue)
				name = str(entry.getAttributeNode('name').nodeValue)
				menu.append(self.CategoryListEntry(name, item_id))
				metrixTools.callOnMainThread(self.setList,menu)
		except Exception, e:
			metrixTools.log("Error getting items via web",e)
			menu.append(self.CategoryListEntry(_("Error loading data!"), "-","-"))
			metrixTools.callOnMainThread(self.setList,menu)

	def setList(self,menu):
		self["menu"].setList(menu)

	def keyDown(self):
		self["menu"].instance.moveSelection(self["menu"].instance.moveDown)

	def keyUp(self):
		self["menu"].instance.moveSelection(self["menu"].instance.moveUp)

	def pageUp(self):
		self["menu"].instance.moveSelection(self["menu"].instance.pageUp)
		
	def pageDown(self):
		self["menu"].instance.moveSelection(self["menu"].instance.pageDown)	
	
	def exit(self):
		self.close()
			

	def showInfo(self, text="Information"):
			self.session.open(MessageBox, _(text), MessageBox.TYPE_INFO)
			

	def restartGUI(self, answer):
		if answer is True:
			config.plugins.MetrixUpdater.Reboot.value = 0
			config.plugins.MetrixUpdater.save()    
			configfile.save()
			self.session.open(TryQuitMainloop, 3)
		else:
			self.close()
			


class CategoryList(MenuList):
	def __init__(self, list):
		MenuList.__init__(self, list, False, eListboxPythonMultiContent)
		self.l.setItemHeight(50)
		self.l.setFont(0, gFont("SetrixHD", 26))
		self.l.setFont(1, gFont("Regular", 22))
		#ONLY FOR TRANSLATION
		if 1==2:
			cat = _("Education")
			cat = _("Movie & Media")
			cat = _("Network & Streaming")
			cat = _("News")
			cat = _("Program Guide")
			cat = _("Social")
			cat = _("Spinners")
			cat = _("Sports")
			
			cat = _("Radio")
			cat = _("Tweaks")
			cat = _("Recordings")
			cat = _("Communication")
			cat = _("System Extensions")
			cat = _("Utilities")
			cat = _("Development")
			cat = _("Picons")
			
			cat = _("Skin Extensions")
			cat = _("SkinParts Collections")
			cat = _("Drivers")
			cat = _("Channellists")
			cat = _("Kernel Modules")
			cat = _("Language Packs")
			cat = _("Weather")
			
			cat = _("Various")
			cat = _("My SkinParts")
			cat = _("Default Bugfixes")
			cat = _("VTI Specific")
			cat = _("OpenPLi Specific")
			cat = _("MetrixHD Default")
			
			
		