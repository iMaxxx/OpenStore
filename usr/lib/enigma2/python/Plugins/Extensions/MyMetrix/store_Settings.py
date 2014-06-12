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
	skin = """<screen name="OpenStore-Setup" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="#b0ffffff">
    <eLabel position="40,40" size="620,640" backgroundColor="#40000000" zPosition="-1" />
  <eLabel position="660,71" size="575,575" backgroundColor="#40111111" zPosition="-1" />
<widget name="metrixVersion" position="325,639" size="319,36" font="Regular; 20" backgroundColor="#40000000" transparent="1" halign="right" />
<eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="75,641" size="250,33" text="%s" transparent="1" />
 <widget name="config" position="54,110" itemHeight="30" scrollbarMode="showOnDemand" size="590,510" transparent="1" foregroundColor="#00ffffff" backgroundColor="#40000000" />
  <eLabel position="55,51" size="348,50" text="OpenStore" font="Regular; 40" valign="center" transparent="1" backgroundColor="#40000000" />
  <eLabel position="280,53" size="249,50" text="%s" foregroundColor="#00ffffff" font="Regular; 30" valign="center" backgroundColor="#40000000" transparent="1" halign="left" />
  <eLabel position="62,639" size="5,40" backgroundColor="#00ff0000" />
  <ePixmap position="671,144" size="550,310" zPosition="3" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/sponsor.png" />
<eLabel position="671,86" size="541,50" text="Sponsor" foregroundColor="#00ffffff" font="Regular; 30" valign="center" backgroundColor="#40000000" transparent="1" halign="left" />
<widget name="avatar" position="1109,521" size="96,96" />

<eLabel position="669,471" size="541,50" text="www.open-store.net" foregroundColor="#00ffffff" font="Regular; 24" valign="center" backgroundColor="#40000000" transparent="1" halign="left" />
<widget name="username" position="692,543" size="400,50" font="Regular; 30" transparent="1" halign="right" backgroundColor="#40000000" foregroundColor="#00ffffff" />
<eLabel position="711,606" size="5,40" backgroundColor="#000000ff" />
<widget name="connectbutton" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="721,605" size="250,33" transparent="1" /></screen>
""" %(_("Discard"), _("Settings"))

	def __init__(self, session, args = None):
		self.skin_lines = []
		Screen.__init__(self, session)
		self.session = session
		self.version = "v"+metrixDefaults.VERSION
		self.picPath = metrixDefaults.PLUGIN_DIR + "images/not-connected.png"
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self["avatar"] = Pixmap()
		self.setTitle(_("Settings"))
		self["connectbutton"] =  Label()
		self["username"] = Label()
		self["metrixVersion"] = Label(_(self.version + " - open-store.net"))
		self["metrixUpdate"] = Label(_(" "))
		if config.plugins.MetrixUpdater.Reboot.value == 1:
			self["metrixVersion"] = Label(self.version + _(" - (Reboot required)"))
		self["metrixUpdate"] = Label(_(" "))
		list = []
		#list.append(getConfigListEntry(_("Automatic Updates ------------------------------------------------------------------------")))
		#list.append(getConfigListEntry(_("Show notification bar"), config.plugins.MetrixUpdater.UpdatePopup_Packages))
		#list.append(getConfigListEntry(_(" ")))
		list.append(getConfigListEntry(_("Sync --------------------------------------------------------------------------------------------")))
		list.append(getConfigListEntry(_("General box information"), config.plugins.MetrixCloudSync.SyncBoxInfo))
		list.append(getConfigListEntry(_("Program information"), config.plugins.MetrixCloudSync.SyncProgramInfo))
		list.append(getConfigListEntry(_("Hardware information"), config.plugins.MetrixCloudSync.SyncProgramInfo))
		list.append(getConfigListEntry(_("Network information"), config.plugins.MetrixCloudSync.SyncProgramInfo))
		list.append(getConfigListEntry(_("Plugins"), config.plugins.MetrixCloudSync.SyncPackages))
		list.append(getConfigListEntry(_("SkinParts"), config.plugins.MetrixCloudSync.SyncSkinParts))
		#list.append(getConfigListEntry(_("EPG"), config.plugins.MetrixCloudSync.SyncEPG))
		#list.append(getConfigListEntry(_("Logs"), config.plugins.MetrixCloudSync.SyncLogs))
		list.append(getConfigListEntry(" "))
		list.append(getConfigListEntry(_("ActiveXPicon ("+config.plugins.MyMetrix.XPiconsRepositoryName.value+")----------------------------------------------------------------------------------------")))
		list.append(getConfigListEntry(_("Download missing Picons"), config.plugins.MyMetrix.ActiveXPicon))
		list.append(getConfigListEntry(_("Overwrite existing Picons"), config.plugins.MyMetrix.XPiconsOverwrite))
		list.append(getConfigListEntry(_("Picons location"), config.plugins.MyMetrix.XPiconsPath))
		list.append(getConfigListEntry(_("Picon sizes:"),config.plugins.MyMetrix.PiconSizes))
		list.append(getConfigListEntry(_("Picon color depth:"),config.plugins.MyMetrix.PiconDepth))
		
		list.append(getConfigListEntry(" "))
		list.append(getConfigListEntry(_("Automatic Updates ------------------------------------------------------------------------")))
		list.append(getConfigListEntry(_("OpenStore and MyMetrix"), config.plugins.MyMetrix.AutoUpdate))
		list.append(getConfigListEntry(_("Downloaded Plugins"), config.plugins.MyMetrix.AutoUpdatePlugins))
		list.append(getConfigListEntry(_("Downloaded SkinParts"), config.plugins.MyMetrix.AutoUpdateSkinParts))
		list.append(getConfigListEntry(_("Show update notification bar"), config.plugins.MetrixUpdater.UpdatePopup_Packages))
		
		
		list.append(getConfigListEntry(" "))
		list.append(getConfigListEntry(_("Enhanced Options ------------------------------------------------------------------------")))
		
		#list.append(getConfigListEntry(_("Open NaviBar on blue key"),config.plugins.navibar.blue)) ##for later integration of navibar
		list.append(getConfigListEntry(_("Show in main menu"),config.plugins.MyMetrix.showInMainMenu))
		
		list.append(getConfigListEntry(_("Plugin Developer"),config.plugins.MyMetrix.Store.Plugin_Developer))
		list.append(getConfigListEntry(_("Log level"),config.plugins.MyMetrix.logLevel))
		list.append(getConfigListEntry(_("Ignore image restrictions"),config.plugins.MyMetrix.Store.IgnoreRestrictions))
		
		self.UpdatePicture()
		self.onLayoutFinish.append(self.UpdateComponents)
		
		
		ConfigListScreen.__init__(self, list)
		self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions"], {
			"down": self.keyDown,
			"up": self.keyUp,
			"blue": self.connect,
			"red": self.exit,
			"cancel": self.save}, -1)
		self.UpdatePicture()
		self.setTitle("OpenStore // Settings")
		self.onLayoutFinish.append(self.UpdateComponents)
		#if config.plugins.MetrixUpdater.UpdateAvailable.value = 1

	def connect(self):
		if not metrixCore.isLoggedIn():
			self.session.open(store_ConnectDevice.OpenScreen)
		else:
			self.session.open(store_DisconnectDevice.OpenScreen)
		self.updateAccountData()

	
		
	def updateAccountData(self):
		self["connectbutton"].setText(_("Connect to OpenStore"))
		if not metrixCore.isLoggedIn():
			self["connectbutton"].setText(_("Connect to OpenStore"))
			self.picPath = metrixDefaults.PLUGIN_DIR + "images/not-connected.png"
			self["username"].setText(_("Not connected!"))
		else:
			self["connectbutton"].setText(_("Disconnect"))
			self.picPath = metrixDefaults.PLUGIN_DIR + "images/user.png"
			self["username"].setText(_(config.plugins.MetrixConnect.username.value))
		self.ShowPicture()

	


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


	def keyDown(self):
		self["config"].instance.moveSelection(self["config"].instance.moveDown)

		
	def keyUp(self):
		self["config"].instance.moveSelection(self["config"].instance.moveUp)

	

	def showInfo(self):
		self.session.open(MessageBox, _("Information"), MessageBox.TYPE_INFO)

	def save(self):
		for x in self["config"].list:
			if len(x) > 1:
        			x[1].save()
			else:
       				pass	
		configfile.save()
		self.close()


	def exit(self):
		self.close()
