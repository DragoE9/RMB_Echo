from os import link
import nationstates
import time
import discord
import re
import tomli
import tkinter
import threading
from datetime import datetime

#Import settings from config
with open ("config.toml","rb") as config_file:
    settings = tomli.load(config_file)
#Setup
user = settings["user_agent"]
api = nationstates.Nationstates(user + "Running RMB Echo by DragoE")
targ_regions = settings["regions"]
previous_messages = []
for element in targ_regions:
    previous_messages.append([])
requested_sleep = settings["refresh_rate"]
if requested_sleep < 100:
    real_sleep = 100
else:
    real_sleep = requested_sleep
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


#First, retreive the messages but don't post
i = 0
for current_region in targ_regions:
    #Call to the API, retreive messages
    api_region = api.region(current_region)
    api_messages = (api_region.messages)["post"]
    for post in api_messages:
        previous_messages[i].append(post["id"])
    i += 1
    
print("RMB Echo V2.1.0 Online")

class RMB_Echo:
    def __init__(self, p_window):
        #window setup
        self.window = p_window
        self.window.title("RMB Echo V2.1.0")
        self.start_button = tkinter.Button(p_window, text="Start", command=self.start_program, width=20, height=5)
        self.start_button.pack()
        self.stop_button = tkinter.Button(p_window, text="Pause", command=self.stop_program, width=20, height=5)
        self.stop_button.pack()
        self.is_running = False
    def start_program(self):
        self.is_running = True
        #run the loop in a new thread so the window doesn't hang
        threading.Thread(target=self.the_function).start()
    def stop_program(self):
        self.is_running = False
    def the_function(self):
        #Loop Section
        global webhook
        while self.is_running:
            i = 0
            #Iterate over every region provided in targ_regions
            for current_region in targ_regions:
                #Call to the API, retreive messages
                api_region = api.region(current_region)
                api_messages = (api_region.messages)["post"]
                for post in api_messages:
                    #Check that the post is new
                    if post["id"] not in previous_messages[i]:
                        #Make it pretty
                        pretty_message = post["message"]
                        links = re.findall(r'(?<=\[url=)(.*?)(?=\])', post["message"])
                        for entry in links:
                            fixed_link = "http://" + entry
                            regex_string = r"(?<=\[url=" + r'{}'.format(entry) + r"\])(.*?)(?=\[/url\])"
                            link_text = (re.search(r'{}'.format(regex_string),pretty_message))
                            insertion_string = "[{}]({})".format(link_text.group(),fixed_link)
                            pretty_message = re.sub(r"\[url=.*?\].*?\[/url]",insertion_string,pretty_message,count=1)
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
                        #pretty_message = re.sub(r"\[quote=.*;\d*\]", "\n> ",pretty_message)
                        #pretty_message = pretty_message.replace("[/quote]","\n")
                        pretty_message = pretty_message.replace("[i]","*")
                        pretty_message = pretty_message.replace("[/i]","*")
                        pretty_message = pretty_message.replace("[b]","**")
                        pretty_message = pretty_message.replace("[/b]","**")
                        pretty_message = pretty_message.replace("[u]","__")
                        pretty_message = pretty_message.replace("[/u]","__")
                        pretty_message = pretty_message.replace("[strike]","~~")
                        pretty_message = pretty_message.replace("[/strike]","~~")
                        pretty_name_nation = post["nation"].replace("_"," ").title()
                        pretty_name_region = current_region.replace("_"," ").title()
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
                            previous_messages[i].append(post["id"])
                        else:
                            webhook = discord.SyncWebhook.from_url(url[i])
                            webhook.send(embed=embed)
                            previous_messages[i].append(post["id"])
                    #Garbage collection to prevent previous messages from getting unecessarily big
                    if len(previous_messages[i]) > 15:
                        previous_messages[i].pop(0)
                i += 1
            now = datetime.now().strftime("%H:%M:%S")
            print("[{}] RMB Search Complete, waiting {} secconds".format(now, real_sleep))
            time.sleep(real_sleep)
        print("Searching Finnished")

#Do the thing
console = tkinter.Tk()
console.minsize(200,200)
Echo = RMB_Echo(console)
console.mainloop()