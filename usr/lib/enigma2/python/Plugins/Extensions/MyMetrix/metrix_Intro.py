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
from encode import multipart_encode
from streaminghttp import register_openers
import cookielib
from xml.dom.minidom import parseString
import gettext
import MultipartPostHandler
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
import urllib
from xml.dom.minidom import parseString
import gettext
from Components.GUIComponent import GUIComponent
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText,MultiContentEntryPixmapAlphaTest
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import metrixDefaults
import time
import shutil
import metrixTools
import metrix_SkinPartTools
import traceback
import metrixCore
import metrix_GenerateSkin
import metrix_MainMenu


#############################################################

config = metrixDefaults.loadDefaults()

def _(txt):
	t = gettext.dgettext("MyMetrix", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

#######################################################################		
		

class OpenScreen(Screen):
	skin = """
<screen name="MyMetrix-Intro" position="0,0" size="1278,720" flags="wfNoBorder" backgroundColor="#99ffffff">
  <eLabel position="40,40" size="1195,113" backgroundColor="#40000000" zPosition="-1" />
  <eLabel position="62,153" size="1151,521" backgroundColor="#40149baf" zPosition="-1" />
<widget name="left" position="84,317" size="262,59" foregroundColor="foreground" font="Regular; 23" valign="center" transparent="1" backgroundColor="#40149baf" halign="center" />
<ePixmap position="194,281" size="36,36" zPosition="10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/left.png" transparent="1" alphatest="blend" />
<ePixmap position="361,161" size="550,310" zPosition="1" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/metrixhddefault.png" />
<ePixmap position="1039,281" size="36,36" zPosition="10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/right.png" transparent="1" alphatest="blend" />
<widget name="right" position="929,318" size="262,59" foregroundColor="foreground" font="Regular; 23" valign="center" transparent="1" backgroundColor="#40149baf" halign="center" />
  <widget name="description" position="75,479" size="1127,189" transparent="1" halign="left" foregroundColor="foreground" backgroundColor="#40149baf" font="Regular; 30" valign="center" />
  <widget position="57,58" size="1162,85" foregroundColor="foreground" name="title" font="SetrixHD; 60" valign="center" transparent="1" backgroundColor="background" />
</screen>
"""

	def __init__(self, session):
		self["title"] = Label(_("Welcome to MyMetrix!"))
		self["description"] = Label(_("MyMetrix brings your set-top box experience onto a whole new level!\nPress left button to start the easy setup which generates the default MetrixHD feeling. Alternatively press right button to explore great SkinParts in OpenStore and customize your user interface how ever you want!"))
		Screen.__init__(self, session)
		self.session = session
		self["right"] = Label(_("Customize"))
		self["left"] = Label(_("Easy setup"))
		#self["helperimage"].instance.setPixmapFromFile("/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/nopreview.png")
		
		config.plugins.MyMetrix.showFirstRun.value = False
		config.plugins.MyMetrix.showFirstRun.save()
		try:
			configfile.save()
		except Exception, e:
			metrixTools.log("Error writing config file",e,"MetrixInto")

		self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions"], {
																											
																										"right": self.keyRight,
																										"left": self.keyLeft,
																											"cancel": self.exit}, -1)
		
		
	
	def keyLeft(self):
		self.session.open(metrix_GenerateSkin.OpenScreen)
		self.exit()
		
	def keyRight(self):
		self.session.open(metrix_MainMenu.OpenScreen)
		self.exit()
	
	
	
	def exit(self):
		self.close()
		
	def showInfo(self, text="Information"):
		self.session.open(MessageBox, _(text), MessageBox.TYPE_INFO)
			
		