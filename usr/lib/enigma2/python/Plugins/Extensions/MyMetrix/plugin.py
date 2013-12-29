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
import store_Packages_Categories
import metrix_MainMenu
from enigma import addFont
#from xml.etree.ElementTree import parse
addFont('/usr/share/fonts/setrixHD.ttf', 'SetrixHD', 100, False)
addFont('/usr/share/fonts/meteocons.ttf', 'Meteo', 100, False)

		
def startMetrixDeamon(reason, **kwargs):
	metrixConnector.syncStart(global_session)			

def startSession(reason, session):
	global global_session
	global_session = session


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

def menu_openstore (menuid, **kwargs):
    if menuid == "mainmenu":
            return [(_("OpenStore"), openStore, "openstore", 15)]
    return []

def main(session, **kwargs):
	session.open(metrix_MainMenu.OpenScreen)
	
def openStore(session, **kwargs):
	session.open(store_Packages_Categories.OpenScreen)
	

def Plugins(**kwargs):
	descriptor = [PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=startSession),
		PluginDescriptor(where=[PluginDescriptor.WHERE_NETWORKCONFIG_READ], fnc=startMetrixDeamon),
		PluginDescriptor(name="MyMetrix", description=_("Metrify Your Set-Top Box"), where = [ PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU ], icon="plugin.png", fnc=main),
		PluginDescriptor(name="OpenStore", description=_("Explore The Variety Of Your Set-Top Box"), where = [ PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU ], icon="plugin-store.png", fnc=openStore)]
	#if config.plugins.MyMetrix.showInMainMenu.value:
	#	descriptor.append(PluginDescriptor(name="OpenStore", description=_("Explore The Variety Of Your Set-Top Box"), where = [PluginDescriptor.WHERE_MENU], fnc=menu_openstore))
	return descriptor



#######################################################################		
		
	
