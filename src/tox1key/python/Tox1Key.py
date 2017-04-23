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

from random import randint


if __name__ == "__main__":
	
	
	regexpDoor  = re.compile("--door")
	isDoor = [True for arg in sys.argv for match in [regexpDoor.search(arg)] if match]
	regexp  = re.compile("--name=(\w+)")
	cfgfile = [match.group(1) for arg in sys.argv for match in [regexp.search(arg)] if match]

	if len(cfgfile) == 0:
		print("Usage: ToxBroker.py --name=<instancename> [--door]")
		exit(1)
	instance_name = cfgfile[0]
	cfgfile = instance_name+".cfg"
	if len(isDoor) == 0:
		isDoor = False
	else:
		isDoor = isDoor[0]
	print("Door",isDoor)

	options = ToxBrokerOptions(ToxBrokerOptions.loadOptions(cfgfile))
	options.instance_name=instance_name
	options.isDoor=isDoor
	options.max_trans_errors=5
	t_stop= threading.Event()
	botThread = ToxBrokerThread(options,t_stop)
	botThread.start()
	try:
		while(True):
			time.sleep(2)
			myData={"value": randint(1,9999999)}
			friendsList=botThread.getFriendsPublicKeys()
			for  public_key in friendsList:
				botThread.setNewData(public_key,myData)
	except KeyboardInterrupt:
		pass
	t_stop.set()
	botThread.join()
