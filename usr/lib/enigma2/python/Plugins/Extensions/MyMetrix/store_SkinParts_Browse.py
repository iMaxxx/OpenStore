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
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Pixmap import Pixmap
import os
from xml.dom.minidom import parseString
import gettext
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText,MultiContentEntryPixmapAlphaTest
from enigma import eListbox, RT_HALIGN_LEFT, RT_HALIGN_RIGHT
from enigma import ePicLoad,eListboxPythonMultiContent,gFont,addFont, loadPic, loadPNG
import metrixDefaults
import store_SubmitRating
import time
import metrixTools
import metrix_SkinPartTools
import traceback
import metrixCore
from twisted.internet import reactor, threads

#############################################################

config = metrixDefaults.loadDefaults()

def _(txt):
	t = gettext.dgettext("MyMetrix", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t


class OpenScreen(ConfigListScreen, Screen):
	skin = """
<screen name="OpenStore-SkinParts-Browse" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">
<eLabel position="0,0" size="1280,720" backgroundColor="#b0ffffff" zPosition="-50" />
<eLabel position="40,40" size="620,640" backgroundColor="#40111111" zPosition="-1" />
<eLabel position="660,60" size="575,600" backgroundColor="#40222222" zPosition="-1" />
<eLabel position="644,40" size="5,60" backgroundColor="#000000ff" />
<widget position="500,61" size="136,40" name="sort" foregroundColor="#00bbbbbb" font="Regular; 25" valign="center" backgroundColor="#40000000" transparent="1" halign="right" />
  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="695,619" size="174,33" text="%s" transparent="1" />
 <widget name="menu" backgroundColorSelected="#00555555" foregroundColorSelected="#00ffffff" position="55,122" scrollbarMode="showNever" size="605,555" transparent="1" foregroundColor="#00ffffff" backgroundColor="#40000000" />
  <widget position="55,55" size="453,50" name="title" noWrap="1" foregroundColor="#00ffffff" font="SetrixHD; 33" valign="center" transparent="1" backgroundColor="#40000000" />
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



	def __init__(self, session,screenname = "%",suite_id="%",title="SkinParts",orderby="date desc",showChangeSort=True,pagelength=0,type="%"):
		Screen.__init__(self, session)
		self["title"] = Label(_("OpenStore // "+_(screenname)))
		if screenname == "%":
			self["title"] = Label(_("OpenStore // "+_(title)))
		
		self.orderby = orderby
		self.screenname = screenname
		self.suite_id = suite_id
		self.pagelength = pagelength
		self.type = type
		self.session = session
		self["itemname"] = Label()
		self["author"] = Label(_("loading..."))
		self["votes"] = Label()
		self["date"] = Label()
		if showChangeSort:
			self["sort"] = Label(_("New"))
		else:
			self["sort"] = Label("")
		self["description"] = Label()
		self["isInstalled"] = Label()
		self.currentauthor = ""
		self.currentid = "0"
		self.image_id = ""
		self.image_token = ""
		self.currenttype = "widget"
		self.currentgroup = 'SkinParts'
		self.picPath = metrixDefaults.URI_IMAGE_LOADING
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self["helperimage"] = Pixmap()
		
		#THREAD ACTIONS
		self.finished = False
		self.getCatalog = True
		self.getEntry = False
		self.action_downloadSkinPart = False
		self.thread_updater = threading.Thread(target=self.threadworker,  args=())
		self.thread_updater.daemon = True
		
		self["menu"] =  SkinPartsList([])
		self.menulist = []                    
		self.menulist.append(self.SkinPartsListEntry("-",_("loading, please wait...")))
		self["menu"].setList(self.menulist)
		
		
		self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions"], {											
			"up": self.keyUp,
			"ok": self.selectItem,
			"green": self.installSkinPart,
			"blue": self.changeSort,
			"down": self.keyDown,
			"right": self.pageDown,
			"left": self.pageUp,
			"yellow": self.openRating,
			"cancel": self.exit}, -1)
		
		self.UpdatePicture()
		self.onLayoutFinish.append(self.startThread)
		
		
	def startThread(self):
		self.thread_updater.start()
		
		
	#THREAD WORKER
	def threadworker(self):
		while(self.finished==False):
			if self.getCatalog == True:
				self.getCatalog = False
				self.getSkinParts()
			if self.getEntry == True:
				self.getEntry = False
				try:
					self.picPath = metrixTools.webPixmap(self["menu"].l.getCurrentSelection()[0][13] + "&width=550")
				except:
					pass
				metrixTools.callOnMainThread(self.refreshMeta)
			if self.action_downloadSkinPart == True:
				self.action_downloadSkinPart = False
				self.downloadSkinPart()
			time.sleep(1)
				
		
		
	def getSkinParts(self,isactive=""):
		menu = []
		
		try:
			if self.pagelength == 0:
				params = {'screenname':self.screenname,
						'suite_id':self.suite_id,
						'developer':str(config.plugins.MyMetrix.Store.SkinPart_Developer.value),
						'restrictions':metrixTools.getRestrictions(),
						'orderby':self.orderby,
						'type':str(self.type)}
			else:
				params = {'screenname':self.screenname,
						'suite_id':self.suite_id,
						'orderby':self.orderby,
						'restrictions':metrixTools.getRestrictions(),
						'developer':str(config.plugins.MyMetrix.Store.SkinPart_Developer.value),
						'pagelength':str(self.pagelength),
						'type':str(self.type),
						'pagenum':'1'}
			data = metrixCore.getWeb(metrixDefaults.URL_GET_SKINPARTS,True,params)
			dom = parseString(data)
			for entry in dom.getElementsByTagName('entry'):
				item_id = str(entry.getAttributeNode('id').nodeValue)
				name = str(entry.getAttributeNode('name').nodeValue)
				author = str(entry.getAttributeNode('author').nodeValue)
				version = str(entry.getAttributeNode('version').nodeValue)
				rating = str(entry.getAttributeNode('rating').nodeValue)
				date = str(entry.getAttributeNode('date').nodeValue)
				item_type = str(entry.getAttributeNode('type').nodeValue)
				screenname = str(entry.getAttributeNode('screenname').nodeValue)
				image_id = str(entry.getAttributeNode('image_id').nodeValue)
				image_token = str(entry.getAttributeNode('image_token').nodeValue)
				total_votes = str(entry.getAttributeNode('total_votes').nodeValue)
				description = str(entry.getAttributeNode('description').nodeValue)
				build = str(entry.getAttributeNode('build').nodeValue)
				image_link = str(entry.getAttributeNode('image_link').nodeValue)
				downloads = str(entry.getAttributeNode('downloads').nodeValue)
				menu.append(self.SkinPartsListEntry(item_id,name,author,rating,date,version,total_votes,item_type,image_id,image_token,description,screenname,image_link,isactive,build))
				metrixTools.callOnMainThread(self.setList,menu)
			if len(menu) < 1:
				self.picPath = metrixDefaults.PLUGIN_DIR + "images/sponsor.png"
				metrixTools.callOnMainThread(self.setList,menu)
		except Exception, e:
			metrixTools.log("Error getting SkinParts", e)
			self.picPath = metrixDefaults.PLUGIN_DIR + "images/sponsor.png"
			metrixTools.callOnMainThread (self.setList,menu)
		 
	def setList(self,menu):
		self["menu"].setList(menu)
		self.getEntry = True
		
	def refreshMeta(self):
		self.updateMeta()
		self.ShowPicture()

	def SkinPartsListEntry(self,item_id,name,author="",rating="",date="",version="",total_votes="",item_type="",image_id="",image_token="",description="",screenname="",image_link="",isactive="",build="0"):
		res = [[item_id,name,author,rating,date,version,total_votes,item_type,image_id,image_token,description,screenname,isactive,image_link,build]]
		path = config.plugins.MyMetrix.SkinPartPath.value +item_type+"s/active/"+item_type+"_"+str(item_id)+"/"
		if os.path.exists(path):
			pngtype = metrixDefaults.PLUGIN_DIR + "images/"+item_type+"-on.png"
			res.append(MultiContentEntryText(pos=(40, 4), size=(367, 45), font=0, text=name,color=metrixDefaults.COLOR_INSTALLED))
		else:
			pngtype = metrixDefaults.PLUGIN_DIR + "images/"+item_type+".png"
			res.append(MultiContentEntryText(pos=(40, 4), size=(367, 45), font=0, text=name))
		
		png = metrixDefaults.PLUGIN_DIR + "images/vote"+rating+".png"
		res.append(MultiContentEntryPixmapAlphaTest(pos=(412, 9), size=(170, 32), png=loadPNG(png)))
		res.append(MultiContentEntryPixmapAlphaTest(pos=(3, 7), size=(32, 32), png=loadPNG(pngtype)))
		
		return res
	

		
	def installSkinPart(self):
		self.action_downloadSkinPart = True
		
	def downloadSkinPart(self):
		metrixTools.callOnMainThread(self["isInstalled"].setText,"Installing...")
		try:
			id = self.currentid
			type = self.currenttype
			author = self.currentauthor
			type = str(self["menu"].l.getCurrentSelection()[0][7])
			image_link = str(self["menu"].l.getCurrentSelection()[0][13])
			if type == "bundle":
				metrix_SkinPartTools.installBundle(id)
			else:
				metrix_SkinPartTools.installSkinPart(id,type,author,image_link)
			getCatalog = True
			getEntry = True
			metrixTools.callOnMainThread(self["isInstalled"].setText,"Installation successful!")
		except Exception, e:
			metrixTools.log("Error installing SkinPart "+id,e)
			metrixTools.callOnMainThread(self["isInstalled"].setText,"Error during installation!")
			

	def updateMeta(self):
		try:
			self["itemname"].setText(_(str(self["menu"].l.getCurrentSelection()[0][1])))
			self["author"].setText(_("loading..."))
			self["votes"].setText(str(self["menu"].l.getCurrentSelection()[0][6]))
			self["date"].setText(str(self["menu"].l.getCurrentSelection()[0][5]))
			self["description"].setText(str(self["menu"].l.getCurrentSelection()[0][10]))
			self.currentid = str(self["menu"].l.getCurrentSelection()[0][0])
			self.currenttype = str(self["menu"].l.getCurrentSelection()[0][7])
			self.currentauthor = str(self["menu"].l.getCurrentSelection()[0][2])
			
			id = self.currentid
			type = self.currenttype
			path = config.plugins.MyMetrix.SkinPartPath.value +type+"s/active/"+type+"_"+str(id)+"/"
			if os.path.exists(path):
				self["isInstalled"].setText("Already installed!")
			else:
				self["isInstalled"].setText("")
		except Exception, e:
			self["itemname"].setText(_("No SkinParts available!"))
			self["author"].setText("")
			metrixTools.log("No SkinParts availbable in this view")
	
	def UpdatePicture(self):
		self.PicLoad.PictureData.get().append(self.DecodePicture)
		self.onLayoutFinish.append(self.ShowPicture)
	
	def ShowPicture(self):
		self.PicLoad.setPara([self["helperimage"].instance.size().width(),self["helperimage"].instance.size().height(),self.Scale[0],self.Scale[1],0,1,"#002C2C39"])
		self.PicLoad.startDecode(self.picPath)
		if self.currentauthor != "":
			self["author"].setText(_("by") + " " + str(self.currentauthor))
		
	def DecodePicture(self, PicInfo = ""):
		#print "decoding picture"
		ptr = self.PicLoad.getData()
		self["helperimage"].instance.setPixmap(ptr)	

	def UpdateComponents(self):
		self.UpdatePicture()
		self.updateMeta()
		
	def selectItem(self):
		self.getEntry = True
		
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
		self.exit()

	
	def exit(self):
		self.finished = True
		self.thread_updater.join()
		self.close()
	
	def openRating(self):
		self.session.open(store_SubmitRating.OpenScreen,self.currentid,self.currentgroup,str(self["menu"].l.getCurrentSelection()[0][1]))
		self.getCatalog = True
		self.getEntry = True
		
	def showInfo(self, text="Information"):
			self.session.open(MessageBox, _(text), MessageBox.TYPE_INFO)
			

	def changeSort(self):
		if self.orderby=="date desc":
			self.orderby="rating.total_value desc"
			self["sort"].setText("Charts")
		elif self.orderby=="rating.total_value desc":
			self.orderby="rating.total_votes desc"
			self["sort"].setText("Popular")
		elif self.orderby=="rating.total_votes desc":
			self.orderby="date desc"
			self["sort"].setText("New")
		self.getCatalog = True
		self.getEntry = True
		
		
		
class SkinPartsList(MenuList):
	def __init__(self, list):
		MenuList.__init__(self, list, False, eListboxPythonMultiContent)
		self.l.setItemHeight(50)
		self.l.setFont(0, gFont("SetrixHD", 24))
		self.l.setFont(1, gFont("Regular", 22))
		



