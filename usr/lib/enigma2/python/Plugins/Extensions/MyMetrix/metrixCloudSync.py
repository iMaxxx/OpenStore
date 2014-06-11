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
import metrixDefaults
import random
import metrixCore
import traceback
import metrixTools


config = metrixDefaults.loadDefaults()

def getSyncRow(area,category,keyname,keydescription,value,order=0):
	row = []
	row.append(area)
	row.append(category)
	row.append(keyname)
	row.append(keydescription)
	row.append(value)
	row.append(order)
	return row
	


def syncNow(sync_data):
	try:
		url = metrixDefaults.URL_STORE_API + 'set.info'
		params = {'data':sync_data}
		metrixCore.getWeb(url,True,params)
	except:
		metrixTools.log("Error on sync")
