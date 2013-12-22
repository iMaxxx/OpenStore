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

import threading
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
import os
import urllib2
import urllib
from xml.dom.minidom import parseString
import gettext
from Components.GUIComponent import GUIComponent
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText,MultiContentEntryPixmapAlphaTest
from enigma import eListbox, RT_HALIGN_LEFT, RT_HALIGN_RIGHT
from enigma import eTimer, eDVBDB,eConsoleAppContainer
from enigma import ePicLoad,eListboxPythonMultiContent,gFont,addFont, loadPic, loadPNG
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import metrixDefaults
import store_SubmitRating
import time
import traceback
import metrixTools
import metrix_PackageTools
import metrixCore

#############################################################

config = metrixDefaults.loadDefaults()

def _(txt):
	t = gettext.dgettext("MyMetrix", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t





#######################################################################		
		

class OpenScreen(ConfigListScreen, Screen ):
	skin = """<screen name="MyMetrix-Store-Browse" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">
<eLabel position="0,0" size="1280,720" backgroundColor="#b0ffffff" zPosition="-50" />
<eLabel position="40,40" size="620,640" backgroundColor="#40111111" zPosition="-1" />
<eLabel position="660,60" size="575,600" backgroundColor="#40222222" zPosition="-1" />
<eLabel position="644,40" size="5,60" backgroundColor="#000000ff" />
<widget position="500,61" size="136,40" name="sort" foregroundColor="#00bbbbbb" font="Regular; 25" valign="center" backgroundColor="#40000000" transparent="1" halign="right" />
  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="695,619" size="174,33" text="%s" transparent="1" />
 <widget name="menu" position="40,117" scrollbarMode="showNever" size="620,560" transparent="1" foregroundColor="#00ffffff" backgroundColor="#40000000" />
  <widget position="55,55" size="470,50" name="title" noWrap="1" foregroundColor="#00ffffff" font="SetrixHD; 33" valign="center" transparent="1" backgroundColor="#40000000" />
  <widget position="679,585" size="533,32" name="isInstalled" foregroundColor="#00ffffff" font="Regular; 20" valign="center" halign="left" transparent="1" backgroundColor="#40000000" />
  <eLabel position="681,620" size="5,40" backgroundColor="#0000ff00" />
<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/star.png" position="1192,619" size="32,34" zPosition="1" alphatest="blend" />
  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="899,618" size="170,33" text="%s" transparent="1" />
<widget name="helperimage" position="669,150" size="550,310" zPosition="1" alphatest="blend" />
<widget position="674,62" size="546,50" name="itemname" foregroundColor="#00ffffff" font="SetrixHD; 35" valign="center" transparent="1" backgroundColor="#40000000" noWrap="1" />
 <widget position="1073,617" size="113,40" name="votes" foregroundColor="#00ffffff" font="Regular; 25" valign="center" halign="right" transparent="1" backgroundColor="#40000000" noWrap="1" />
<eLabel position="885,620" zPosition="1" size="5,40" backgroundColor="#00ffff00" />
<widget position="674,462" size="545,121" name="description" foregroundColor="#00ffffff" font="Regular; 17" valign="center" halign="left" transparent="1" backgroundColor="#40000000" />
<widget position="674,112" size="341,35" name="author" foregroundColor="#00bbbbbb" font="Regular; 25" valign="center" backgroundColor="#40000000" transparent="1" halign="left" />
<widget position="1019,113" size="200,35" name="date" foregroundColor="#00999999" font="Regular; 25" valign="center" backgroundColor="#40000000" transparent="1" halign="right" zPosition="1" />
 </screen>
""" %(_("Install "), _("Vote"))

	def __init__(self, session,category_id = "%",category_name=_("Plugins"),updates="0", limit = ""):
		Screen.__init__(self, session)
		self.limit = limit
		self["title"] = Label(_("OpenStore // "+category_name))
		self.orderby="date_created desc"
		self.url = metrixDefaults.URL_GET_PACKAGES
		self["itemname"] = Label()
		self["author"] = Label()
		self["votes"] = Label()
		self["date"] = Label()
		self["sort"] = Label(_("New"))
		self["description"] = Label()
		self["isInstalled"] = Label()
		self.category_id = category_id
		self.currentid = "0"
		self.image_id = ""
		self.image_token = ""
		self.storage_id = ""
		self.file_id = ""
		self.file_token = ""
		self.currentgroup = 'Packages'
		self.image = metrixDefaults.URI_IMAGE_LOADING
		self.icon = ''
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self["helperimage"] = Pixmap()
		self.thread_getDesigns = threading.Thread(target=self.threadworker,  args=())
		#THREAD ACTIONS
		self.getCatalog = True
		self.getEntry = True
		self.action_downloadPackage = False
		self.finished = False

		self["menu"] =  PackagesList([])

		self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions"], {
			"up": self.keyUp,
			"green": self.installPackage,
			"blue": self.changeSort,
			"down": self.keyDown,
			"right": self.pageDown,
			"left": self.pageUp,
			"yellow": self.openRating,
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
				self.getPackages()
			if self.getEntry == True:
				self.getEntry = False
				self.image = metrixTools.webPixmap(self["menu"].l.getCurrentSelection()[0][8],'openStoreImage',{'width':550})
				#self.icon = metrixTools.webPixmap(self["menu"].l.getCurrentSelection()[0][9],'openStoreIcon',{'width':100})
				metrixTools.callOnMainThread(self.refreshMeta)
			if self.action_downloadPackage == True:
				self.action_downloadPackage = False
				self.downloadPackage()
				
			time.sleep(1)
				
		
		
	def getPackages(self,isactive=""):
		menu = []
		try:
			params = {'restrictions':metrixTools.getRestrictions(),
					  'orderby':self.orderby+" "+self.limit,
					  'category_id':str(self.category_id)}
			data = metrixCore.getWeb(self.url,True,params)

			dom = parseString(data)
			for design in dom.getElementsByTagName('entry'):
				item_id = str(design.getAttributeNode('id').nodeValue)
				name = str(design.getAttributeNode('name').nodeValue)
				author = str(design.getAttributeNode('author').nodeValue)
				version = str(design.getAttributeNode('version').nodeValue)
				rating = str(design.getAttributeNode('rating').nodeValue)
				date = str(design.getAttributeNode('date_created').nodeValue)
				date_modified = str(design.getAttributeNode('date_modified').nodeValue)
				item_type = str(design.getAttributeNode('type').nodeValue)
				file_link = str(design.getAttributeNode('file_link').nodeValue)
				image_link = str(design.getAttributeNode('image_link').nodeValue)
				icon_link = str(design.getAttributeNode('icon_link').nodeValue)
				downloads = str(design.getAttributeNode('downloads').nodeValue)
				total_votes = str(design.getAttributeNode('total_votes').nodeValue)
				description = str(design.getAttributeNode('description').nodeValue)
				previouspackage = str(design.getAttributeNode('previouspackage').nodeValue)
				path = metrixDefaults.pathRoot()+"packages/"+item_id
				menu.append(self.PackagesListEntry(item_id,name,author,rating,date,version,total_votes,item_type,image_link,icon_link,description,file_link,downloads,previouspackage,date_modified))
				metrixTools.callOnMainThread(self.setList,menu)
			if len(menu) < 1:
				menu.append(self.PackagesListEntry("-",_("No Packages available!")))
				metrixTools.callOnMainThread(self.setList,menu)
		except Exception, e:
			metrixTools.log('Error getting packages via web',e)
			menu.append(self.PackagesListEntry("-",_("Error loading data!")))
			metrixTools.callOnMainThread(self.setList,menu)

	def PackagesListEntry(self,item_id,name,author="",rating="",date="",version="",total_votes="",item_type="",image_link="",icon_link="",description="",file_link="",downloads="",previouspackage="0",date_modified=""):
		res = [[item_id,name,author,rating,date,version,total_votes,item_type,image_link,icon_link,description,file_link,downloads,date_modified]]
		path = metrixDefaults.pathRoot()+"packages/"+str(item_id)
		if os.path.exists(path):
			pngtype = metrixDefaults.PLUGIN_DIR + "images/package-on.png"
		else:
			pngtype = metrixDefaults.PLUGIN_DIR + "images/package.png"
		
		png = metrixDefaults.PLUGIN_DIR + "images/vote"+rating+".png"
		pngicon = metrixTools.webPixmap(icon_link,"openStoreIcon"+str(item_id),{'width':54})
		res.append(MultiContentEntryPixmapAlphaTest(pos=(445, 9), size=(185, 32), png=loadPNG(png)))
		res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 1), size=(54, 54), png=loadPNG(pngicon)))
		res.append(MultiContentEntryText(pos=(70, 4), size=(365, 45), font=0, text=name))
		return res
		
	def installPackage(self):
		self.action_downloadPackage = True
		
	def downloadPackage(self):
		self.updateStatus(_("Installing..."))
		download_link = self["menu"].l.getCurrentSelection()[0][11]
		type = self["menu"].l.getCurrentSelection()[0][7]
		if str(type) == "piconrepo": #XPicon Repository
			config.plugins.MyMetrix.XPiconsRepository.value = self["menu"].l.getCurrentSelection()[0][0]
			config.plugins.MyMetrix.XPiconsRepositoryName.value = self["menu"].l.getCurrentSelection()[0][1]
			config.plugins.MyMetrix.save()    
			configfile.save()
			self.updateStatus(_("Repo successfully selected!"))
		else:
			try:
				#data = metrixCore.getWeb(download_link, True)
				instStatus = metrix_PackageTools.installPackage(download_link,True,True)
				if instStatus:
					self.updateStatus(_("Installation complete!"))
					config.plugins.MetrixUpdater.Reboot.value = 1
					config.plugins.MetrixUpdater.save()    
					configfile.save()
				else:
					self.updateStatus(_("Error installing package!"))
			except:
				pass
		
	def updateStatus(self,message):
		metrixTools.callOnMainThread(self["isInstalled"].setText,message)
				

	def updateMeta(self):
		try:
			self["itemname"].setText(str(self["menu"].l.getCurrentSelection()[0][1]))
			self.setTitle(_("OpenStore // "+self["menu"].l.getCurrentSelection()[0][1]))
			self["author"].setText(_("loading..."))
			self["votes"].setText(str(self["menu"].l.getCurrentSelection()[0][6]))
			self["date"].setText(str(self["menu"].l.getCurrentSelection()[0][5]))
			self["description"].setText(str(self["menu"].l.getCurrentSelection()[0][10]))
			self.currentid = str(self["menu"].l.getCurrentSelection()[0][0])
			self.currenttype = str(self["menu"].l.getCurrentSelection()[0][7])
			
			id = self.currentid
			type = self.currenttype
			path = metrixDefaults.pathRoot()+"packages/"+str(self.currentid)+"/"
			if os.path.exists(path):
				self["isInstalled"].setText("Already installed!")
			else:
				self["isInstalled"].setText("")
		except:
			pass
	
	def UpdatePicture(self):
		self.PicLoad.PictureData.get().append(self.DecodePicture)
		self.onLayoutFinish.append(self.ShowPicture)
	
	def ShowPicture(self):
		self.PicLoad.setPara([self["helperimage"].instance.size().width(),self["helperimage"].instance.size().height(),self.Scale[0],self.Scale[1],0,1,"#002C2C39"])
		self.PicLoad.startDecode(self.image)
		try:
			if self["menu"].l.getCurrentSelection()[0][2] != "":
				self["author"].setText(_("by " + str(self["menu"].l.getCurrentSelection()[0][2])))
		except:
			pass
		#print "showing image"
		
	def DecodePicture(self, PicInfo = ""):
		#print "decoding picture"
		ptr = self.PicLoad.getData()
		self["helperimage"].instance.setPixmap(ptr)	

	def UpdateComponents(self):
		self.UpdatePicture()
		self.updateMeta()
		
	def setList(self,menu):
		self["menu"].setList(menu)
		self.getEntry = True
		
	def refreshMeta(self):
		self.updateMeta()
		self.ShowPicture()
		
	def pageUp(self):
		self["menu"].instance.moveSelection(self["menu"].instance.pageUp)
		self.getEntry = True
		
	def pageDown(self):
		self["menu"].instance.moveSelection(self["menu"].instance.pageDown)	
		self.getEntry = True
		
	def keyDown(self):
		self["menu"].instance.moveSelection(self["menu"].instance.moveDown)
		self.getEntry = True
		
	def keyUp(self):
		self["menu"].instance.moveSelection(self["menu"].instance.moveUp)
		self.getEntry = True
	
	def save(self):
		config.plugins.MyMetrix.Color.save()
		configfile.save()
		self.exit()

	
	def exit(self):
		self.finished = True
		self.thread_getDesigns.join()
		self.close()
	
	def openRating(self):
		self.session.open(store_SubmitRating.OpenScreen,self.currentid,self.currentgroup)
		
		self.getCatalog = True
		self.getEntry = True
		

	def changeSort(self):
		if self.orderby=="date_created desc":
			self.orderby="rating.total_value desc"
			self["sort"].setText("Charts")
		elif self.orderby=="rating.total_value desc":
			self.orderby="rating.total_votes desc"
			self["sort"].setText("Popular")
		elif self.orderby=="rating.total_votes desc":
			self.orderby="date_created desc"
			self["sort"].setText("New")
		
		self.getCatalog = True
		self.getEntry = True

		
class PackagesList(MenuList):
	def __init__(self, list):
		MenuList.__init__(self, list, False, eListboxPythonMultiContent)
		self.l.setItemHeight(56)
		self.l.setFont(0, gFont("SetrixHD", 26))
		self.l.setFont(1, gFont("Regular", 22))
		
	

