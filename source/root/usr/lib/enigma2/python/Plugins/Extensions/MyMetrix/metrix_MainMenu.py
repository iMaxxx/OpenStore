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
from uuid import getnode as get_id
from Screens.Console import Console
import cookielib
from xml.dom.minidom import parseString
import gettext
import MultipartPostHandler
from enigma import eListboxPythonMultiContent, gFont, eTimer, eDVBDB, getDesktop
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.MenuList import MenuList
from Components.config import config, configfile, ConfigYesNo, ConfigSequence, ConfigSubsection, ConfigSelectionNumber, getConfigListEntry, ConfigSelection, ConfigNumber, ConfigText, ConfigInteger
from Components.Label import Label
from Components.Language import language
from os import environ, listdir, remove, rename, system
from skin import parseColor
from Components.Pixmap import Pixmap
from Components.Label import Label
import gettext
from enigma import ePicLoad
from Components.GUIComponent import GUIComponent
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText,MultiContentEntryPixmapAlphaTest
from enigma import eListbox, RT_HALIGN_LEFT, RT_HALIGN_RIGHT
from enigma import ePicLoad,eListboxPythonMultiContent,gFont,addFont, loadPic, loadPNG
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import metrixConnector
import metrix_MetrixColors
import metrixDefaults
import metrixInfobar
import store_SkinParts_Categories
import metrix_MySkinParts
import metrix_GenerateSkin
import metrixSecondInfobar
#import metrixWeather
import metrix_Settings
from metrixTools import getHex, getHexColor
#import libxml2
from xml.dom.minidom import parseString, parse
import os
import socket
import e2info
import threading
import time
import store_Settings
import metrix_Settings
import store_SkinParts_Categories

#from xml.etree.ElementTree import parse
#############################################################



#############################################################

config = metrixDefaults.loadDefaults()

lang = language.getLanguage()
def _(txt):
	t = gettext.dgettext("MyMetrix", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t


#######################################################################		
		

class OpenScreen(Screen):
	skin = """
<screen name="MyMetrix-Menu" position="0,0" size="1200,640" flags="wfNoBorder" backgroundColor="transparent">
    <eLabel position="264,51" zPosition="-1" size="340,320" backgroundColor="#40000000" transparent="0" />
    <!-- /*ClockWidget-->
    <widget source="global.CurrentTime" foregroundColor="#00ffffff" render="Label" position="450,401" size="169,80" font="SetrixHD; 60" halign="left" backgroundColor="#40000000" transparent="1" valign="top">
      <convert type="ClockToText">Default</convert>
    </widget>
    <widget source="global.CurrentTime" render="Label" position="290,444" size="148,29" font="SetrixHD; 20" halign="right" backgroundColor="#40000000" foregroundColor="#00bbbbbb" transparent="1">
      <convert type="ClockToText">Format:%e. %B</convert>
    </widget>
    <widget source="global.CurrentTime" render="Label" position="313,415" size="125,30" font="SetrixHD; 20" halign="right" backgroundColor="#40000000" foregroundColor="#00bbbbbb" transparent="1">
      <convert type="ClockToText">Format:%A</convert>
    </widget>
    <eLabel position="265,410" zPosition="-1" size="340,70" backgroundColor="#40000000" transparent="0" />
    <!--ClockWidget */-->
    
<widget name="menu" position="636,60" size="430,555" scrollbarMode="showNever" itemHeight="60" enableWrapAround="1" transparent="1" foregroundColor="#00ffffff" backgroundColor="#40000000">
    </widget>
    <eLabel name="" position="645,51" zPosition="-19" size="412,565" backgroundColor="#40000000" foregroundColor="#40000000" />
    <ePixmap position="310,85" size="256,256" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/mymetrix.png" alphatest="blend" />
</screen>
"""

	def __init__(self, session, args = None):
		#recolorImage()
		Screen.__init__(self, session)
		self.session = session
		self.list = []
		
		self.list.append(self.MetrixListEntry(_("OpenStore"), "OpenStore"))
		self.list.append(self.MetrixListEntry(_("SkinPart Settings"), "SkinParts"))
		self.list.append(self.MetrixListEntry(_("MetrixColors Settings"), "metrixColors"))
		self.list.append(self.MetrixListEntry(_("General Settings"),"general"))
		self.list.append(self.MetrixListEntry(_("OpenStore Settings"),"openstoresettings"))
		self.list.append(self.MetrixListEntry(_("Save My Skin"), "generate"))
			
		self["menu"] =  MetrixList([])
		self["menu"].setList(self.list)
		self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions"], {
				"ok": self.go,
				"red": self.exit,
				"yellow": self.reboot, 
				"green": self.save,
				"cancel": self.exit
			}, -1)
		self.setTitle("MyMetrix")
		
	 
	def MetrixListEntry(self,_name,_value):
		entry = [[_value,_name]]
		#png = "/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/vote"+rating+".png"
		#res.append(MultiContentEntryPixmapAlphaTest(pos=(412, 9), size=(170, 32), png=loadPNG(png)))
		entry.append(MultiContentEntryText(pos=(30, 5), size=(405, 50), font=0, text=_name))
		return entry
																											
	def go(self):
		returnValue = str(self["menu"].l.getCurrentSelection()[0][0])
		if returnValue is not None:
			
			if returnValue is "metrixColors":
				self.session.open(metrix_MetrixColors.OpenScreen)
			elif returnValue is "OpenStore":
				self.session.open(store_SkinParts_Categories.OpenScreen)
			elif returnValue is "SkinParts":
				self.session.open(metrix_MySkinParts.OpenScreen)
			elif returnValue is "general":
				self.session.open(metrix_Settings.OpenScreen)
			elif returnValue is "openstoresettings":
				self.session.open(store_Settings.OpenScreen)
			elif returnValue is "generate":
				self.session.open(metrix_GenerateSkin.OpenScreen)
		else:
			pass
	
	def reboot(self):
		restartbox = self.session.openWithCallback(self.restartGUI,MessageBox,_("Do you really want to reboot now?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Restart GUI"))
		
	def showInfo(self):
		self.session.open(MessageBox, _("Information"), MessageBox.TYPE_INFO,3)

		
	
	def exit(self):
		self.close()
		
	def save(self):
		
		self.close()
		
		
class MetrixList(MenuList):
	def __init__(self, list):
		MenuList.__init__(self, list, False, eListboxPythonMultiContent)
		self.l.setItemHeight(60)
		self.l.setFont(0, gFont("SetrixHD", 30))
		self.l.setFont(1, gFont("Regular", 22))
	
	