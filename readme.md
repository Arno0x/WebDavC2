WebDAVC2
============
LAST/CURRENT VERSION: 0.1

Author: Arno0x0x - [@Arno0x0x](https://twitter.com/Arno0x0x)

WebDavC2 is a PoC of using the WebDAV protocol with **PROPFIND only requests** to serve as a C2 communication channel between an agent, running on the target system, and a controller acting as the actuel C2 server.

The tool is distributed under the terms of the [GPLv3 licence](http://www.gnu.org/copyleft/gpl.html).

Background information
----------------

Check this blog post on how and **why** I came up with the idea of using WebDAV PROPFIND only requests as a C2 channel:

[TBD](https://tbd)

Architecture
----------------

WebDavC2 is composed of:
- a controller, written in Python, which acts as the C2 server
- an agent, written in C#/.Net, running on the target system, delivered to the target system via various initial stagers
- various flavors of initial stagers (*created on the fly when the controller starts*) used for the initial compromission of the target system

Features
----------------

WebDavC2 main features:
  - Various stager (*powershell one liner, batch file, two types of MS-Office macro*) - this is not limited, you can easily come up with your own stagers, check the templates folder to get an idea
  - Pseudo-interactive shell (*with environment persistency*)

<img src="https://dl.dropboxusercontent.com/s/swucv9ixr7baumb/webdav_03.png?dl=0" width="600">

Installation & Configuration
------------

Installation is pretty straight forward:
* Git clone this repository: `git clone https://github.com/Arno0x/WebDAVC2 WebDavC2`
* cd into the WebDavC2 folder: `cd WebDavC2`
* Give the execution rights to the main script: `chmod +x webDavC2.py`

To start the controller, simply type `./webDavC2.py`.

Compiling your own agent
------------

Although it is perfectly OK to use the provided *agent.exe*, you can very easily compile your own executables of the agent, from the source code provided. You don't need Visual Studio installed.

* Copy the `agent/agent.cs` file on a Windows machine with the .Net framework installed
* CD into the source directory
* Use the .Net command line C# compiler:
  - To get the standard agent executable: `C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /out:agent.exe *.cs`
  - To get the debug version: `C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /define:DEBUG /out:agent_debug.exe *.cs`

DISCLAIMER
----------------
This tool is intended to be used in a legal and legitimate way only:
  - either on your own systems as a means of learning, of demonstrating what can be done and how, or testing your defense and detection mechanisms
  - on systems you've been officially and legitimately entitled to perform some security assessments (pentest, security audits)

Quoting Empire's authors:
*There is no way to build offensive tools useful to the legitimate infosec industry while simultaneously preventing malicious actors from abusing them.*

TODO
------------

This tool is just a PoC so don't expect production quality, plus it has some arbitrary limitations in terms of quantity of data that can be transfered from the agent back to the controller.

To be added in the next releases:
- Check if the WebClient service is started, if not start it with the `pushd \\webdavserver & popd` trick.

To be fixed:
- Increase the (*arbitrary*) size limit of command output that can be returned to the controller
- waiting for feedback :)