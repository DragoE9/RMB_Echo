import nationstates
import time
import discord
import re
import tomli

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

#Loop Section
while True:
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
                pretty_message = re.sub(r"\[quote=.*;\d*\]", "\n> ",pretty_message)
                pretty_message = pretty_message.replace("[/quote]","\n")
                pretty_message = pretty_message.replace("[i]","*")
                pretty_message = pretty_message.replace("[/i]","*")
                pretty_message = pretty_message.replace("[b]","**")
                pretty_message = pretty_message.replace("[/b]","**")
                pretty_message = pretty_message.replace("[u]","__")
                pretty_message = pretty_message.replace("[/u]","__")
                pretty_name_nation = post["nation"].replace("_"," ").capitalize()
                pretty_name_region = current_region.replace("_"," ").capitalize()
                if len(pretty_message) > 1900:
                    final_msg = pretty_message[:1900] + "[...]"
                else:
                    final_msg = pretty_message
                #Send it off to the Webhook
                if settings["mode"] == "single":
                    webhook.send("# {} in {} said:\n{}".format(pretty_name_nation,pretty_name_region,final_msg))
                    previous_messages[i].append(post["id"])
                else:
                    webhook = discord.SyncWebhook.from_url(url[i])
                    webhook.send("# {} in {} said:\n{}".format(pretty_name_nation,pretty_name_region,final_msg))
                    previous_messages[i].append(post["id"])
            #Garbage collection to prevent previous messages from getting unecessarily big
            if len(previous_messages[i]) > 15:
                previous_messages[i].pop(0)
        i += 1
    print("RMB Search Complete, waiting {} secconds".format(real_sleep))
    time.sleep(real_sleep)    
