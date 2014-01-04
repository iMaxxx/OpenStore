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
from os import environ, listdir, remove, rename, system
from skin import parseColor
from Components.Pixmap import Pixmap
from Components.Label import Label
from xml.dom.minidom import parseString
import gettext
from Components.GUIComponent import GUIComponent
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText,MultiContentEntryPixmapAlphaTest,MultiContentEntryPixmapAlphaBlend
from enigma import eListbox, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER
from enigma import ePicLoad,eListboxPythonMultiContent,gFont,addFont, loadPic, loadPNG
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import metrixDefaults
import store_Packages_Browse
import threading
import traceback
import time
import metrixTools
import metrixCore
import store_Settings

#############################################################

config = metrixDefaults.loadDefaults()

def _(txt):
	t = gettext.dgettext("MyMetrix", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t


#######################################################################		
		

class OpenScreen(ConfigListScreen, Screen):
	skin = """<screen name="OpenStore-Categories" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">
<eLabel position="0,0" size="1280,720" backgroundColor="#b0ffffff" zPosition="-50" />
<eLabel position="30,25" size="1222,668" backgroundColor="#40111111" zPosition="-1" />
<ePixmap position="60,40" size="200,70" transparent="1" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/openstore-logo-small.png" />
<widget name="list1" backgroundColorSelected="#00009cff" foregroundColorSelected="#00ffffff" position="60,125" scrollbarMode="showNever" size="290,568" transparent="1" foregroundColor="#00ffffff" backgroundColor="#40000000" />
<widget name="list2" backgroundColorSelected="#00009cff" foregroundColorSelected="#00ffffff" position="350,125" scrollbarMode="showNever" size="290,568" transparent="1" foregroundColor="#00ffffff" backgroundColor="#40000000" />
<widget name="list3" backgroundColorSelected="#00009cff" foregroundColorSelected="#00ffffff" position="639,125" scrollbarMode="showNever" size="290,568" transparent="1" foregroundColor="#00ffffff" backgroundColor="#40000000" />
<widget name="list4" backgroundColorSelected="#00009cff" foregroundColorSelected="#00ffffff" position="930,125" scrollbarMode="showNever" size="290,568" transparent="1" foregroundColor="#00ffffff" backgroundColor="#40000000" />
<eLabel name="" position="1214,25" size="5,60" backgroundColor="blue" />
<widget position="766,36" size="438,51" name="title" foregroundColor="#00ffffff" font="SetrixHD; 28" valign="center" transparent="1" backgroundColor="#40000000" halign="right" text="Settings" /></screen>
"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self["title"] = Label(_("OpenStore"))
		
		self.thread_updater = threading.Thread(target=self.threadworker,  args=())
		
		#THREAD ACTIONS
		self.getCatalog = True
		self.finished = False
		
		self["list1"] =  CategoriesList([])
		self["list2"] =  CategoriesList([])
		self["list3"] =  CategoriesList([])
		self["list4"] =  CategoriesList([])
		self.listnull = CategoriesList([])
		self.clist = [[],[],[]]
		self.columns = 4
		self.rows = 3
		self.selectedColumn = 1
		self.selectedRow = 1
		
		list = []
		list.append(self.CategoryEntry(0,_("Loading..."),"/img/categories/refresh.png"))
		
		self["list1"].setList(list)
		self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions"], {
			"left": self.keyLeft,
			"right": self.keyRight,
			"up": self.keyUp,
			"upRepeated": self.keyUp,
			"blue":self.openSettings,
			"ok": self.openCategory,
			"down": self.keyDown,
			"downRepeated": self.keyDown,
			"cancel": self.exit}, -1)
		self.setTitle("OpenStore")
		self.onLayoutFinish.append(self.startThread)
		
		
		
	def startThread(self):	
		self.thread_updater.daemon = True
		self.thread_updater.start()
		
	#THREAD WORKER
	def threadworker(self):
		while(self.finished == False):
			if self.getCatalog == True:
				self.getCatalog = False
				self.getCategories()
			time.sleep(1)
	
		
	def openCategory(self):
		category_id = self["list"+str(self.selectedColumn)].l.getCurrentSelection()[0][0]
		category_name = self["list"+str(self.selectedColumn)].l.getCurrentSelection()[0][1]
		onlyupdates = self["list"+str(self.selectedColumn)].l.getCurrentSelection()[0][3]
		onlyinstalled = self["list"+str(self.selectedColumn)].l.getCurrentSelection()[0][4]
		orderby = self["list"+str(self.selectedColumn)].l.getCurrentSelection()[0][5]
		limit = self["list"+str(self.selectedColumn)].l.getCurrentSelection()[0][6]
		self.session.open(store_Packages_Browse.OpenScreen,category_id,category_name,onlyupdates=onlyupdates,onlyinstalled=onlyinstalled,orderby=orderby,limit=limit)
		
	def openSettings(self):
		self.session.open(store_Settings.OpenScreen)
		self.selectedColumn = 1
		self.selectedRow = 1
		self.getCatalog = True
		

		

	def CategoryEntry(self,column_id, item_id,name,image_link="",onlyupdates=False,onlyinstalled=False,orderby="",limit=""):
		res = [[item_id,name,image_link,onlyupdates,onlyinstalled,orderby,limit]]
		pngicon = metrixTools.webPixmap(metrixDefaults.URL_STORE + str(image_link),"openStoreImage-"+str(column_id)+str(item_id))
		res.append(MultiContentEntryPixmapAlphaBlend(pos=(81, 1), size=(128, 128), png=loadPNG(pngicon)))
		res.append(MultiContentEntryText(pos=(0, 128), size=(290, 40), font=0, text=_(name),flags = RT_HALIGN_CENTER))
		return res
	
	def getCategories(self):
		list = [[],[],[],[],[]]
		selectionEnabled = False
		i = 1

		list[i].append(self.CategoryEntry(i,"%", _("Installed"), "/img/categories/installed.png",onlyinstalled=True,orderby="date_modified desc",))
		metrixTools.callOnMainThread(self.setList,list[i],i)
		i += 1
		list[i].append(self.CategoryEntry(i,"%", _("Updates"), "/img/categories/updates.png",onlyupdates=True,orderby="date_modified desc",))
		metrixTools.callOnMainThread(self.setList,list[i],i)
		i += 1
		list[i].append(self.CategoryEntry(i,"%", _("New"), "/img/categories/new.png",orderby="date_created desc", limit="LIMIT 20"))
		metrixTools.callOnMainThread(self.setList,list[i],i)
		i += 1
		list[i].append(self.CategoryEntry(i,"%", _("Last Modified"), "/img/categories/recent.png",orderby="date_modified desc", limit="LIMIT 20"))
		metrixTools.callOnMainThread(self.setList,list[i],i)
		i = 1
		list[i].append(self.CategoryEntry(i,"%%", _("Top 50 Downloads"), "/img/categories/top50.png",orderby="rating desc", limit="LIMIT 50"))
		metrixTools.callOnMainThread(self.setList,list[i],i)
		i += 1
		if config.plugins.MyMetrix.Store.Plugin_Developer.value:
			list[i].append(self.CategoryEntry(i,9999, _("My Packages"), "/img/categories/my.png",orderby="date_modified desc",))
			metrixTools.callOnMainThread(self.setList,list[i],i)
			i += 1
		try:
			data = metrixCore.getWeb(metrixDefaults.URL_GET_CATEGORIES,True)
			dom = parseString(data)
			
			for entry in dom.getElementsByTagName('entry'):
				item_id = str(entry.getAttributeNode('id').nodeValue)
				name = str(entry.getAttributeNode('name').nodeValue)
				image_link = str(entry.getAttributeNode('image').nodeValue)
				list[i].append(self.CategoryEntry(i,item_id, name, image_link,orderby="date_created desc"))
				metrixTools.callOnMainThread(self.setList,list[i],i)
				i += 1
				if i == self.columns+1:
					i = 1
			metrixTools.callOnMainThread(self.setMaxRows,len(list[1])+1)
		except Exception,e:
			showInfo("Check your internet connection")
			metrixTools.log("Error getting categories via web!",e)
			
	def setMaxRows(self,rows):
		self.rows = rows
			
	def setList(self,list,listnumber,selectionEnabled=False):
		self["list"+str(listnumber)].setList(list)
		self.updateSelection()
		

	def keyDown(self):
		if self.selectedRow < self.rows:
			self.selectedRow += 1
			self.updateSelection()
		
	def keyUp(self):
		if self.selectedRow > 1:
			self.selectedRow -= 1
			self.updateSelection()
		
	def keyRight(self):
		if self.selectedColumn < self.columns:
			self.selectedColumn += 1
			self.updateSelection()
		else:
			self.selectedColumn = 1
			self.selectedRow += 1
			self.updateSelection()
		
	def keyLeft(self):
		if self.selectedColumn > 1:
			self.selectedColumn -= 1
			self.updateSelection()
	
	def updateSelection(self):
		if self.selectedRow > 1:
			if self.selectedRow > len(self["list"+str(self.selectedColumn)].list): 
				self.selectedRow = 1
		for i in range(1,self.columns+1):
			if i == self.selectedColumn:
				selectionEnabled = True
			else:
				selectionEnabled = False
			self["list"+str(i)].selectionEnabled(selectionEnabled)
			self["list"+str(i)].instance.moveSelectionTo(self.selectedRow-1)
			if self.selectedRow > len(self["list"+str(i)].list) and self.selectedRow == 4 and self["list"+str(i)].list != []:
				self.clist[i-2] = self["list"+str(i)].list
				self["list"+str(i)].setList([])
			elif self["list"+str(i)].list == [] and self.selectedRow == 3:
				self["list"+str(i)].setList(self.clist[i-2])
				self.clist[i-2] = []


	def exit(self):
		self.finished = True
		self.thread_updater.join()
		if config.plugins.MetrixUpdater.Reboot.value == 1:
			restartbox = self.session.openWithCallback(self.restartGUI,MessageBox,_("To apply the new software you have to restart your device!\nDo you want to restart now?"), MessageBox.TYPE_YESNO)
		else:
			self.close()
		
	def restartGUI(self, answer):
		if answer is True:
			config.plugins.MetrixUpdater.Reboot.value = 0
			config.plugins.MetrixUpdater.save()    
			configfile.save()
			self.session.open(TryQuitMainloop, 3)
		else:
			self.close()
		
	def showInfo(self, text="Information"):
			self.session.open(MessageBox, _(text), MessageBox.TYPE_INFO)
			
	

class CategoriesList(MenuList):
	def __init__(self, list):
		MenuList.__init__(self, list, False, eListboxPythonMultiContent)
		self.l.setItemHeight(173)
		self.l.setFont(0, gFont("SetrixHD", 30) )
		#for translation
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
			
			
		