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

import thread
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
import store_SubmitRating
import threading
import time
import metrixTools
import metrixCore


def installMetrixColors(item_name):
	try:
		data = metrixCore.getWeb(metrixDefaults.URL_GET_METRIXCOLORS,True,{'name':item_name})
		dom = parseString(data)
		for design in dom.getElementsByTagName('design'):
			name = str(design.getAttributeNode('name').nodeValue)
			if name == item_name:
				try:
					config.plugins.MyMetrix.Color.BackgroundTransparency.value = str(design.getAttributeNode('backgroundtrans').nodeValue)
					config.plugins.MyMetrix.Color.SelectionTransparency.value = str(design.getAttributeNode('selectiontrans').nodeValue)
					config.plugins.MyMetrix.Color.BackgroundTextTransparency.value = str(design.getAttributeNode('backgroundtexttrans').nodeValue)
					config.plugins.MyMetrix.Color.Selection.value = str(design.getAttributeNode('selection').nodeValue)
					config.plugins.MyMetrix.Color.ProgressBar.value = str(design.getAttributeNode('progressbars').nodeValue)
					config.plugins.MyMetrix.Color.Background.value = str(design.getAttributeNode('background').nodeValue)
					config.plugins.MyMetrix.Color.Background2.value = str(design.getAttributeNode('background2').nodeValue)
					config.plugins.MyMetrix.Color.Foreground.value = str(design.getAttributeNode('foreground').nodeValue)
					config.plugins.MyMetrix.Color.BackgroundText.value = str(design.getAttributeNode('backgroundtext').nodeValue)
					config.plugins.MyMetrix.Color.Accent1.value = str(design.getAttributeNode('accent1').nodeValue)
					config.plugins.MyMetrix.Color.Accent2.value = str(design.getAttributeNode('accent2').nodeValue)
					
					config.plugins.MyMetrix.Color.Selection_Custom.value = metrixTools.toRGB(str(design.getAttributeNode('selection_custom').nodeValue))
					config.plugins.MyMetrix.Color.Background_Custom.value = metrixTools.toRGB(str(design.getAttributeNode('background_custom').nodeValue))
					config.plugins.MyMetrix.Color.Background2_Custom.value = metrixTools.toRGB(str(design.getAttributeNode('background2_custom').nodeValue))
					config.plugins.MyMetrix.Color.Foreground_Custom.value = metrixTools.toRGB(str(design.getAttributeNode('foreground_custom').nodeValue))
					config.plugins.MyMetrix.Color.BackgroundText_Custom.value = metrixTools.toRGB(str(design.getAttributeNode('backgroundtext_custom').nodeValue))
					config.plugins.MyMetrix.Color.Accent1_Custom.value = metrixTools.toRGB(str(design.getAttributeNode('accent1_custom').nodeValue))
					config.plugins.MyMetrix.Color.Accent2_Custom.value = metrixTools.toRGB(str(design.getAttributeNode('accent2_custom').nodeValue))
					return True
				except Exception, e:
					metrixTools.log("Error setting MetrixColor!",e)
	except Exception, e:
		metrixTools.log("Error downloading MetrixColor!",e)
	return False

	