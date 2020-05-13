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
from Tox1Key import Tox1Key
#debugging stuff
from pprint import pprint
import traceback

from random import randint

def usage():
	print ("l - list users")
	print ("s - send test data")
	print ("a - add a user")
	
	
if __name__ == "__main__":
	
	
	regexpDoor  = re.compile("--door")
	isDoor = [True for arg in sys.argv for match in [regexpDoor.search(arg)] if match]
	regexp  = re.compile("--name=(\w+)")
	cfgfile = [match.group(1) for arg in sys.argv for match in [regexp.search(arg)] if match]

	if len(cfgfile) == 0:
		print("Usage: ToxBroker.py --name=<instancename> [--door]")
		exit(1)
	instance_name = cfgfile[0]
	if len(isDoor) == 0:
		isDoor = False
	else:
		isDoor = isDoor[0]
	print("Door",isDoor)
	toxKey=Tox1Key(instance_name,isDoor)
	try:
		while(True):
			usage()
			line = raw_input('PROMPT> ')
			if line=="u":
				usage()
				
			if line=="a":
				if isDoor:
					print("I'm a door. Users can only added by friends programmably")
				else:
					newUser = raw_input('new User Tox ID> ')
					if toxKey.addUser(newUser):
						print ("Added")
					else:
						print("Error")
			if line=="s":
				myData={
					"name": instance_name,
					"permissions" : {
						"public_key1": [
							],
						"public_key2": [
							]
						}
						
					}
				friendsList=toxKey.getFriends()
				for  public_key in friendsList:
					toxKey.setData(public_key,myData)
			if line=="l":
				friendsList=toxKey.getFriends()
				for  public_key in friendsList:
					print(public_key)
	except KeyboardInterrupt:
		pass
	toxKey.stop()
