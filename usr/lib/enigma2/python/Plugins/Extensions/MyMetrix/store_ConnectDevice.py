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

import traceback
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
<screen name="OpenStore-Setup" position="264,207" size="689,270" flags="wfNoBorder" backgroundColor="#40000000">
  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="49,229" size="250,33" text="Cancel" transparent="1" />
 <widget name="config" position="19,83" itemHeight="30" scrollbarMode="showOnDemand" size="653,36" transparent="1" foregroundColor="#00ffffff" backgroundColor="#40000000" />
  <eLabel position="20,15" size="348,50" text="OpenStore" font="Regular; 40" valign="center" transparent="1" backgroundColor="#40000000" />
  <eLabel position="223,13" size="449,50" text="Connect to open-store.net" foregroundColor="#00ffffff" font="Regular; 30" valign="center" backgroundColor="#40000000" transparent="1" halign="right" />
  <eLabel position="35,230" size="5,40" backgroundColor="#00ff0000" />
  <eLabel position="389,230" size="5,40" backgroundColor="#0000ff00" />
<eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="404,229" size="250,33" text="Connect" transparent="1" />
<widget position="17,136" size="657,82" name="help" foregroundColor="#00ffffff" font="Regular; 23" valign="center" backgroundColor="#40000000" transparent="1" halign="center" /></screen>
"""

	def __init__(self, session, args = None, picPath = None):
		self.skin_lines = []
		Screen.__init__(self, session)
		self.session = session
		self.picPath = picPath
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self["help"] = Label(_("Sign in to open-store.net open Device Portal and choose Add Device!"))
		list = []
		#config = metrixDefaults.loadDefaults()
		list.append(getConfigListEntry(_("Enter PIN"), config.plugins.MetrixConnect.PIN))
		
		ConfigListScreen.__init__(self, list)
		self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions"], {
																											"green": self.connectDevice,
																											"ok": self.connectDevice,
																											"cancel": self.exit,
																											"red": self.exit}, -1)
		#self.onLayoutFinish.append(self.UpdateComponents)
		
	def connectDevice(self):
		#config = metrixDefaults.loadDefaults()
		config.plugins.MetrixConnect.PIN.save()
		config.plugins.MetrixConnect.save()
		configfile.save()
		pin = config.plugins.MetrixConnect.PIN.value
		self["help"].setText(_("Please wait..."))
		try:
			
			data = metrixCore.connectDevice(pin)
			dom = parseString(data)
			for design in dom.getElementsByTagName('entry'):
				status = str(design.getAttributeNode('status').nodeValue)
				try:
					username = str(design.getAttributeNode('username').nodeValue)
					auth_token = str(design.getAttributeNode('auth_token').nodeValue)
					auth_id = str(design.getAttributeNode('auth_id').nodeValue)
					
				except:
					pass
			if status == 'success':
				if username == '':
					self["help"].setText(_("Accept device and press connect again."))
				else:
					#config.plugins.MetrixConnect.PIN.value = 0
					config.plugins.MetrixConnect.username.value = username
					config.plugins.MetrixConnect.auth_token.value = auth_id
					config.plugins.MetrixConnect.auth_id.value = auth_token
					config.plugins.MetrixConnect.save()
					configfile.save()
					self.close()
			elif status == 'error':
				self["help"].setText(_("Error. Verify your PIN!"))
		except Exception, e:
			metrixTools.log("Error connecting device!",e)
			#except:
			self["help"].setText(_("Error connecting to OpenStore!"))
		
	def showInfo(self):
		self.session.open(MessageBox, _("Information"), MessageBox.TYPE_INFO)


	
	def exit(self):
		self.close()
