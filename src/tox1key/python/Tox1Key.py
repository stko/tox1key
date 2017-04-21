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
import json
import hashlib
import struct
import binascii

#debugging stuff
from pprint import pprint
from random import randint
import traceback

from pytoxcore import ToxCore, ToxCoreException


try:
    dict.iteritems
except AttributeError:
    def itervalues(d):
        return iter(d.values())
    def iteritems(d):
        return iter(d.items())
    def listvalues(d):
        return list(d.values())
    def listitems(d):
        return list(d.items())
else:
    def itervalues(d):
        return d.itervalues()
    def iteritems(d):
        return d.iteritems()
    def listvalues(d):
        return d.values()
    def listitems(d):
        return d.items()


class Tox1KeyOptions(object):
    """
    basic options
    """
    def __init__(self, options):
        """
        Аргументы:
            options (dict) -- basic options
        """
        self.debug          = self._bool(options["debug"])
        self.verbose        = self._bool(options["verbose"]) or self.debug
        self.name           = str(options["name"])
        self.instance_name  = str(options["instance_name"])
        self.status_message = str(options["status_message"])
        self.avatar_ext         = str(options["avatar_ext"])
        self.save_file_ext      = str(options["save_file_ext"])
        self.save_tmp_file_ext  = str(options["save_tmp_file_ext"])
        self.t1k_file_ext      = str(options["t1k_file_ext"])
        self.t1k_tmp_file_ext  = str(options["t1k_tmp_file_ext"])
        self.save_interval  = int(options["save_interval"])
        self.bootstrap_host = str(options["bootstrap_host"])
        self.bootstrap_port = int(options["bootstrap_port"])
        self.bootstrap_key  = str(options["bootstrap_key"])
        self.ipv6_enabled   = self._bool(options["ipv6_enabled"])
        self.udp_enabled    = self._bool(options["udp_enabled"])

        proxy_type = options["proxy_type"].lower()
        if len(proxy_type) == 0:
            self.proxy_type = ToxCore.TOX_PROXY_TYPE_NONE
        elif proxy_type == "http":
            self.proxy_type = ToxCore.TOX_PROXY_TYPE_HTTP
        elif proxy_type == "socks":
            self.proxy_type = ToxCore.TOX_PROXY_TYPE_SOCKS5
        else:
            raise ValueError("Unknown proxy type: {0}".format(options["proxy_type"]))

        self.proxy_host = str(options["proxy_host"])
        self.proxy_port = int(options["proxy_port"])
        self.start_port = int(options["start_port"])
        self.end_port   = int(options["end_port"])
        self.tcp_port   = int(options["tcp_port"])

        self.accept_avatars  = self._bool(options["accept_avatars"])
        self.max_avatar_size = int(options["max_avatar_size"])
        self.avatars_path    = str(options["avatars_path"])
        self.accept_files    = self._bool(options["accept_files"])
        self.max_file_size   = int(options["max_file_size"])
        self.files_path      = str(options["files_path"])


    def __repr__(self):
        return "{0!s}({1!r})".format(self.__class__, self.__dict__)


    @staticmethod
    def _bool(value):
        """
	Converting a String Value to a Boolean

	Arguments:
	Value (str | bool) - String representation of a Boolean value

	Result (bool):
	The result of converting a string value to a boolean is [true | yes | t | y | 1] => True, otherwise False
        """
        if type(value) is bool:
            return value

        value = value.lower().strip()

        if value == "true" or value == "yes" or value == "t" or value == "y" or value == "1":
            return True

        return False


    @staticmethod
    def defaultOptions():
        """
	Default Options

	Result (dict):
	Default options dictionary
        """
        tox_opts = ToxCore.tox_options_default()

        options = {
	    "instance_name"   : "echobot",
            "debug"           : "yes",
            "verbose"         : "yes",
            "name"            : "Tox1Key",
            "status_message"  : "Think Safety",
            "avatar_ext"      : ".png",
            "save_file_ext"   : ".data",
            "save_tmp_file_ext" : ".data.tmp",
            "t1k_file_ext"   : ".json",
            "t1k_tmp_file_ext" : ".json.tmp",
            "max_trans_errors" : 5,
            "save_interval"   : "300",
            "bootstrap_host"  : "178.62.250.138",   # https://wiki.tox.chat/users/nodes
            "bootstrap_port"  : "33445",
            "bootstrap_key"   : "788236D34978D1D5BD822F0A5BEBD2C53C64CC31CD3149350EE27D4D9A2F9B6B",
            "ipv6_enabled"    : "yes" if tox_opts["ipv6_enabled"] else "no",
            "udp_enabled"     : "yes" if tox_opts["udp_enabled"]  else "no",
            "proxy_type"      : "",
            "proxy_host"      : "" if tox_opts["proxy_host"] is None else tox_opts["proxy_host"],
            "proxy_port"      : str(tox_opts["proxy_port"]),
            "start_port"      : str(tox_opts["start_port"]),
            "end_port"        : str(tox_opts["end_port"]),
            "tcp_port"        : str(tox_opts["tcp_port"]),
            "accept_avatars"  : "no",
            "max_avatar_size" : "0",
            "avatars_path"    : "",
            "accept_files"    : "no",
            "max_file_size"   : "0",
            "files_path"      : "",
        }

        if tox_opts["proxy_type"] == ToxCore.TOX_PROXY_TYPE_SOCKS5:
            options["proxy_type"] = "socks"
        elif tox_opts["proxy_type"] == ToxCore.TOX_PROXY_TYPE_HTTP:
            options["proxy_type"] = "http"
        elif tox_opts["proxy_type"] != ToxCore.TOX_PROXY_TYPE_NONE:
            raise NotImplementedError("Unknown proxy_type: {0}".format(tox_opts["proxy_type"]))

        return options


    @staticmethod
    def loadOptions(filename, options = None):
        """
	Reading the cfg file

	Arguments:
		Filename (str) - The name of the json file
		Options (dict) - Basic configuration

	Result (dict):
		Configuration of the application based on the configuration file
        """
        if options is None:
            options = Tox1KeyOptions.defaultOptions()

        options = options.copy()

	try:
		with open(filename) as data_file:    
			options = json.load(data_file)
	except :
		options = Tox1KeyOptions.defaultOptions()
        return options


class Tox1Key(ToxCore):
    """
    Boot
    """
    T1K_CMD_TRANSFERREQ = 1 
    T1K_CMD_BLOCKREQ = 2
    T1K_CMD_BLOCK = 3
    T1K_CMD_TRANSFERCANCEL = 4
    T1K_TRANSFER_MAX_SIZE = 5000 # max allowed transfer data size
    
    
    def __init__(self, options):
        """
        Arguments:
		Options (Tox1KeyOptions) - Application Options
        """
        self.options = options

        tox_opts = {
            "ipv6_enabled" : self.options.ipv6_enabled,
            "udp_enabled"  : self.options.udp_enabled,
            "proxy_type"   : self.options.proxy_type,
            "proxy_host"   : self.options.proxy_host,
            "proxy_port"   : self.options.proxy_port,
            "start_port"   : self.options.start_port,
            "end_port"     : self.options.end_port,
            "tcp_port"     : self.options.tcp_port
        }

        if os.path.isfile(self.options.instance_name+self.options.save_file_ext):
            self.debug("Load data from file: {0}".format(self.options.instance_name+self.options.save_file_ext))
            with open(self.options.instance_name+self.options.save_file_ext, "rb") as f:
                tox_opts["savedata_type"] = ToxCore.TOX_SAVEDATA_TYPE_TOX_SAVE
                tox_opts["savedata_data"] = f.read()

        super(Tox1Key, self).__init__(tox_opts)

        self.debug("Set self instance name: {0}".format(self.options.instance_name))
        self.tox_self_set_name(self.options.instance_name)

        self.debug("Set self status: {0}".format(self.options.status_message))
        self.tox_self_set_status_message(self.options.status_message)

        self.debug("Get self ToxID: {0}".format(self.tox_self_get_address()))
        self.db=self.loadT1kdb(self.options.instance_name+self.options.t1k_file_ext)
	# try to read master IDs, if door
	if self.options.isDoor:
		try:
			self.debug("try to open masters file: {0}".format(self.options.instance_name+".masters"))
			with open(self.options.instance_name+".masters") as data_file: 
				global masters
				masters = json.load(data_file)
				pprint(masters)
				for address in masters["masters"]:
					public_key=address[:64]
					try:
						friendNr=self.tox_friend_by_public_key(public_key)
						print(friendNr)
					except ToxCoreException:
						print(len(address))
						print(address)
						print(masters["welcome"])
						friendNr=self.tox_friend_add(address, masters["welcome"])
						self.debug("new master {0} added as {1}".format(address,friendNr))
					if not public_key in self.db:
						self.db[public_key]={}
						self.db[public_key]["frames"]={"name" : self.options.instance_name}
						self.db[public_key]["grants"]={"name" : self.options.instance_name}
					self.db[public_key]["friend_number"]=friendNr
		except :
			traceback.print_exc()
		



    def loadT1kdb(self,filename):
        """
	Reading the Tox1Key settings

	Arguments:
		Filename (str) - The name of the json file

	Result (dict):
		Configuration of the t1kuser
        """


	try:
		with open(filename) as data_file:    
			db = json.load(data_file,encoding="utf-8")
	except :
		db = {}
        return db




    def debug(self, message):
        """
	Output of debugging information

	Arguments:
		Message (str) - Message for output
        """
        if self.options.debug:
            sys.stderr.write("[{0}] {1}\n".format(time.strftime("%Y-%m-%d %H:%M:%S"), message))


    def verbose(self, message):
        """
	Extended information output

	Arguments:
		Message (str) - Message for output
        """
        if self.options.verbose:
            sys.stderr.write("[{0}] {1}\n".format(time.strftime("%Y-%m-%d %H:%M:%S"), message))


    def run(self):
        """
	Operation cycle
        """
        self.debug("Connecting to: {0} {1} {2}".format(self.options.bootstrap_host, self.options.bootstrap_port, self.options.bootstrap_key))
        self.tox_bootstrap(self.options.bootstrap_host, self.options.bootstrap_port, self.options.bootstrap_key)
        self.debug("Connected to: {0} {1} {2}".format(self.options.bootstrap_host, self.options.bootstrap_port, self.options.bootstrap_key))

        checked       = False
        savetime      = 0
        save_interval = self.options.save_interval * 1000

        while True:
            status = self.tox_self_get_connection_status()

            if not checked and status != ToxCore.TOX_CONNECTION_NONE:
                checked = True

            if checked and status == ToxCore.TOX_CONNECTION_NONE:
                self.debug("Connecting to: {0} {1} {2}".format(self.options.bootstrap_host, self.options.bootstrap_port, self.options.bootstrap_key))
                self.tox_bootstrap(self.options.bootstrap_host, self.options.bootstrap_port, self.options.bootstrap_key)
                self.debug("Connected to: {0} {1} {2}".format(self.options.bootstrap_host, self.options.bootstrap_port, self.options.bootstrap_key))
                checked = False

            self.tox_iterate()

            interval = self.tox_iteration_interval()

            time.sleep(float(interval) / 1000.0)

            savetime += interval
            if savetime > save_interval:
                self.save_file()
                self.send_frame_hashes()
                savetime = 0


    def save_file(self):
        """
	Saving data
        """
        self.debug("Save data to file: {0}".format(self.options.instance_name+self.options.save_tmp_file_ext))

        with open(self.options.instance_name+self.options.save_tmp_file_ext, "wb") as f:
            f.write(self.tox_get_savedata())

        self.debug("Move data to file: {0}".format(self.options.instance_name+self.options.save_file_ext))
        os.rename(self.options.instance_name+self.options.save_tmp_file_ext, self.options.instance_name+self.options.save_file_ext)

        self.debug("Save t1k data to file: {0}".format(self.options.instance_name+self.options.t1k_tmp_file_ext))

        with open(self.options.instance_name+self.options.t1k_tmp_file_ext, "w") as f:
		pprint(self.db)
		json.dump(self.db, f)

        self.debug("Move data to file: {0}".format(self.options.instance_name+self.options.t1k_file_ext))
        os.rename(self.options.instance_name+self.options.t1k_tmp_file_ext, self.options.instance_name+self.options.t1k_file_ext)


    def send_avatar(self, friend_number):
        """
	Sending an avatar

	Agruments:
		Friend_number (int) - Friend number
        """
        if len(self.options.avatar_ext) == 0 or not os.path.isfile(self.options.instance_name+self.options.avatar_ext):
            return

        friend_name = self.tox_friend_get_name(friend_number)
        self.verbose("Send avatar to {0}/{1}".format(friend_name, friend_number))

        self.tox_sendfile(friend_number, ToxCore.TOX_FILE_KIND_AVATAR, self.options.instance_name+self.options.avatar_ext, "", 60)


    def send_file(self, friend_number, path, name = None):
        """
	Sending a file

	Arguments:
		Friend_number (int) - Friend number
		Path (str) - Path to file
		Name (str) - The name of the file (optional, if it does not match the name of the path)
        """
        if not os.path.isfile(path):
            return

        friend_name = self.tox_friend_get_name(friend_number)

        if name:
            self.verbose("Send file {0} as {1} to {2}/{3}".format(path, name, friend_name, friend_number))
        else:
            self.verbose("Send file {0} to {1}/{2}".format(path, friend_name, friend_number))

        if not name:
            name = os.path.basename(path)

        self.tox_sendfile(friend_number, ToxCore.TOX_FILE_KIND_DATA, path, name, 60)


    def tox_self_connection_status_cb(self, connection_status):
        """
	Change the state of the connection

	Arguments:
		Connection_status (int) - Status
        """
        if connection_status == ToxCore.TOX_CONNECTION_NONE:
            self.debug("Disconnected from DHT")
        elif connection_status == ToxCore.TOX_CONNECTION_TCP:
            self.debug("Connected to DHT via TCP")
        elif connection_status == ToxCore.TOX_CONNECTION_UDP:
            self.debug("Connected to DHT via UDP")
        else:
            raise NotImplementedError("Unknown connection_status: {0}".format(connection_status))


    def tox_friend_request_cb(self, public_key, message):
        """
	Request to add to friends

	Arguments:
		Public_key (str) - Public key of a friend
		Message (str) - Request message to add to friends
        """
        self.verbose("Friend request from {0}: {1}".format(public_key, message))
        if not options.isDoor: # I'm a normal user, not a door, so I could accept here
		self.tox_friend_add_norequest(public_key)
		self.verbose("Friend request from {0}: accepted".format(public_key))
		if not public_key in self.db:
			self.db[public_key]={}
			self.db[public_key]["grants"]={"name" : self.options.instance_name}
			self.db[public_key]["frames"]={"name" : self.options.instance_name}
		self.db[public_key]["frames"]["name"]= options.instance_name


    def tox_friend_connection_status_cb(self, friend_number, connection_status):
        """
	Changing the status of a friend's connection

	Arguments:
		Friend_number (int) - Friend number
		Connection_status (int) - Friend's connection status (see enum TOX_CONNECTION)
		"""
        friend_name = self.tox_friend_get_name(friend_number)

        if connection_status == ToxCore.TOX_CONNECTION_NONE:
            self.verbose("Friend {0}/{1} is offline".format(friend_name, friend_number))
        elif connection_status == ToxCore.TOX_CONNECTION_TCP:
            self.verbose("Friend {0}/{1} connected via TCP".format(friend_name, friend_number))
        elif connection_status == ToxCore.TOX_CONNECTION_UDP:
            self.verbose("Friend {0}/{1} connected via UDP".format(friend_name, friend_number))
        else:
            raise NotImplementedError("Unknown connection_status: {0}".format(connection_status))

        if connection_status == ToxCore.TOX_CONNECTION_TCP or connection_status == ToxCore.TOX_CONNECTION_UDP:
            self.send_avatar(friend_number)
            self.send_frame_hash(friend_number)

    def send_frame_hash(self, friend_number):
	public_key=self.tox_friend_get_public_key(friend_number)
	m = hashlib.md5() #it would be more performant to have this as a global
	try:
		self.db[public_key]["confirmation"]
	except: # initialize the data
		self.db[public_key]={}
		self.db[public_key]["grants"]={"name" : self.options.instance_name}
		self.db[public_key]["frames"]={"name" : self.options.instance_name}
		self.db[public_key]["confirmation"]=1  #the 1 is just a dummy
		self.db[public_key]["grantError"]=0  #counting the trials to update the other side
		self.db[public_key]["frameError"]=0  #counting the trials to update the other side
		m.update(json.dumps(self.db[public_key]["grants"]))
		grantHash= m.hexdigest()
		m.update(json.dumps(self.db[public_key]["frames"]))
		frameHash= m.hexdigest()
		self.db[public_key]["grantHash"]=grantHash
		self.db[public_key]["frameHash"]=frameHash
	if self.db[public_key]["confirmation"]!=-1:
		message_id = self.tox_friend_send_message(friend_number, ToxCore.TOX_MESSAGE_TYPE_NORMAL, "hashes:"+grantHash+":"+frameHash)
		self.db[public_key]["confirmation"]=message_id
		self.verbose("Hash compare sent with msg_id {0}".format(message_id))

    def send_frame_hashes(self):
	    for public_key in self.db:
		    if self.db[public_key]["confirmation"]!=-1:
			friend_number= tox_friend_by_public_key(public_key)
			connection_status=tox_friend_get_connection_status(friend_number)
			if connection_status == ToxCore.TOX_CONNECTION_TCP or connection_status == ToxCore.TOX_CONNECTION_UDP:
				self.send_frame_hash(self, friend_number)
					
    def tox_friend_name_cb(self, friend_number, name):
        """
	Change friend's name

	Arguments:
		Friend_number (int) - Friend number
		Name (str) - New name        """
        self.verbose("Friend name change {0}/{1}".format(name, friend_number))


    def tox_friend_status_message_cb(self, friend_number, message):
        """
	Change of status message

	Arguments:
		Friend_number (int) - Friend number
		Message (str) - Status message
        """
        friend_name = self.tox_friend_get_name(friend_number)

        self.verbose("Friend status message change {0}/{1}: {2}".format(friend_name, friend_number, message))


    def tox_friend_status_cb(self, friend_number, status):
        """
	Change of status

	Arguments:
		Friend_number (int) - Friend number
		Status (int) - Status (see TOX_USER_STATUS)
        """
        friend_name = self.tox_friend_get_name(friend_number)

        if status ==ToxCore.TOX_USER_STATUS_NONE:
            self.verbose("Friend {0}/{1} is online now".format(friend_name, friend_number))
        elif status == ToxCore.TOX_USER_STATUS_AWAY:
            self.verbose("Friend {0}/{1} is away now".format(friend_name, friend_number))
        elif status == ToxCore.TOX_USER_STATUS_BUSY:
            self.verbose("Friend {0}/{1} is busy now".format(friend_name, friend_number))
        else:
            raise NotImplementedError("Unknown status: {0}".format(status))


    def tox_friend_message_cb(self, friend_number, message):
        """
	Message from a friend

	Arguments:
		Friend_number (int) - Friend number
		Message (str) - Message
        """
        friend_name = self.tox_friend_get_name(friend_number)

        self.verbose("Message from {0}/{1}: {2}".format(friend_name, friend_number, message))
        public_key=self.tox_friend_get_public_key(friend_number)
        if public_key in self.db:
		print ("Tox1Key message from {0}".format(public_key))
		m=re.match(r"^hashes:(\w{32}):(\w{32})$",message)
		thisAccount=self.db[public_key]
		if m:
			grantHash=m.group(1)
			frameHash=m.group(2)
			print("grant hash {0}\nframe hash {1}".format(grantHash,frameHash))
			if options.isDoor: #in case we are a door
				if grantHash!=thisAccount["grantHash"] and thisAccount["grantError"]<options.max_trans_errors: #the user don't have the latest grant table, so send it
					self.sendData(friend_number,public_key, thisAccount["grants"])
					thisAccount["grantError"]+=1
				else:
					thisAccount["grantError"]=0
			else:
				if frameHash!=thisAccount["frameHash"] and thisAccount["frameError"]<options.max_trans_errors: #the user don't have the latest grant table, so send it
					self.sendData(friend_number,public_key, thisAccount["frames"])
					thisAccount["frameError"]+=1
				else:
					thisAccount["frameError"]=0

    def sendData(self,friend_number,public_key, obj):
	global sendManager
	try:
		sendManager;
	except:
		sendManager={}
	try:
		sendManager[public_key];
	except:
		sendManager[public_key]={}
		sendManager[public_key]["send"]={}
		sendManager[public_key]["receive"]={}
	thisData=sendManager[public_key]["send"]
	thisData["id"]=randint(1,9999999)
	thisData["data"]=bytearray(json.dumps(obj))
	dataLen=len(thisData["data"])
	self.send_packet_struct (friend_number,self.T1K_CMD_TRANSFERREQ, thisData["id"],dataLen, ToxCore.TOX_MAX_CUSTOM_PACKET_SIZE)
	
	
    def tox_friend_lossless_packet_cb(self, friend_number, packed_data):
	public_key=self.tox_friend_get_public_key(friend_number)
	global sendManager
	try:
		sendManager;
	except:
		sendManager={}
	try:
		sendManager[public_key];
	except:
		sendManager[public_key]={}
		sendManager[public_key]["send"]={}
		sendManager[public_key]["receive"]={}
	thisData=sendManager[public_key]
	if len(packed_data)>=20:
		s = struct.Struct('B 3s I I I I')
		header=packed_data[:20]
		unpacked_data = s.unpack(header)
		print 'Unpacked Values:', unpacked_data
		#check for magic header
		if unpacked_data[1]=="t1k":
			print "Valid header :-)"
			cmd=unpacked_data[2]
			id=unpacked_data[3]
			if cmd==self.T1K_CMD_TRANSFERREQ:
				fileSize=unpacked_data[4]
				blockSize=unpacked_data[5]
				if fileSize>self.T1K_TRANSFER_MAX_SIZE: #the data is too big !!
					return
				blockSize=blockSize if blockSize<=ToxCore.TOX_MAX_CUSTOM_PACKET_SIZE else ToxCore.TOX_MAX_CUSTOM_PACKET_SIZE # choose the blocksize which is allowed on both sides
				thisData["receive"]["id"]=id
				thisData["receive"]["data"]=bytearray()
				thisData["receive"]["fileSize"]=fileSize
				thisData["receive"]["blockNr"]=0
				thisData["receive"]["blockSize"]=blockSize
				self.send_packet_struct (friend_number,self.T1K_CMD_BLOCKREQ, thisData["receive"]["id"],blockSize, thisData["receive"]["blockNr"])
			if cmd==self.T1K_CMD_BLOCKREQ:
				blockSize=unpacked_data[4]
				if blockSize < ToxCore.TOX_MAX_CUSTOM_PACKET_SIZE:
					self.send_packet_struct (friend_number,self.T1K_CMD_TRANSFERCANCEL, thisData["send"]["id"],0, 0)
					return
				if id != thisData["send"]["id"]:
					self.send_packet_struct (friend_number,self.T1K_CMD_TRANSFERCANCEL, thisData["send"]["id"],1, 0)
					return
				blockNr=unpacked_data[5]
				if blockNr * blockSize >= len(thisData["send"]["data"]):
					self.send_packet_struct (friend_number,self.T1K_CMD_TRANSFERCANCEL, thisData["send"]["id"],2, 0)
					return
				self.send_packet_struct (friend_number,self.T1K_CMD_BLOCK, thisData["send"]["id"],blockSize, blockNr,thisData["send"]["data"][blockNr * blockSize:(blockNr+1) * blockSize])
			if cmd==self.T1K_CMD_BLOCK:
				blockSize=unpacked_data[4]
				if blockSize != thisData["receive"]["blockSize"]: #illegal blockSize, stop
					return
				if id != thisData["receive"]["id"]: #illegal id, stop
					return
				blockNr=unpacked_data[5]
				if blockNr != thisData["receive"]["blockNr"]:#illegal blocknr, stop
					return
				print("received block nr. {0}".format(blockNr))
				# store the received bytes
				thisData["receive"]["data"].extend(packed_data[20:])
				thisData["receive"]["blockNr"]+=1
				if thisData["receive"]["blockNr"] * blockSize >= len(thisData["receive"]["data"]): #end of packet reached
					pprint(thisData["receive"]["data"])
				else: #request next block
					self.send_packet_struct (friend_number,self.T1K_CMD_BLOCKREQ, thisData["receive"]["id"],blockSize, thisData["receive"]["blockNr"])
				
				
				
    def send_packet_struct(self,friend_number, cmd, integer1, integer2, integer3, attachment=None):
	values = (160, "t1k", cmd, integer1,integer2, integer3)
	s = struct.Struct('B 3s I I I I')
	packed_data = bytearray(s.pack(*values))
	if attachment != None:
		packed_data.extend(attachment)
	print 'Original values:', values
	print 'Format string  :', s.format
	print 'Uses           :', s.size, 'bytes'
	print 'Packed Value   :', binascii.hexlify(packed_data)
	
	self.tox_friend_send_lossless_packet(friend_number,str(packed_data))


    def tox_friend_read_receipt_cb(self, friend_number, message_id):
        """
	Receipt for the delivery of the message

	Arguments:
		Friend_number (int) - Friend number
		Message_id (int) - Message ID
        """
        friend_name = self.tox_friend_get_name(friend_number)

        self.verbose("Message receipt {0} from {1}/{2}".format(message_id, friend_name, friend_number))
	public_key=self.tox_friend_get_public_key(friend_number)
	
	if self.db[public_key]["confirmation"]==message_id:
		self.db[public_key]["confirmation"]=-1


    def can_accept_file(self, friend_number, file_number, kind, file_size, filename):
        """
	Verifying that the file can be received

	Arguments:
		Friend_number (int) - Friend number
		File_number (int) - File number (random number within transmission)
		Kind (int) - The value of the file (see TOX_FILE_KIND)
		File_size (int) - File size
		Filename (str) - Filename

	Result (bool):
		Accepted file acceptance flag
        """
        # flow?
        if file_size <= 0:
            return False

        if kind == ToxCore.TOX_FILE_KIND_DATA:
            return (
                self.options.accept_files and
                (self.options.max_file_size == 0 or file_size <= self.options.max_file_size) and
                (os.path.isdir(self.options.files_path)))

        elif kind == ToxCore.TOX_FILE_KIND_AVATAR:
            return (
                self.options.accept_avatars and
                (self.options.max_avatar_size == 0 or file_size <= self.options.max_avatar_size) and \
                (os.path.isdir(self.options.avatars_path)))

        raise NotImplementedError("Unknown kind: {0}".format(kind))


    def tox_file_recv_cb(self, friend_number, file_number, kind, file_size, filename):
        """
	Getting the file
	(See tox_file_recv_cb)

	Arguments:
		Friend_number (int) - Friend number
		File_number (int) - File number (random number within transmission)
		Kind (int) - The value of the file (see TOX_FILE_KIND)
		File_size (int) - File size
		Filename (str) - Filename
	"""
        friend_name = self.tox_friend_get_name(friend_number)

        if kind == ToxCore.TOX_FILE_KIND_DATA:
            file_id = self.tox_file_get_file_id(friend_number, file_number)
            self.verbose("File from {0}/{1}: number = {2}, size = {3}, id = {4}, name = {5}".format(friend_name, friend_number, file_number, file_size, file_id, filename))
        elif kind == ToxCore.TOX_FILE_KIND_AVATAR:
            filename = ""
            if file_size != 0:
                file_id = self.tox_file_get_file_id(friend_number, file_number)
                self.verbose("Avatar from {0}/{1}: number = {2}, size = {3}, id = {4}".format(friend_name, friend_number, file_number, file_size, file_id))
            else:
                self.verbose("No Avatar from {0}/{1}: number = {2}".format(friend_name, friend_number, file_number))
        else:
            raise NotImplementedError("Unknown kind: {0}".format(kind))

        if self.can_accept_file(friend_number, file_number, kind, file_size, filename):
            if kind == ToxCore.TOX_FILE_KIND_DATA:
                path = self.options.files_path + "/" + file_id
            elif kind == ToxCore.TOX_FILE_KIND_AVATAR:
                path = self.options.avatars_path + "/" + file_id

            self.tox_recvfile(friend_number, file_number, file_size, path, filename, 60)
        else:
            self.tox_file_control(friend_number, file_number, ToxCore.TOX_FILE_CONTROL_CANCEL)


    def tox_file_recv_control_cb(self, friend_number, file_number, control):
        """
	Controlling the receipt of a file
	(See tox_file_recv_control_cb)

	Arguments:
		Friend_number (int) - Friend number
		File_number (int) - File number (random number within transmission)
		Control (int) - The control command received (see TOX_FILE_CONTROL)
        """
        friend_name = self.tox_friend_get_name(friend_number)

        if control == ToxCore.TOX_FILE_CONTROL_RESUME:
            self.verbose("File resumed from {0}/{1}: number = {2}".format(friend_name, friend_number, file_number))
        elif control == ToxCore.TOX_FILE_CONTROL_PAUSE:
            self.verbose("File paused from {0}/{1}: number = {2}".format(friend_name, friend_number, file_number))
        elif control == ToxCore.TOX_FILE_CONTROL_CANCEL:
            self.verbose("File canceled from {0}/{1}: number = {2}".format(friend_name, friend_number, file_number))
        else:
            raise NotImplementedError("Unknown control: {0}".format(control))


    def tox_recvfile_cb(self, friend_number, file_number, path, filename, status):
        """
	Monitoring execution of tox_recvfile

	Arguments:
		Friend_number (int) - Friend number
		File_number (int) - File number (random number within transmission)
		Status (int) - File receiving status
        """
        friend_name = self.tox_friend_get_name(friend_number)

        if status == ToxCore.TOX_RECVFILE_COMPLETED:
            self.verbose("recvfile completed to {0}/{1}: number = {2}".format(friend_name, friend_number, file_number))

            file_id = self.tox_file_get_file_id(friend_number, file_number)
            path = self.options.files_path + "/" + file_id
            if os.path.isfile(path):
                self.tox_sendfile(friend_number, ToxCore.TOX_FILE_KIND_DATA, path, filename, 60)

        elif status == ToxCore.TOX_RECVFILE_TIMEOUT:
            self.verbose("recvfile timeout to {0}/{1}: number = {2}".format(friend_name, friend_number, file_number))
        elif status == ToxCore.TOX_RECVFILE_ERROR:
            self.verbose("recvfile error to {0}/{1}: number = {2}".format(friend_name, friend_number, file_number))
        else:
            raise NotImplementedError("Unknown status: {0}".format(status))


if __name__ == "__main__":
	
	
    regexpDoor  = re.compile("--door")
    isDoor = [True for arg in sys.argv for match in [regexpDoor.search(arg)] if match]
    regexp  = re.compile("--name=(\w+)")
    cfgfile = [match.group(1) for arg in sys.argv for match in [regexp.search(arg)] if match]

    if len(cfgfile) == 0:
	    print("Usage: Tox1Key.py --name=<instancename> [--door]")
	    exit(1)
    else:
        instance_name = cfgfile[0]
        cfgfile = instance_name+".cfg"
    if len(isDoor) == 0:
	    isDoor = False
    else:
        isDoor = isDoor[0]
    print("Door",isDoor)

    options = Tox1KeyOptions(Tox1KeyOptions.loadOptions(cfgfile))
    options.instance_name=instance_name
    options.isDoor=isDoor
    bot = Tox1Key(options)

    try:
        bot.run()
    except KeyboardInterrupt:
        bot.save_file()
