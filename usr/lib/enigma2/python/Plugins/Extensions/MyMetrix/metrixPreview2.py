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
import gettext
from enigma import ePicLoad
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import metrixDefaults
from enigma import addFont
from datetime import datetime
from time import gmtime, strftime
from metrixTools import getHex, getHexColor
import metrixSubmitDesign
import os



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

def main(session, **kwargs):
	session.open(MyMetrixPreview2Window)

#######################################################################		
		

class MyMetrixPreview2Window(ConfigListScreen, Screen):
	skin = """
<screen name="MyMetrix-Preview" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">
  <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/preview/ico_dolby_on.png" position="1020,670" size="64,23" zPosition="1" alphatest="blend" />
  <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/preview/ico_format_on.png" position="1156,668" size="41,26" zPosition="1" alphatest="blend" />
  <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/preview/ico_txt_off.png" position="981,669" size="28,24" zPosition="1" alphatest="blend" />
  <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/preview/ico_hd_off.png" position="1095,670" size="49,24" zPosition="1" alphatest="blend" />
  <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/preview/ico_crypt_on.png" position="1209,668" size="27,25" zPosition="1" alphatest="blend" />
  <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/preview/ico_hbbtv_on.png" position="907,669" size="64,24" zPosition="1" alphatest="blend" />
  <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/preview/subtitle_off.png" position="867,671" size="30,22" alphatest="blend" />
 <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/picon.png" position="39,570" zPosition="4" size="220,132" transparent="1" alphatest="blend" />

<widget position="-1,560" size="1283,160" zPosition="-10" name="InfoBar_BG" />
<widget name="ClockWidget_BG" position="913,40" zPosition="-1" size="320,70" transparent="0" />
  <widget name="WeatherWidget_BG" position="46,40" size="213,70" />
  <widget name="WeatherWidget_BG2" position="259,43" size="105,65" />
<widget name="Clock" position="1081,31" size="169,80" font="SetrixHD; 60" halign="left" transparent="1" valign="top" />
<widget name="Clock_Day" position="944,46" size="125,30" font="Regular; 18" halign="right" transparent="1" />
<widget name="Clock_Date" position="921,77" size="148,29" font="Regular; 18" halign="right" transparent="1" />





<widget name="Now" position="286,558" size="788,56" font="SetrixHD; 40" halign="left" transparent="1" />
<widget name="Next" position="286,624" size="825,40" font="Regular; 24" halign="left" transparent="1" valign="top" />

<widget name="Now_Time" position="1082,563" size="155,30" font="Regular; 19" halign="right" transparent="1" />
<widget name="Now_Timer" position="1125,586" size="113,30" font="Regular; 19" halign="right" transparent="1" />

<widget name="Next_Timer" position="1124,624" size="113,30" font="Regular; 18" halign="right" transparent="1" />

<widget name="ProgressBar" position="288,619" size="450,3" zPosition="7" transparent="0" />
<widget name="ProgressBarBack" position="288,620" size="950,1" />



<widget name="Temp" position="45,47" size="78,55" font="SetrixHD; 55" zPosition="10" halign="right" valign="center" transparent="1" noWrap="1" />
<widget name="TempC" position="123,49" size="30,26" font="Regular; 17" zPosition="10" halign="left" valign="center" transparent="1" noWrap="1" />
<widget name="TempCode" position="156,50" size="50,50" font="Meteo; 45" zPosition="10" halign="left" valign="center" transparent="1" noWrap="1" />

<widget name="TempA" position="210,50" size="39,26" font="Regular; 16" zPosition="10" halign="right" valign="center" transparent="1" noWrap="1" />
 <widget name="TempB" position="210,76" size="39,26" font="Regular; 16" zPosition="10" halign="right" valign="center" transparent="1" noWrap="1" />


<widget name="TempCode2" position="265,50" size="50,50" font="Meteo; 45" zPosition="10" halign="left" valign="center" transparent="1" noWrap="1" />
<widget name="TempC2" position="317,50" size="39,26" font="Regular; 16" zPosition="10" halign="right" valign="center" transparent="1" noWrap="1" />
<widget name="TempD" position="317,76" size="39,26" font="Regular; 16" zPosition="10" halign="right" valign="center" transparent="1" noWrap="1" />


 <widget name="B" font="Regular; 20" position="285,667" size="18,33" halign="center" transparent="1" valign="center" zPosition="3" />
  <widget name="I" font="Regular; 20" position="303,667" size="18,33" halign="center" transparent="1" valign="center" zPosition="3" />
  <widget name="S" font="Regular; 20" position="321,667" size="18,33" halign="center" transparent="1" valign="center" zPosition="3" />
  <widget name="V" font="Regular; 20" position="339,667" size="18,33" halign="center" transparent="1" valign="center" zPosition="3" />
  <widget name="N" font="Regular; 20" position="357,667" size="18,33" halign="center" transparent="1" valign="center" zPosition="3" />


  <widget name="CW" font="Regular; 20" position="375,667" size="44,33" halign="center" transparent="1" valign="center" zPosition="3" />
  <widget name="ND" font="Regular; 20" position="419,667" size="42,33" halign="center" transparent="1" valign="center" zPosition="3" />
  <widget name="CO" font="Regular; 20" position="461,667" size="40,33" halign="center" transparent="1" valign="center" zPosition="3" />
  <widget name="Crypt" font="SetrixHD; 22" position="357,694" size="18,3" halign="center" zPosition="4" transparent="0" valign="top" />

<widget name="Channelname" position="35,405" size="1252,306" font="SetrixHD; 140" valign="top" noWrap="1" transparent="1" zPosition="-30" />

</screen>
"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		
		lorem = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet."
		
		self["InfoBar_BG"] = Label()
		self["WeatherWidget_BG"] = Label()
		self["WeatherWidget_BG2"] = Label()
		self["ClockWidget_BG"] = Label()
		self["Clock"] = Label(_(str(strftime("%H:%M", gmtime()))))
		self["EPGNow_BG"] = Label()
		self["EPGNext_BG"] = Label()
		self["Clock_Day"] = Label(_(str(strftime("%A", gmtime()))))
		self["Clock_Date"] = Label(_(str(strftime("%e. %B", gmtime()))))
		
		self["Event_Now"] = Label(_(lorem))
		self["Event_Next"] = Label(_(lorem))
		self["Event_No"] = Label(_("Foreground"))
		self["Event_Ne"] = Label(_("Accent 1"))
		
		self["Now"] = Label(_("Foreground"))
		self["Next"] = Label(_("21:15 - 22:10 Accent 1"))
		
		self["Now_Time"] = Label(_("20:15 - 21:10"))
		self["Now_Timer"] = Label(_("+10 min"))
		self["Next_Timer"] = Label(_("50 min"))
		
		self["ProgressBar"] = Label()
		self["ProgressBarBack"] = Label()
		
		self["Temp"] = Label(_("18"))
		self["TempC"] = Label(_("°C"))
		self["TempA"] = Label(_("23°C"))
		self["TempB"] = Label(_("16°C"))
		self["TempCode"] = Label(_("H"))
		
		self["TempC2"] = Label(_("18°C"))
		self["TempD"] = Label(_("12°C"))
		self["TempCode2"] = Label(_("R"))
		
		
		
		self["B"] = Label(_("B"))
		self["I"] = Label(_("I"))
		self["S"] = Label(_("S"))
		self["V"] = Label(_("V"))
		self["N"] = Label(_("N"))
		self["CW"] = Label(_("CW"))
		self["ND"] = Label(_("ND"))
		self["CO"] = Label(_("CO"))
		
		self["Channelname"] = Label(_("Background text"))
		
		self["Crypt"] = Label()
		
		
		
		self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions"], {"cancel": self.exit,"ok": self.exit,"green": self.exit}, -1)
		self.onLayoutFinish.append(self.layoutFinish)
		
	def grabScreen(sefl):
		os.system('/usr/bin/grab -d -r 1280 -p /tmp/metrixPreview.png')
		
		#self.onLayoutFinish.append(self.UpdateComponents)
		#if config.plugins.MetrixUpdater.UpdateAvailable.value = 1
	
		
	def layoutFinish(self):
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
			_transparent = getHexColor(config.plugins.MyMetrix.Color.Background_Custom.value,"255")
		else:
			_transparent = config.plugins.MyMetrix.Color.Background.value.replace("#00","#ff")
			
			
		self["InfoBar_BG"].instance.setBackgroundColor(parseColor(_background))
		self["WeatherWidget_BG"].instance.setBackgroundColor(parseColor(_background))
		self["WeatherWidget_BG2"].instance.setBackgroundColor(parseColor(_background2))
		self["EPGNow_BG"].instance.setBackgroundColor(parseColor(_background))
		self["EPGNext_BG"].instance.setBackgroundColor(parseColor(_background2))
		self["ClockWidget_BG"].instance.setBackgroundColor(parseColor(_background))
		self["Clock"].instance.setForegroundColor(parseColor(_Foreground))
		self["Clock"].instance.setBackgroundColor(parseColor(_background))
		self["Clock_Day"].instance.setForegroundColor(parseColor(_Accent1))
		self["Clock_Day"].instance.setBackgroundColor(parseColor(_background))
		self["Clock_Date"].instance.setForegroundColor(parseColor(_Accent1))
		self["Clock_Date"].instance.setBackgroundColor(parseColor(_background))
		
		self["Event_Now"].instance.setForegroundColor(parseColor(_Foreground))
		self["Event_Now"].instance.setBackgroundColor(parseColor(_background))
		self["Event_Next"].instance.setForegroundColor(parseColor(_Accent1))
		self["Event_Next"].instance.setBackgroundColor(parseColor(_background2))
		
		self["Now"].instance.setForegroundColor(parseColor(_Foreground))
		self["Now"].instance.setBackgroundColor(parseColor(_background))
		self["Next"].instance.setForegroundColor(parseColor(_Accent1))
		self["Next"].instance.setBackgroundColor(parseColor(_background))
		
		self["Event_No"].instance.setForegroundColor(parseColor(_Foreground))
		self["Event_No"].instance.setBackgroundColor(parseColor(_background))
		self["Event_Ne"].instance.setForegroundColor(parseColor(_Accent1))
		self["Event_Ne"].instance.setBackgroundColor(parseColor(_background2))
		
		self["Now_Time"].instance.setForegroundColor(parseColor(_Foreground))
		self["Now_Time"].instance.setBackgroundColor(parseColor(_background))
		self["Now_Timer"].instance.setForegroundColor(parseColor(_Foreground))
		self["Now_Timer"].instance.setBackgroundColor(parseColor(_background))
		
		self["Next_Timer"].instance.setForegroundColor(parseColor(_Accent1))
		self["Next_Timer"].instance.setBackgroundColor(parseColor(_background))
		
		self["Channelname"].instance.setForegroundColor(parseColor(_BackgroundText))
		
		self["ProgressBar"].instance.setBackgroundColor(parseColor(config.plugins.MyMetrix.Color.ProgressBar.value))
		self["ProgressBarBack"].instance.setBackgroundColor(parseColor(_Accent1))
		
		self["Temp"].instance.setForegroundColor(parseColor(_Foreground))
		self["Temp"].instance.setBackgroundColor(parseColor(_background))
		self["TempC"].instance.setForegroundColor(parseColor(_Foreground))
		self["TempC"].instance.setBackgroundColor(parseColor(_background))
		self["TempA"].instance.setForegroundColor(parseColor(_Accent1))
		self["TempA"].instance.setBackgroundColor(parseColor(_background))
		self["TempB"].instance.setForegroundColor(parseColor(_Accent2))
		self["TempB"].instance.setBackgroundColor(parseColor(_background))
		self["TempCode"].instance.setForegroundColor(parseColor(_Foreground))
		self["TempCode"].instance.setBackgroundColor(parseColor(_background))
		
		self["TempC2"].instance.setForegroundColor(parseColor(_Accent1))
		self["TempC2"].instance.setBackgroundColor(parseColor(_background2))
		self["TempD"].instance.setForegroundColor(parseColor(_Accent2))
		self["TempD"].instance.setBackgroundColor(parseColor(_background2))
		self["TempCode2"].instance.setForegroundColor(parseColor(_Accent1))
		self["TempCode2"].instance.setBackgroundColor(parseColor(_background2))
		self["Crypt"].instance.setBackgroundColor(parseColor(_selection))
		
		self["B"].instance.setForegroundColor(parseColor(_Foreground))
		self["B"].instance.setBackgroundColor(parseColor(_background))
		
		self["I"].instance.setForegroundColor(parseColor(_Accent1))
		self["I"].instance.setBackgroundColor(parseColor(_background))
		
		self["S"].instance.setForegroundColor(parseColor(_Accent1))
		self["S"].instance.setBackgroundColor(parseColor(_background))
		
		self["V"].instance.setForegroundColor(parseColor(_Accent1))
		self["V"].instance.setBackgroundColor(parseColor(_background))
		
		self["N"].instance.setForegroundColor(parseColor(_Foreground))
		self["N"].instance.setBackgroundColor(parseColor(_background))
		
		self["CW"].instance.setForegroundColor(parseColor(_Accent1))
		self["CW"].instance.setBackgroundColor(parseColor(_background))
		
		self["ND"].instance.setForegroundColor(parseColor(_Foreground))
		self["ND"].instance.setBackgroundColor(parseColor(_background))
		
		self["CO"].instance.setForegroundColor(parseColor(_Accent1))
		self["CO"].instance.setBackgroundColor(parseColor(_background))
		
		self.instance.setBackgroundColor(parseColor(_transparent))
		
		
		
	def exit(self):
		self.grabScreen()
		self.close()
