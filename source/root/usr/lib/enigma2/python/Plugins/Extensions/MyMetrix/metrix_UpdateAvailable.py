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
from Screens.Screen import Screen
from Components.Label import Label
from Components.ActionMap import ActionMap
import threading
from Tools import Notifications
from Screens.Standby import TryQuitMainloop
from Components.ConfigList import ConfigListScreen
import gettext
import metrixDefaults
import metrix_GenerateSkin

#############################################################

config = metrixDefaults.loadDefaults()

def _(txt):
	t = gettext.dgettext("MyMetrix", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

#######################################################################		
		

class OpenScreen(ConfigListScreen, Screen):
	skin = """<screen name="MyMetrix-UpdateAvailable" position="-1,-1" size="1285,64" flags="wfNoBorder" backgroundColor="#40000000">
  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="1115,15" size="163,33" text="Update" transparent="1" />
 
  <eLabel position="20,7" size="226,50" text="OpenStore" font="Regular; 40" valign="center" transparent="1" backgroundColor="#40000000" noWrap="1" />
  <eLabel position="228,7" size="174,50" text="Updater" foregroundColor="#00ffffff" font="Regular; 25" valign="center" backgroundColor="#40000000" transparent="1" halign="left" noWrap="1" />
  <eLabel position="1103,0" size="5,50" backgroundColor="#000000ff" />
   
<widget name="output" position="409,10" size="675,43" foregroundColor="#00ffffff" font="Regular; 22" valign="center" backgroundColor="#40000000" transparent="1" halign="left" noWrap="1" /> 
  </screen>
"""

	def __init__(self, session, message = "SkinPart-Updates available!",generate = True):
		self.generate = generate
		if config.plugins.MetrixUpdater.UpdatePopup_SkinParts.value and generate:
			self.exit()
		
		if config.plugins.MetrixUpdater.UpdatePopup_Packages.value and not generate:
			self.exit()
		
		if config.plugins.MetrixUpdater.Open.value == 0:
			Screen.__init__(self, session)
			self.session = session
			self["output"] = Label(_(message))
			config.plugins.MetrixUpdater.UpdateAvailable.value = 0
			config.plugins.MetrixUpdater.save()    
			self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions"], {"cancel": self.exit,"ok": self.exit,"blue": self.runAction}, -1)
			config.plugins.MetrixUpdater.Open.value = 1
		else:
			self.exit()
			
	def runAction(self):
		if self.generate:
			self.generateSkin()
		else:
			self.reboot()
		
	def reboot(self):
		self.session.open(TryQuitMainloop, 3)
		
	def generateSkin(self):
		self.session.open(metrix_GenerateSkin.OpenScreen)
		
	def exit(self):
		self.close()

