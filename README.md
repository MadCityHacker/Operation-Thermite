# Operation-Thermite

Thermite is a Python script designed to facilitate a C2 (Command & Control) infrastructure. The core component of Thermite is the server infrastructure, which allows for multiple client connections and supports SSL communication. The client component, codenamed BRIMSTONE, is used to communicate back to the Thermite server, and can be a normal Python script or a compiled executable. For additional information on how to use this program or any others created, please visit https://madcityhacker.com.

# Setup
Thermite was written using Python 3.7. It has been tested on both Windows and Linux operating systems.

Installation
------------
Simply clone the repository and run `pip3 install -r requirements.txt`.

# Usage
The below are switches that can be run with Thermite.

 * -p <PORT> - Required - This option specifies the port to listen on for incoming BRIMSTONE connections
 * -i <IP> - Optional - This option specifies the IP address that the BRIMSTONE agents will connect to. This will be prompted for if not specified.
 * -c - Optional - This option will compile the BRIMSTONE agent using pyinstaller.
 * --usessl - Optional - This option will force the BRIMSTONE to Thermite connection to be encrypted. It will also generate a certificate/private key pair if none are found in the etc/ folder.
 
 Examples
 --------
 **Basic Thermite Usage**
 
 `python3 thermite.py -p 80`
 
 [![Example1.png](https://i.postimg.cc/s2xyp7b6/Example1.png)](https://postimg.cc/Jsf98DrZ)
 
 **Thermite w/ SSL Communcation**
 
 `python3 thermite.py -p 443 --usessl`
 
 [![Example2.png](https://i.postimg.cc/SRFhF5R3/Example2.png)](https://postimg.cc/njk5q3vG)
 
 **Thermite w/ Compiled Client and IP Address via Command Line**
 
 `python3 thermite.py -p 80 -i 192.168.1.6 -c`
 
 [![Example3.png](https://i.postimg.cc/VvqcYRb6/Example3.png)](https://postimg.cc/BPnzp2p9)
 
 BRIMSTONE Agent Interaction
 ---------------------------
 
 From the "BRIMSTONE>" command line within Thermite, a number of commands are supported:
 
  * list - This will list all active BRIMSTONE agent connections and their corresponding ID
  * select <ID> - This will interact with the specified BRIMSTONE agent
  * exit - This exits out of the Thermite program
  
 When interacting with an agent (IE, after running the "select" command), the following BRIMSTONE commands are available:
 
  * quit - This backs out of the agent and returns to the Thermite command line. This does NOT close the agent connection.
  * close/exit - Either of these commands will return to the Thermite command line and CLOSE the agent connection on the endpoint.
  
 Since this is a C2 program, when interacting with an agent, all normal operating system commands are also available to run.
 
 Licensing
 ---------
 This program is licensed under GNU GPL v3. For more information, please reference the LICENSE file that came with this program or visit https://www.gnu.org/licenses/. 
 
 Contact Us
 ----------
 Whether you want to report a bug, send a patch, or give some suggestions on this program, please open an issue on the GitHub page or send an email to madcityhacker@gmail.com.
