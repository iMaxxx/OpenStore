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
import socket
import base64
from encode import multipart_encode
from streaminghttp import register_openers
import cookielib
from xml.dom.minidom import parseString
import gettext
import MultipartPostHandler
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
import os
from skin import parseColor
from Components.Pixmap import Pixmap
from Components.Label import Label
import urllib
import gettext
from enigma import ePicLoad
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import metrix_MetrixColors
import store_ConnectDevice
import store_DisconnectDevice
import metrixDefaults
from shutil import copytree,rmtree
import metrixCore
#############################################################


config = metrixDefaults.loadDefaults()

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("MyMetrix", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/MyMetrix/locale/"))

def _(txt):
	t = gettext.dgettext("MyMetrix", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

def translateBlock(block):
	for x in TranslationHelper:
		if block.__contains__(x[0]):
			block = block.replace(x[0], x[1])
	return block




#######################################################################			

class OpenScreen(ConfigListScreen, Screen):
	skin = """<screen name="MyMetrix-Setup" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="#b0ffffff">
    <eLabel position="40,40" size="620,640" backgroundColor="#40000000" zPosition="-1" />
  <eLabel position="660,71" size="575,575" backgroundColor="#40111111" zPosition="-1" />
<widget name="metrixVersion" position="329,640" size="315,35" font="Regular; 20" backgroundColor="#40000000" transparent="1" halign="right" />
<eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="75,641" size="250,33" text="%s" transparent="1" />
 <widget name="config" position="54,110" itemHeight="30" scrollbarMode="showOnDemand" size="590,510" transparent="1" foregroundColor="#00ffffff" backgroundColor="#40000000" />
  <eLabel position="54,51" size="348,50" text="MyMetrix" font="Regular; 40" valign="center" transparent="1" backgroundColor="#40000000" />
  <eLabel position="273,50" size="349,50" text="%s" foregroundColor="#00ffffff" font="Regular; 30" valign="center" backgroundColor="#40000000" transparent="1" halign="left" />
  <eLabel position="62,639" size="5,40" backgroundColor="#00ff0000" />
  <ePixmap position="671,149" size="550,310" zPosition="3" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/sponsor.png" />

<widget name="avatar" position="1109,526" size="96,96" />
<eLabel text="Sponsor" position="675,85" size="500,52" backgroundColor="#40000000" foregroundColor="#00ffffff" transparent="1" font="Regular; 30" />
<eLabel text="www.open-store.net" position="675,492" size="426,45" backgroundColor="#40000000" foregroundColor="#00ffffff" transparent="1" font="Regular; 24" />
<widget name="username" position="692,553" size="400,50" font="Regular; 30" transparent="1" halign="right" backgroundColor="#40000000" foregroundColor="#00ffffff" />

</screen>
""" %(_("Discard"), _("Settings"))

	def __init__(self, session, args = None):
		self.skinPartPath = config.plugins.MyMetrix.SkinPartPath.value
		self.skin_lines = []
		Screen.__init__(self, session)
		self.session = session
		self.version = "v"+metrixDefaults.VERSION
		self.picPath = metrixDefaults.PLUGIN_DIR + "images/not-connected.png"
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self["avatar"] = Pixmap()
		self["username"] = Label()
		self["metrixVersion"] = Label(_(self.version + " - open-store.net"))
		if config.plugins.MetrixUpdater.Reboot.value == 1:
			self["metrixVersion"] = Label(self.version + _(" - (Reboot required)"))
		list = []
		
		
		#list.append(getConfigListEntry(_("Update interval (min)"), config.plugins.MetrixUpdater.refreshInterval))
		
		list.append(getConfigListEntry(_("Weather --------------------------------------------------------------------------------------")))
		
		list.append(getConfigListEntry(_("MetrixWeather ID"), config.plugins.MetrixWeather.woeid))
		list.append(getConfigListEntry(_("Unit"), config.plugins.MetrixWeather.tempUnit))
		#list.append(getConfigListEntry(_("Refresh Interval (min)"), config.plugins.MetrixWeather.refreshInterval))
		list.append(getConfigListEntry(_(" ")))
		list.append(getConfigListEntry(_("SkinPart tools -------------------------------------------------------------------------------------")))
		list.append(getConfigListEntry(_("Negate image downloads"), config.plugins.MyMetrix.Color.SkinPartImagesNegate))
		list.append(getConfigListEntry(_("Greyscale image downloads"), config.plugins.MyMetrix.Color.SkinPartImagesGreyscale))
		list.append(getConfigListEntry(_("image downloads depth"), config.plugins.MyMetrix.Color.SkinPartImagesDepth))
		
		list.append(getConfigListEntry(_(" ")))
		list.append(getConfigListEntry(_("Skin -------------------------------------------------------------------------------------------------")))
		list.append(getConfigListEntry(_("SkinParts location (regenerate skin!)"), config.plugins.MyMetrix.SkinPartPath))
		#list.append(getConfigListEntry(_("SkinPart updates"), config.plugins.MyMetrix.AutoUpdateSkinParts))
		#list.append(getConfigListEntry(_("Show update notification bar"), config.plugins.MetrixUpdater.UpdatePopup_Packages))
		#list.append(getConfigListEntry(_("Show intro page"), config.plugins.MyMetrix.showFirstRun))
		list.append(getConfigListEntry(_("Skin template"), config.plugins.MyMetrix.Templates))
		list.append(getConfigListEntry(_("My skin name"), config.plugins.MyMetrix.SkinName))
		list.append(getConfigListEntry(_("Only use SkinParts in InfoBar"), config.plugins.MyMetrix.CleanInfoBar))
		
		#list.append(getConfigListEntry(_("Skin target folder"), config.plugins.MyMetrix.SkinXMLPath))
		
		list.append(getConfigListEntry(" "))
		list.append(getConfigListEntry(_("Developer"),config.plugins.MyMetrix.Store.SkinPart_Developer))
		list.append(getConfigListEntry(_("Background mode (for better OSD screenshots)"),config.plugins.MyMetrix.Color.BackgroundMode))
		
		self.setTitle(_("Settings"))
		ConfigListScreen.__init__(self, list)
		self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions"], {
			"down": self.keyDown,
			"up": self.keyUp,
			"red": self.exit,
			"cancel": self.save}, -1)
		self.UpdatePicture()
		self.onLayoutFinish.append(self.UpdateComponents)
		#if config.plugins.MetrixUpdater.UpdateAvailable.value = 1

	
		

	def UpdatePicture(self):
		self.PicLoad.PictureData.get().append(self.DecodePicture)
		self.onLayoutFinish.append(self.ShowPicture)
	
	def ShowPicture(self):
		self.PicLoad.setPara([self["avatar"].instance.size().width(),self["avatar"].instance.size().height(),self.Scale[0],self.Scale[1],0,1,"#30000000"])
		self.PicLoad.startDecode(self.picPath)
		#print "showing image"
		
	def DecodePicture(self, PicInfo = ""):
		#print "decoding picture"
		ptr = self.PicLoad.getData()
		self["avatar"].instance.setPixmap(ptr)	

	def UpdateComponents(self):
		self.updateAccountData()
		
	def updateAccountData(self):
		if not metrixCore.isLoggedIn():
			self.picPath = metrixDefaults.PLUGIN_DIR + "images/not-connected.png"
			self["username"].setText(_("Not connected!"))
		else:
			self.picPath = metrixDefaults.PLUGIN_DIR + "images/user.png"
			self["username"].setText(_(config.plugins.MetrixConnect.username.value))
		#self.UpdatePicture()
		self.ShowPicture()


	def keyDown(self):
		#print "key down"
		self["config"].instance.moveSelection(self["config"].instance.moveDown)
		#ConfigListScreen.keyDown(self)
		self.ShowPicture()
		
	def keyUp(self):
		#print "key up"
		self["config"].instance.moveSelection(self["config"].instance.moveUp)
		#ConfigListScreen.keyUp(self)
		self.ShowPicture()
	

	def showInfo(self):
		self.session.open(MessageBox, _("Information"), MessageBox.TYPE_INFO)

	def save(self):
		for x in self["config"].list:
			if len(x) > 1:
        			x[1].save()
			else:
       				pass
       		
		configfile.save()
	
		
		if not self.skinPartPath == config.plugins.MyMetrix.SkinPartPath.value:
			 #if os.path.exists(config.plugins.MyMetrix.SkinPartPath.value):
			 #rmtree(config.plugins.MyMetrix.SkinPartPath.value)
			 try:
			 	copytree(self.skinPartPath,config.plugins.MyMetrix.SkinPartPath.value)
			 	rmtree(self.skinPartPath)
			 except:
			 	pass
		self.close()

		if not os.path.exists(config.plugins.MyMetrix.SkinPartPath.value):
			os.makedirs(config.plugins.MyMetrix.SkinPartPath.value+"widgets/active/")	
			os.makedirs(config.plugins.MyMetrix.SkinPartPath.value+"widgets/inactive/")	
			os.makedirs(config.plugins.MyMetrix.SkinPartPath.value+"screens/active/")	
			os.makedirs(config.plugins.MyMetrix.SkinPartPath.value+"screens/inactive/")	

	def exit(self):
			
		for x in self["config"].list:
			if len(x) > 1:
					x[1].cancel()
			else:
       				pass
		self.close()
		
	def restartGUI(self, answer):
		if answer is True:
			config.plugins.MetrixUpdater.Reboot.value = 0
			config.plugins.MetrixUpdater.save()    
			configfile.save()
			configfile.save()
			self.session.open(TryQuitMainloop, 3)
		else:
			self.close()
