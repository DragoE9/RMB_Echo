# RMB_Echo
A script which creates an RMB Feed in your discord using Webhooks
## Requirements
This script utilises two librairies which must be installed prior to use
- pynationstates (pip install nationstates)
- discord.py (pip install discord.py)
In addition, you must setup a webhook in your server as described here (https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) and provide the script with the url at setup.
## Use
To use, run the RMB_Echo.py file, and enter the required information into the command line prompts. The program must remain open and running for the feed to continue refreshing. 
Refresh speed is locked at a maximum of once every 100 secconds to prevent the script from being used to creat API spam. Modification of the script to go faster is not endorsed! Unless the region you're using this for is extremley busy, even 100 is probably uncessarily fast.
## To-Do
- Make this read from a config file for easier rebooting
- Add Multi-Channel option for different regions
