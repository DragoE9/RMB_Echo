import sans
from time import sleep
import discord
import re
import tomli
import tkinter
import threading
from datetime import datetime
import sys
import xml.etree.ElementTree as ET

#I need to use this later
def escape_me(string):
    result_str = string.replace("?",r"\?")
    result_str = result_str.replace("*",r"\*")
    result_str = result_str.replace("(",r"\(")
    result_str = result_str.replace(")",r"\)")
    return result_str

#Import settings from config
with open ("config.toml","rb") as config_file:
    settings = tomli.load(config_file)
#Setup
user = settings["user_agent"]
sans.set_agent(user + " Running RMB Echo V3.0.0 by DragoE")
targ_regions = [x.lower().replace(" ","_") for x in settings["regions"]]
url = settings["webhooks"]
if settings["mode"] == "single":
    webhook = discord.SyncWebhook.from_url(url[0])
    print("Setup Complete")
elif settings["mode"] == "multi":
    if len(targ_regions) == len(url):
        print("Setup Complete")
    else:
        print("Error: Detected Mismatch Between Webhooks and Regions")
        quit()
else:
    print("Error: Unkown Mode")
    quit()
    
if len(settings["colours"]) == len(targ_regions):
    palette = settings["colours"]
else:
    print("Couldn't Load Colours. Using Defaults")
    rainbow = [0xff0000,0xff7500,0xffea00,0x00ff00,0x00fffa,0x0000ff,0xff00ff]
    palette = [rainbow[i % len(rainbow)] for i in range(len(targ_regions))]
    
print("RMB Echo V3.0.0 Online")

class RMB_Echo:
    def __init__(self, p_window):
        #window setup
        self.window = p_window
        self.window.title("RMB Echo V3.0.0")
        self.start_button = tkinter.Button(p_window, text="Start", command=self.start_program, width=20, height=5)
        self.start_button.pack()
        self.stop_button = tkinter.Button(p_window, text="Exit", command=self.stop_program, width=20, height=5)
        self.stop_button.pack()
        self.is_running = False
    
    def start_program(self):
        if self.is_running == False:
            self.is_running = True
            #run the loop in a new thread so the window doesn't hang
            self.sse_thread = threading.Thread(target=self.the_function,daemon=True)
            self.sse_thread.start()
        else:
            print("Search is already running")

    def stop_program(self):
        print("Initiating Stop")
        #Killing a thread in python is nearly impossible apparently, and I don't wanna deal with it. So this button now just kills everything
        #Thread will end bc it's daemon
        sys.exit(0)

    def the_function(self):
        #Loop Section
        global webhook
        for event in sans.serversent_events(sans.Client(),"rmb").view(regions=targ_regions):
            #Upon Receiving an RMB Message Event from SSE
            #Identify the region
            #This should hopefully never overspeed the rate-limit if used on its own. If used with other scripts... hopefully sans' internal rate-limiting catches it
            region = re.search(r"%%(.*)%%",event["str"]).group(1)
            i = targ_regions.index(region)
            #Get the text of the message
            try:
                response = sans.get(sans.Region(region,"messages",limit=1)).xml
                print(ET.tostring(response, encoding='unicode'))
                #Note to self. .// required if you wanna search the entire tree
                pretty_message = response.find(".//MESSAGE").text
                sleep(0.6)
                #Make it pretty
                pretty_message = pretty_message.replace("[i]","*")
                pretty_message = pretty_message.replace("[/i]","*")
                pretty_message = pretty_message.replace("[b]","**")
                pretty_message = pretty_message.replace("[/b]","**")
                pretty_message = pretty_message.replace("[u]","__")
                pretty_message = pretty_message.replace("[/u]","__")
                links = re.findall(r'(?<=\[url=)(.*?)(?=\])', pretty_message)
                for entry in links:
                    if entry[:7] == "http://" or entry[:8] == "https://":
                        fixed_link = entry
                    elif entry[:5] == "page=":
                        fixed_link = "https://www.nationstates.net/" + entry
                    else:
                        fixed_link = "http://" + entry
                    regex_string = r"(?<=\[url=" + r'{}'.format(escape_me(entry)) + r"\])((.|\n)*?)(?=\[/url\])"
                    link_text = (re.search(r'{}'.format(regex_string),pretty_message))
                    insertion_string = "[{}]({})".format(link_text.group(),fixed_link)
                    pretty_message = re.sub(r"\[url=.*?\](.|\n)*?\[/url]",insertion_string,pretty_message,count=1)
                nations = re.findall(r'(?<=\[nation\])(.*?)(?=\[\/nation\])',pretty_message)
                for entry in nations:
                    name = entry.lower().replace(" ","_")
                    fixed_link = "http://nationstates.net/nation=" + name
                    insertion_string = "[{}]({})".format(entry,fixed_link)
                    pretty_message = re.sub(r'\[nation\].*?\[\/nation\]',insertion_string,pretty_message,count=1)
                regions = re.findall(r'(?<=\[region\])(.*?)(?=\[\/region\])',pretty_message)
                for entry in regions:
                    name = entry.lower().replace(" ","_")
                    fixed_link = "http://nationstates.net/region=" + name
                    insertion_string = "[{}]({})".format(entry,fixed_link)
                    pretty_message = re.sub(r'\[region\].*?\[\/region\]',insertion_string,pretty_message,count=1)
                quotes = re.findall(r'\[quote=.*;\d*\]([\S\s]*?)\[\/quote\]', pretty_message)
                for entry in quotes:
                    better_quote = "\n> " + entry.replace("\n", "\n> ") + "\n"
                    pretty_message = re.sub(r'\[quote=.*;\d*\][\S\s]*?\[\/quote\]',better_quote,pretty_message,count=1)
                spoilers = re.findall(r'(?<=\[spoiler=)(.*?)(?=])',pretty_message)
                for entry in spoilers:
                    regex_string = r"(?<=\[spoiler=" + r'{}'.format(escape_me(entry)) + r"\])((.|\n)*?)(?=\[/spoiler\])"
                    spoiled_message = re.search(r"{}".format(regex_string),pretty_message)
                    insertion_string = "(Spoiler: " + entry + ") ||" + spoiled_message.group() + "||"
                    pretty_message = re.sub(r"\[spoiler=.*?\](.|\n)*?\[/spoiler]",insertion_string,pretty_message,count=1)
                pretty_message = pretty_message.replace("[strike]","~~")
                pretty_message = pretty_message.replace("[/strike]","~~")
                pretty_message = pretty_message.replace("[list]","")
                pretty_message = pretty_message.replace("[/list]","")
                pretty_message = pretty_message.replace("[*]","- ")
                pretty_name_nation = response.find(".//NATION").text.replace("_"," ").title()
                pretty_name_region = region.replace("_"," ").title()
                if len(pretty_message) > 1900:
                    final_msg = pretty_message[:1900] + "[...]"
                else:
                    final_msg = pretty_message
                #Make an Embed
                embed = discord.Embed(title="Message in {}".format(pretty_name_region),description=final_msg,color=discord.Color(palette[i]))
                embed.set_author(name=pretty_name_nation)
                #Send it off to the Webhook
                if settings["mode"] == "single":
                    webhook.send(embed=embed)
                else:
                    webhook = discord.SyncWebhook.from_url(url[i])
                    webhook.send(embed=embed)
                now = datetime.now().strftime("%H:%M:%S")
                print("[{}] Made a post for {}".format(now, region))
            except Exception as e:
                #Lazy Error Handling
                print("An Error Occured while trying to fetch or send the post")
                print(e)

#Do the thing
console = tkinter.Tk()
console.minsize(200,200)
Echo = RMB_Echo(console)
console.mainloop()