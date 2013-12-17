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
import urllib,urllib2
from uuid import getnode as get_id
import gettext
from enigma import ePicLoad
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import metrix_MetrixColors
import metrixDefaults
import metrixTools
import metrixCore

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
<screen name="MyMetrix-Setup" position="264,207" size="689,270" flags="wfNoBorder" backgroundColor="#40000000">
  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="49,229" size="250,33" text="Cancel" transparent="1" />
 
  <eLabel position="20,15" size="348,50" text="MyMetrix" font="Regular; 40" valign="center" transparent="1" backgroundColor="#40000000" />
  <eLabel position="223,13" size="449,50" text="Disconnect" foregroundColor="#00ffffff" font="Regular; 30" valign="center" backgroundColor="#40000000" transparent="1" halign="right" />
  <eLabel position="35,230" size="5,40" backgroundColor="#00ff0000" />
  <eLabel position="389,230" size="5,40" backgroundColor="#000000ff" />
<eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="404,229" size="250,33" text="Disconnect" transparent="1" />
<eLabel position="17,101" size="657,82" text="Do you really want to disconnect?" foregroundColor="#00ffffff" font="Regular; 23" valign="center" backgroundColor="#40000000" transparent="1" halign="center" /></screen>"""

	def __init__(self, session, args = None, picPath = None):
		self.skin_lines = []
		Screen.__init__(self, session)
		self.session = session
		self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions"], {
																											"blue": self.disconnectDevice,
																											"ok": self.disconnectDevice,
																											"red": self.exit,
																											"cancel": self.exit}, -1)
		#self.onLayoutFinish.append(self.UpdateComponents)
		
	def disconnectDevice(self):
		try:
			url = metrixDefaults.URL_STORE_API + 'connect.deletedevice'
			data = metrixCore.getWeb(url,True)
			if not data:
				metrixTools.log("Error connecting to server!")
			
			dom = parseString(data)
			for design in dom.getElementsByTagName('entry'):
				status = str(design.getAttributeNode('status').nodeValue)
			if status == 'success':
				config.plugins.MetrixConnect.PIN.value = 0
				config.plugins.MetrixConnect.username.value = "Not connected"
				config.plugins.MetrixConnect.auth_token.value = "None"
				config.plugins.MetrixConnect.auth_id.value = ""
				config.plugins.MetrixConnect.save()
				configfile.save()
				self.close()
		except Exception, e:
			metrixTools.log("Error disconnecting device",e)
		
	
	def exit(self):
		self.close()
