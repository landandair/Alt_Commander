# Alt_Commander
Game/interface for Operating smarter bots for R/Place in a semi or fully-autonomous manner.

**Install Instructions:**
- **Installing and Starting a Standard Client**
1. Download python https://www.python.org/downloads/
2. Run the executable installer for your os
   1. Follow the prompt some of the key buttons are below
      1. select- Install launcher for all users
      2. select- Add python.exe to PATH
      3. click- Install Now
      4. click- pip
      5. click- py launcher and for all users
      6. click- next
3. Download the project files from github and unzip to the desired location
4. Open command line(command prompt) and type 'python --version' or try 'py --version'
   1. You should see your python version u downloaded 
   2. if not look up how to change your default version
5. While in terminal/console/command prompt, 
   1. Navigate to the area (unix: cd /path/to/Alt_Commander)
   2. (python3 -m[if needed]) pip install -r /path/to/Alt_Commander/requirements.txt
   3. All required libraries should be installed
6. Finally, ensure that you have Google Chrome installed (sorry, but other browsers won't work as they dont put elements in same spot)
   1. If you run into any problems with the Selenium driver please make sure chrome is up to date
7. Create an Account_Info.txt file that has all the account info for the accounts you plan to use following the example
   1. Format is 'Account_Username Password' use a hashtag at the beginning of a line to stop using that account
8. Get the server data from the person running the server
   1. Insert Server_data.txt into the /Alt_Manager directory
9. Open up 'IDLE' and use file > open the desired script to run
   1. for people running bots open up Alt_Manager/start_alts.py
   2. click the run button to run the script
   3. If this doesnt work try using command prompt
   4. if you get Alert: Running in local mode cannot join a server please change if undesired
      1. Look at the open 'start_alts.py' script and change local=True to local=False
- **Starting a Server**
1. Follow instructions for the client
   1. (minus getting the server data and running it)
2. Open up /Server/make_server_data.py and run it and follow the prompts or skip them to use the defaults
3. Look at the generated server data file and make sure it looks correct
4. Open up the IDLE and run the server
   1. It should run without error
   2. Unfortunately this is not enough
5. If zou wish for the server to be public to the internet(you do)
   1. Look up 'set up port forwarding on (your isp)'
   2. Follow the instructions they give
      1. Set up a port forward for the port in Server_data.txt
6. Once you finish check your work
   1. https://www.portchecktool.com and type in port
   2. Check ip to ensure it looks good(or proxy if you used a proxy instead of your public ip)
   3. Make sure it says "Success!"
   4. Congrats you have made a hole in your firewall
      1. (Consider turning this off after the event is done)
7. Now share your Server_data.txt to the people who are joining
   1. (maybe in a private channel with just the people who need it as it contains your encryption key for the server, your public ip, and the port you used)
8. Modify the start server script to meet your needs
   1. Add desired template to /Server/Templates
      1. Needs to be a 1:1 png with the exact colors and a color not in the pallet for ignored areas of the square area
   2. Open the script modify the following
   3. corner_pos = (100, 100) 
      1. Where you want the top left corner of the image to go
   4. file_name = 'Templates/daniil.png'
      1. Path to the image file
9. Now congrats you should be able to have people join your hosted server as clients
   1. They can join as either bots or managers
   2. To run clients on the machine running the server ensure that the local variable is set to True as described above
- **Installing and Starting a Command Client**
1. Not Complete yet
2. Follow the instructions to start a standard client
3. Select if its in local mode or not
   1. Open script and modify to local=True or local=False
4. Run 'start_cmd_client.py', it should connect to the server and open the interface
5. Controls are below

**Detailed Instructions of How the Bots Behave and Can Be Controlled**

(TBD Once Cmd client is done)