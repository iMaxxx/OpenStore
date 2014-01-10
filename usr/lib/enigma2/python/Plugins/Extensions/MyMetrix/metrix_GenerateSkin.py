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

from xml.dom.minidom import parse
import cookielib
from xml.dom.minidom import parseString
import gettext
from uuid import getnode as get_id
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
from enigma import eListbox, RT_HALIGN_LEFT, RT_HALIGN_RIGHT
from enigma import ePicLoad,eListboxPythonMultiContent,gFont,addFont, loadPic, loadPNG
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import metrixDefaults
import time
from metrixTools import getHex, getHexColor,skinPartIsCompatible
import metrixTools
import traceback
import metrix_SkinPartTools

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
<screen name="MyMetrix-GenerateSkin" position="-1,657" size="1285,64" flags="wfNoBorder" backgroundColor="#40000000">
  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="1115,16" size="163,33" text="Cancel" transparent="1" />
 
  <eLabel position="20,7" size="190,50" text="MyMetrix" font="Regular; 40" valign="center" transparent="1" backgroundColor="#40000000" noWrap="1" />
  <eLabel position="215,7" size="261,50" text="%s" foregroundColor="#00ffffff" font="Regular; 25" valign="center" backgroundColor="#40000000" transparent="1" halign="left" noWrap="1" />
  <eLabel position="1103,13" size="5,50" backgroundColor="#00ff0000" />
   
<widget name="output" position="488,10" size="601,43" foregroundColor="#00ffffff" font="Regular; 22" valign="center" backgroundColor="#40000000" transparent="1" halign="left" noWrap="1" /> 
  </screen>
""" %(_("Generating Skin"))

	def __init__(self, session, args = None, picPath = None):
		Screen.__init__(self, session)
		self.session = session
		self["output"] = Label(_("Generating..."))
		self.generate = True
		self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions"], {"cancel": self.exit,"red": self.exit}, -1)
		self.onLayoutFinish.append(self.startThread)
		
	def startThread(self):	
		global thread_getDesigns
		thread_getDesigns = threading.Thread(target=self.threadworker,  args=())
		thread_getDesigns.daemon = True
		thread_getDesigns.start()
		
	#THREAD WORKER
	def threadworker(self):
		while(1):
			if self.generate == True:
				self.generate = False
				self.generateSkin()
				break
			time.sleep(1)
				
	
	def getSkinPartsScreennames(self,path):
		screennames = []
		dirs = listdir( path )
		for dir in dirs:
			try:
				dom = parse(path+"/"+dir+"/data.xml")
				screen = dom.getElementsByTagName('screen')[0]
				name = str(screen.getAttributeNode('name').nodeValue)
				screennames.append(name)
			except:
				pass
		return screennames
	
	
	
	
	def generateSkin(self):
		screennames = [] 
		screennames = self.getSkinPartsScreennames(config.plugins.MyMetrix.SkinPartPath.value + "screens/active/")
		metrixTools.callOnMainThread(self["output"].setText,_("Reading template file"))
		skindom = parse(config.plugins.MyMetrix.Templates.value)
		skinNode = skindom.getElementsByTagName('skin')[0]
		
		metrixTools.callOnMainThread(self["output"].setText,_("Setting colors"))
		self.setColor(skinNode)
		for screen in skindom.getElementsByTagName('screen'):
			screenname = str(screen.getAttributeNode('name').nodeValue)
			
			metrixTools.callOnMainThread(self["output"].setText,(str(_("Checking screen ")+screenname)))
			if screenname in screennames:
				metrixTools.callOnMainThread(self["output"].setText,_(str("Removing default screen "+screenname)))
				parentNode = screen.parentNode
				parentNode.removeChild(screen)
			if config.plugins.MyMetrix.CleanInfoBar.value:
				if screenname == "InfoBar" or screenname == "SecondInfoBar":
					for child in screen.childNodes:
						screen.removeChild(child)
				
		# APPEND STORE SCREENS
		path = config.plugins.MyMetrix.SkinPartPath.value + "screens/active/"
		dirs = listdir(path)
		for dir in dirs:
			metrixTools.callOnMainThread(self["output"].setText,_("Parsing SkinPart Screens"))
			try:	
				screen = metrix_SkinPartTools.parseSkinPart(path+dir,"data.xml","config.cfg",screenname)
				customscreen = skindom.importNode(screen, True)
				skinNode.appendChild(customscreen)
			except Exception, e:
				metrixTools.log("Error appending screen",e)
			
		# APPEND STORE WIDGETS
		path = config.plugins.MyMetrix.SkinPartPath.value + "widgets/active/"
		dirs = listdir(path)
		for dir in dirs:
			try:
				widget = metrix_SkinPartTools.parseSkinPart(path+dir,"data.xml","config.cfg",screenname,False)
				
				for widgetscreenname in str(widget.getAttributeNode('screenname').nodeValue).split(","):
					metrixTools.callOnMainThread(self["output"].setText,str(_("Parsing SkinPart widget for ")+widgetscreenname))
					for screen in skinNode.getElementsByTagName('screen'):
						screenname = str(screen.getAttributeNode('name').nodeValue)
						
						if screenname == widgetscreenname and metrix_SkinPartTools.widgetActive(path+dir,"data.xml","config.cfg",screenname):
							for child in widget.childNodes:
								#raw_xml = raw_xml.replace("%SCREENNAME%",screenname)
								childimport = skindom.importNode(child, True)
								screen.appendChild(childimport)
							break
					
			except Exception, e:
				metrixTools.log("Error appending widget",e)	
		
		for screen in skindom.getElementsByTagName('screen'):
			screenname = str(screen.getAttributeNode('name').nodeValue)
			metrixTools.callOnMainThread(self["output"].setText,_(str("Setting ProgressBars for "+screenname+" screen")))
			try:
				for widget in screen.getElementsByTagName('widget'):
					try:
						pixmap = widget.getAttributeNode('pixmap').nodeValue
						if pixmap == "MetrixHD/colors/00ffffff.png":
							widget.setAttribute("pixmap",pixmap.replace("/00ffffff", "/" + config.plugins.MyMetrix.Color.ProgressBar.value.replace("#","")))
						elif pixmap == "%METRIX:PROGRESSBAR:COLOR:MULTI%":
							widget.setAttribute("pixmap","MetrixHD/colors/" + config.plugins.MyMetrix.Color.ProgressBar.value.replace("#","")+".png")
						elif pixmap == "%METRIX:PROGRESSBAR:COLOR:WHITE%":
							widget.setAttribute("pixmap","MetrixHD/colors/00ffffff.png")
					except:
						pass
			except: 
				pass
			
		for screen in skinNode.getElementsByTagName('screen'):
			screenname = str(screen.getAttributeNode('name').nodeValue)
			metrixTools.callOnMainThread(self["output"].setText,_(str("Checking compatibility for "+screenname)))
			screen = skinPartIsCompatible(screen)
		
		metrixTools.callOnMainThread(self.writeFile,skindom)
		
		

	def writeFile(self,skindom):
		try:
			self["output"].setText(_("Writing skin file, please wait..."))
			oldfilename = config.plugins.MyMetrix.Templates.value.split("/")[-1]
			file =  config.plugins.MyMetrix.Templates.value.replace(oldfilename,"skin."+config.plugins.MyMetrix.SkinName.value + ".xml")
			path = os.path.dirname(file)	
			if not os.path.exists(path):
				os.makedirs(path)	
			metrix_SkinPartTools.writeSkinFile(skindom,file)
		
			self["output"].setText(_("Activating Skin"))
			config.skin.primary_skin.value = file.replace(metrixDefaults.SKINS_ROOT,"")
			config.skin.primary_skin.save()
			configfile.save()
		except Exception, e:
			
			metrixTools.log("Error activating skin",e)
		self.finished()
		
	
	def finished(self):
		restartbox = self.session.openWithCallback(self.restartGUI,MessageBox,_("GUI needs a restart to apply a new skin.\nDo you want to Restart the GUI now?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Restart GUI"))
		
		
	def setColor(self,skinNode):
		###########READING DATA FILES
		try:
			if config.plugins.MyMetrix.Color.Selection.value == "CUSTOM":
				_selection = getHexColor(config.plugins.MyMetrix.Color.Selection_Custom.value,config.plugins.MyMetrix.Color.SelectionTransparency.value)
			else:
				_selection = config.plugins.MyMetrix.Color.Selection.value.replace("#00","#"+str(hex(int(config.plugins.MyMetrix.Color.SelectionTransparency.value))))
			
			if config.plugins.MyMetrix.Color.Background2.value == "CUSTOM":
				_background2 = getHexColor(config.plugins.MyMetrix.Color.Background2_Custom.value,config.plugins.MyMetrix.Color.BackgroundTransparency.value)
			else:
				_background2 = config.plugins.MyMetrix.Color.Background2.value.replace("#00","#"+getHex(config.plugins.MyMetrix.Color.BackgroundTransparency.value))
			
			if config.plugins.MyMetrix.Color.Background.value == "CUSTOM":
				_background = getHexColor(config.plugins.MyMetrix.Color.Background_Custom.value,config.plugins.MyMetrix.Color.BackgroundTransparency.value)
			else:
				_background = config.plugins.MyMetrix.Color.Background.value.replace("#00","#"+getHex(config.plugins.MyMetrix.Color.BackgroundTransparency.value))
			
			if config.plugins.MyMetrix.Color.BackgroundText.value == "CUSTOM":
				_BackgroundText = getHexColor(config.plugins.MyMetrix.Color.BackgroundText_Custom.value, config.plugins.MyMetrix.Color.BackgroundTextTransparency.value)
			else:
				_BackgroundText = config.plugins.MyMetrix.Color.BackgroundText.value.replace("#00","#"+getHex(config.plugins.MyMetrix.Color.BackgroundTextTransparency.value))
			
			if config.plugins.MyMetrix.Color.Foreground.value == "CUSTOM":
				_Foreground = getHexColor(config.plugins.MyMetrix.Color.Foreground_Custom.value)
			else:
				_Foreground = config.plugins.MyMetrix.Color.Foreground.value
				
			if config.plugins.MyMetrix.Color.Accent1.value == "CUSTOM":
				_Accent1 = getHexColor(config.plugins.MyMetrix.Color.Accent1_Custom.value)
			else:
				_Accent1 = config.plugins.MyMetrix.Color.Accent1.value
			
			if config.plugins.MyMetrix.Color.Accent2.value == "CUSTOM":
				_Accent2 = getHexColor(config.plugins.MyMetrix.Color.Accent2_Custom.value)
			else:
				_Accent2 = config.plugins.MyMetrix.Color.Accent2.value
			
			if config.plugins.MyMetrix.Color.Background.value == "CUSTOM":
				_transparent = getHexColor(config.plugins.MyMetrix.Color.Background_Custom.value,255)
			else:
				_transparent = config.plugins.MyMetrix.Color.Background.value.replace("#00","#ff")
			if config.plugins.MyMetrix.Color.BackgroundMode.value != "Dynamic":
				_transparent = config.plugins.MyMetrix.Color.BackgroundMode.value.replace("#00","#ff")
					
			colors = skinNode.getElementsByTagName('colors')[0]
			for color in colors.getElementsByTagName('color'):
				colorname = color.getAttributeNode('name').nodeValue
				metrixTools.callOnMainThread(self["output"].setText,_(str("Setting color: " + colorname)))
				if colorname == "metrixSelection":
					color.setAttribute('value',_selection)
				elif colorname == "metrixBackground":
					color.setAttribute('value',_background)
				elif colorname == "metrixBackground2":
					color.setAttribute('value',_background2)
				elif colorname == "metrixPreTrans":
					color.setAttribute('value',_BackgroundText)
				elif colorname == "metrixPreTrans2":
					color.setAttribute('value',_BackgroundText)
				elif colorname == "metrixForeground":
					color.setAttribute('value',_Foreground)
				elif colorname == "metrixAccent1":
					color.setAttribute('value',_Accent1)
				elif colorname == "metrixAccent2":
					color.setAttribute('value',_Accent2)
				elif colorname == "transparent":
					color.setAttribute('value',_transparent)
		except Exception, e:
			metrixTools.callOnMainThread(self["output"].setText,_(str("Error setting colors!")))
			metrixTools.log("Error setting colors",e)

	def restartGUI(self, answer):
		if answer is True:
			config.plugins.MetrixUpdater.Reboot.value = 0
			config.plugins.MetrixUpdater.save()    
			configfile.save()
			self.session.open(TryQuitMainloop, 3)
		else:
			self.close()
		
	def exit(self):
		self.close()

