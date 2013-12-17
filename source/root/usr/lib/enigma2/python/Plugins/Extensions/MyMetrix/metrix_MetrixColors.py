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
from Components.config import config, configfile, ConfigYesNo, ConfigSequence, ConfigSubsection, ConfigSelectionNumber, getConfigListEntry, ConfigSelection, ConfigNumber, ConfigText, ConfigInteger
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Language import language
from os import environ, listdir, remove, rename, system
from skin import parseColor
from Components.Pixmap import Pixmap
from Components.Label import Label
import os
import gettext
from enigma import ePicLoad
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import metrixDefaults
import metrixPreview
import metrixPreview2
import metrixPreviewSIB
import metrixSubmitDesign
from metrixTools import getHex, getHexColor
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
	skin = """
<screen name="MyMetrix-MetrixColors" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="#b0ffffff">
    <eLabel position="40,40" size="620,640" backgroundColor="#40000000" zPosition="-1" />
  <eLabel position="660,71" size="575,575" backgroundColor="#40111111" zPosition="-1" />

  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="67,639" size="250,33" text="%s" transparent="1" />
 <widget name="config" itemHeight="30" position="53,125" scrollbarMode="showOnDemand" size="590,506" transparent="1" foregroundColor="#00ffffff" backgroundColor="#40000000" />
  <eLabel position="53,52" size="348,50" text="MyMetrix" font="Regular; 40" valign="center" transparent="1" backgroundColor="#40000000" />
  <eLabel position="284,49" size="349,50" text="MetrixColors" foregroundColor="#00ffffff" font="Regular; 30" valign="center" backgroundColor="#40000000" transparent="1" halign="left" />
  <eLabel position="55,639" size="5,40" backgroundColor="#00ff0000" />
    <eLabel position="940,606" size="5,40" backgroundColor="#000000ff" />
  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="952,605" size="270,33" text="%s" transparent="1" />

 <eLabel position="376,639" size="5,40" backgroundColor="#0000ff00" />
  <widget name="buttonGreen" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="388,639" size="250,33" transparent="1" />


 <eLabel position="670,606" size="5,40" backgroundColor="#00ffff00" />
  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="682,605" size="250,33" text="%s" transparent="1" />

   <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/metrixcolors.png" position="671,95" size="550,500" zPosition="1" />
  </screen>
"""  %(_("Discard"), _("Preview SecondInfoBar"), _("Preview InfoBar")) 

	def __init__(self, session, args = None, index = 0):
		self.index = index
		Screen.__init__(self, session)
		self.session = session
		self["buttonGreen"] = Label()
		if metrixCore.isLoggedIn():
			self["buttonGreen"].setText(_("Publish to OpenStore"))
		
		list = []
		list.append(getConfigListEntry(_("Background transparency"), config.plugins.MyMetrix.Color.BackgroundTransparency))
		list.append(getConfigListEntry(_("Selection transparency"), config.plugins.MyMetrix.Color.SelectionTransparency))
		list.append(getConfigListEntry(_("Background text transparency"), config.plugins.MyMetrix.Color.BackgroundTextTransparency))
		
		list.append(getConfigListEntry(_("Selection"), config.plugins.MyMetrix.Color.Selection))
		list.append(getConfigListEntry(_("Progress bars"), config.plugins.MyMetrix.Color.ProgressBar))
		list.append(getConfigListEntry(_("Background"), config.plugins.MyMetrix.Color.Background))
		list.append(getConfigListEntry(_("Background 2"), config.plugins.MyMetrix.Color.Background2))
		list.append(getConfigListEntry(_("Foreground"), config.plugins.MyMetrix.Color.Foreground))
		list.append(getConfigListEntry(_("Background text"), config.plugins.MyMetrix.Color.BackgroundText))
		list.append(getConfigListEntry(_("Accent 1"), config.plugins.MyMetrix.Color.Accent1))
		list.append(getConfigListEntry(_("Accent 2"), config.plugins.MyMetrix.Color.Accent2))
		
		list.append(getConfigListEntry(_("Custom colors (r,g,b):"), ))
		list.append(getConfigListEntry(_("    Selection"), config.plugins.MyMetrix.Color.Selection_Custom))
		list.append(getConfigListEntry(_("    Background"), config.plugins.MyMetrix.Color.Background_Custom))
		list.append(getConfigListEntry(_("    Background 2"), config.plugins.MyMetrix.Color.Background2_Custom))
		list.append(getConfigListEntry(_("    Foreground"), config.plugins.MyMetrix.Color.Foreground_Custom))
		list.append(getConfigListEntry(_("    Background text"), config.plugins.MyMetrix.Color.BackgroundText_Custom))
		list.append(getConfigListEntry(_("    Accent 1"), config.plugins.MyMetrix.Color.Accent1_Custom))
		list.append(getConfigListEntry(_("    Accent 2"), config.plugins.MyMetrix.Color.Accent2_Custom))
		

		ConfigListScreen.__init__(self, list)
		
		self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions"], {
																											"left": self.keyLeft,
																											"down": self.keyDown,
																											"up": self.keyUp,
																											"right": self.keyRight,
																											"red": self.exit,
																											"green": self.openSubmitDesignWindow,
																											"yellow":  self.previewInfobar,
																											"blue":  self.previewSecondInfobar,
																											 "cancel": self.save}, -1)
		#self.onLayoutFinish.append(self.layoutFinish)
		#self.onLayoutFinish.append(self.UpdateComponents)
		#if config.plugins.MetrixUpdater.UpdateAvailable.value = 1
		
	def previewInfobar(self):
		config.plugins.MyMetrix.Color.save()
		self.session.open(metrixPreview.MetrixPreviewWindow)
		
	def previewSecondInfobar(self):
		config.plugins.MyMetrix.Color.save()
		self.session.open(metrixPreviewSIB.MetrixPreviewSIBWindow)
	
	def openSubmitDesignWindow(self):
		if metrixCore.isLoggedIn():
			self.session.open(metrixSubmitDesign.MyMetrixSubmitDesignWindow)
		
		
	def keyLeft(self):	
		ConfigListScreen.keyLeft(self)
		

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		
	
	def keyDown(self):
		#print "key down"
		self["config"].instance.moveSelection(self["config"].instance.moveDown)
		#ConfigListScreen.keyDown(self)
		
	def keyUp(self):
		#print "key up"
		self["config"].instance.moveSelection(self["config"].instance.moveUp)
		#ConfigListScreen.keyUp(self)
	
	def reboot(self):
		restartbox = self.session.openWithCallback(self.restartGUI,MessageBox,_("Do you really want to reboot now?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Restart GUI"))
		
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

	def restartGUI(self, answer):
		if answer is True:
			config.plugins.MetrixUpdater.Reboot.value = 0
			config.plugins.MetrixUpdater.save()    
			configfile.save()
			self.session.open(TryQuitMainloop, 3)
		else:
			self.close()
		
	def exit(self):
		for x in self["config"].list:
			if len(x) > 1:
					x[1].cancel()
			else:
       				pass
		self.close()
