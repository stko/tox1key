#!/usr/bin/env python
# -*- coding: utf-8 -*-

#credits: echobot.py (https://github.com/abbat/pytoxcore) used as starting point

__title__    = "Tox1Key"
__author__   = "Steffen Koehler"
__license__  = "GPL3.0"

import sys
import os
import time
import re
import threading
from ToxBroker import ToxBrokerThread, ToxBrokerOptions

#debugging stuff
from pprint import pprint
import traceback

class Tox1Key:

	def __init__(self, instance_name, isDoor):
		cfgfile = instance_name+".cfg"
		self.options = ToxBrokerOptions(ToxBrokerOptions.loadOptions(cfgfile))
		self.options.instance_name=instance_name
		self.options.isDoor=isDoor
		self.options.max_trans_errors=5
		self.t_stop= threading.Event()
		self.botThread = ToxBrokerThread(self.options,self.t_stop)
		self.botThread.start()
		
	def getFriends(self): # returns a hash with public_key as key and friend data
		result={}
		friendsList=self.botThread.getFriendsPublicKeys()
		for  public_key in friendsList:
			result[public_key]={"name":"nobody"}
		return result

	def setData(self,public_key,newData):
		self.botThread.setNewData(public_key,newData)
		
	def stop(self):
		self.t_stop.set()
		self.botThread.join()
	
	def addUser(self,address):
		if self.options.isDoor:
			return False
		try:
			self.botThread.bot.tox_address_check(address)
			
			return True
		except:
			return False
	
