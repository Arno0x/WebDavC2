# -*- coding: utf8 -*-
"""

Miscelaneous helper functions used in WebDavC2

"""

import string
import base64
from string import Template
from Crypto.Random import random

#------------------------------------------------------------------------
def b64encode(data):
	return base64.b64encode(data)

def b64decode(data):
	return base64.b64decode(data)

#------------------------------------------------------------------------
def httpdate(dt):
    """
    Return a string representation of a date according to RFC 1123 (HTTP/1.1).
    The supplied date must be in UTC.
    """

    weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
             "Oct", "Nov", "Dec"][dt.month - 1]
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, dt.day, month, dt.year, dt.hour, dt.minute, dt.second)

#------------------------------------------------------------------------
def webdavdate(dt):
	"""
	Return a string as required in a webdav response, in the form '2017-25-07T14:24:12Z'
	"""
	return "%02d-%02d-%02dT%02d:%02d:%02dZ" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
	
#------------------------------------------------------------------------
def chunks(s, n):
	"""
	Author: HarmJ0y, borrowed from Empire
	Generator to split a string s into chunks of size n.
	"""
	for i in xrange(0, len(s), n):
		yield s[i:i+n]

#------------------------------------------------------------------------
def powershellEncode(rawData):
	"""
	Author: HarmJ0y, borrowed from Empire
	Encode a PowerShell command into a form usable by powershell.exe -enc ...
	"""
	return base64.b64encode("".join([char + "\x00" for char in unicode(rawData)]))

#------------------------------------------------------------------------
def convertFromTemplate(parameters, templateFile):
	try:
		with open(templateFile) as f:
			src = Template(f.read())
			result = src.substitute(parameters)
			f.close()
			return result
	except IOError:
		print color("[!] Could not open or read template file [{}]".format(templateFile))
		return None

#------------------------------------------------------------------------
def randomString(length = -1, charset = string.ascii_letters):
    """
    Author: HarmJ0y, borrowed from Empire
    Returns a random string of "length" characters.
    If no length is specified, resulting string is in between 6 and 15 characters.
    A character set can be specified, defaulting to just alpha letters.
    """
    if length == -1: length = random.randrange(6,16)
    random_string = ''.join(random.choice(charset) for x in range(length))
    return random_string

#------------------------------------------------------------------------
def randomInt(minimum, maximum):
	""" Returns a random integer between or equald to minimum and maximum
	"""
	if minimum < 0: minimum = 0
	if maximum < 0: maximum = 100
	return random.randint(minimum, maximum)

#------------------------------------------------------------------------
def color(string, color=None, bold=None):
    """
    Author: HarmJ0y, borrowed from Empire
    Change text color for the Linux terminal.
    """
    
    attr = []
    
    if color:
    	if bold:
    		attr.append('1')
        if color.lower() == "red":
            attr.append('31')
        elif color.lower() == "green":
            attr.append('32')
        elif color.lower() == "blue":
            attr.append('34')

        return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)
    else:
		if string.strip().startswith("[!]"):
			attr.append('1')
			attr.append('31')
			return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)
		elif string.strip().startswith("[+]"):
			attr.append('1')
			attr.append('32')
			return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)
		elif string.strip().startswith("[?]"):
			attr.append('1')
			attr.append('33')
			return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)
		elif string.strip().startswith("[*]"):
			attr.append('1')
			attr.append('34')
			return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)
		else:
			return string

#------------------------------------------------------------------------
def printBanner():
	print color("""
	
██╗    ██╗███████╗██████╗ ██████╗  █████╗ ██╗   ██╗ ██████╗██████╗ 
██║    ██║██╔════╝██╔══██╗██╔══██╗██╔══██╗██║   ██║██╔════╝╚════██╗
██║ █╗ ██║█████╗  ██████╔╝██║  ██║███████║██║   ██║██║      █████╔╝
██║███╗██║██╔══╝  ██╔══██╗██║  ██║██╔══██║╚██╗ ██╔╝██║     ██╔═══╝ 
╚███╔███╔╝███████╗██████╔╝██████╔╝██║  ██║ ╚████╔╝ ╚██████╗███████╗
 ╚══╝╚══╝ ╚══════╝╚═════╝ ╚═════╝ ╚═╝  ╚═╝  ╚═══╝   ╚═════╝╚══════╝
	
	""", "blue")

