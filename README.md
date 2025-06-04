# RMB_Echo
A script which creates an RMB Feed in your discord using Webhooks
## Requirements
This script utilises two librairies which must be installed prior to use
- sans (pip install sans)
- discord.py (pip install discord.py)

**Older Versions Requirements Notice**
RMB_Echo was migrated to using sans as a wrapper in V3, V2s and earlier builds used pynationstates (pip install nationstates) instead.

In addition, you must setup a webhook in your server as described here (https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) and provide the script with the url at setup.
## Use
To use, edit the config.toml file in a text editor such as notepad with your settings and save it. Then, run the RMB_Echo.py file. The program must remain open and running for the feed to remain connected.

Refresh speed setting is now deprectaed and no longer appears in the config for V3+, instead the script responds as soon as it is informed of RMB activity by Server-Sent Events (assuming it can within rate-limit).

This script should never overrun the API when used on it's own. Use of this script simultaniously with other API calling scripts does expose you to the risk of one script making too many requests and locking the other one out. Doing this is not officially endorsed or supported behavhiour, and is done at your own risk.
## To-Do
- Nothing
