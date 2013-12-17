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
import urllib2
import urllib
from xml.dom.minidom import parseString
import gettext
from Components.GUIComponent import GUIComponent
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText,MultiContentEntryPixmapAlphaTest
from enigma import eListbox, RT_HALIGN_LEFT, RT_HALIGN_RIGHT
from enigma import ePicLoad,eListboxPythonMultiContent,gFont,addFont, loadPic, loadPNG
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
<screen name="OpenStore-Vote" position="264,207" size="689,270" flags="wfNoBorder" backgroundColor="#40000000">
  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="49,229" size="250,33" text="Cancel" transparent="1" />
  <eLabel position="20,15" size="348,50" text="OpenStore" font="Regular; 40" valign="center" transparent="1" backgroundColor="#40000000" />
  <eLabel position="223,13" size="449,50" text="Vote" foregroundColor="#00ffffff" font="Regular; 30" valign="center" backgroundColor="#40000000" transparent="1" halign="right" />
  <eLabel position="35,230" size="5,40" backgroundColor="#00ff0000" />
  <eLabel position="389,230" size="5,40" backgroundColor="#0000ff00" />
  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="404,229" size="250,33" text="Submit" transparent="1" />
  <widget position="263,120" size="170,32" name="ratingbar" alphatest="blend" zPosition="0" />
  <ePixmap position="185,106" size="64,64" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/left.png" alphatest="blend" />
  <ePixmap position="448,106" size="64,64" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/right.png" alphatest="blend" />
</screen>
"""

	def __init__(self, session, vote_id="1", group='none'):
		self.ratingurl = metrixDefaults.URL_STORE_API + "set.rating"
		Screen.__init__(self, session)
		self.vote_id = str(vote_id)
		self.group = group
		self.session = session
		self.picPath = ""
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self.rating = 5
		self["ratingbar"] = Pixmap()
		
		self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions"], {
																											"left": self.keyLeft,
																											"right": self.keyRight,
																											"ok": self.submit,
																											"green": self.submit,
																											"red": self.close,
																											"cancel": self.close}, -1)
		self.onLayoutFinish.append(self.UpdateComponents)
		
	
	def GetPicturePath(self):
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/vote"+str(self.rating)+".png"
		return path
		

	
	def UpdatePicture(self):
		self.PicLoad.PictureData.get().append(self.DecodePicture)
		self.onLayoutFinish.append(self.ShowPicture)
	
	def ShowPicture(self):
		self.PicLoad.setPara([self["ratingbar"].instance.size().width(),self["ratingbar"].instance.size().height(),self.Scale[0],self.Scale[1],0,1,"#002C2C39"])
		self.PicLoad.startDecode(self.GetPicturePath())
		#print "showing image"
		
	def DecodePicture(self, PicInfo = ""):
		#print "decoding picture"
		ptr = self.PicLoad.getData()
		self["ratingbar"].instance.setPixmap(ptr)	

	def UpdateComponents(self):
		self.UpdatePicture()

	def keyLeft(self):
		if self.rating > 1:
			self.rating = self.rating - 1
		self.ShowPicture()

		
	def keyRight(self):
		if self.rating < 5:
			self.rating = self.rating + 1
		self.ShowPicture()
	


	
	def exit(self):
		self.close()
		
		
	
	def submit(self):
		#&group=DesignStore_dark-red_Test&vote_id=1&device_id=99099&value=2
		try:
			params = {'group':self.group,'vote_id':self.vote_id,'value':self.rating}
			data = metrixCore.getWeb(self.ratingurl,True,params)
			if not data:
				metrixTools.log("Error contacting server")
			
			dom = parseString(data)
			for design in dom.getElementsByTagName('entry'):
				status = str(design.getAttributeNode('status').nodeValue)
				code = str(design.getAttributeNode('code').nodeValue)
			if status == 'error':
				if code == '103':
					self.showInfo("Already voted!")
			else:
				self.showInfo("Thank you!")
			self.close()
		except:
			metrixTools.log("Error submitting rating")
			self.close()
	
	def showInfo(self, text="Information"):
			self.session.open(MessageBox, _(text), MessageBox.TYPE_INFO)
		
