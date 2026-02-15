This python script automatically switchs OBS sources if tracking is lost or retored. 
I use it to switch to a PNG Tuber when tracking is lost and back to a VtubeStudio model when it is back.
Cloning the repo isn't necessary. Just copy the script to your PC.


Step 1: Download and install Python.

  The script was tested with python 3.10. Later version should still work?  
  https://www.python.org/downloads/
  

Step 2: Setup OBS.

  Enable Websockets in OBS.
    In OBS, ensure your WebSocket server is enabled:
    Go to Tools -> WebSocket Server Settings.
    Check Enable WebSocket server.
    Note the Server Port (default is 4455) and copy the Server Password.
    

Step 3: Configure the Script

  Copy the script and save to your PC (example name tracker.py)
  Set your port and password on lines 12 and 13.
    VTSPort = 4455
    VTSPassword = changeme

  On Lines 127-135 add as many source visibily changes that you'd like. I've included an example.
  Note that the first variable is the scene, second variable is the source name, True or false shows or hides the source.

  
Step 4: Library Install Instructions.

  pip install obsws-python
  pip install pyvts


Step 5: Run it!

  Open Command Prompt and use the cd command to navigate to the location you saved your script.  
  run with
  python tracker.py
  
  A popup will appear on Vtube Studio.
  Tab to Vtube Studio and authorize the script.

Your ready to roll, Enjoy.
