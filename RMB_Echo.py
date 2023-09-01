import nationstates
import time
import discord
import re

#Setup
user = input("Enter User Name (Main Nation): ")
api = nationstates.Nationstates(user + "Running RMB Echo by DragoE")
targ_regions = (input("Enter Regions to Watch, Seperated by Commas (EX: Conch Kingdom,Lands End): ")).lower().strip().replace(" ","_").split(",")
previous_messages = []
for element in targ_regions:
    previous_messages.append([])
requested_sleep = int(input("Enter the number of seconds between checks (minimum 100):"))
if requested_sleep < 100:
    real_sleep = 100
else:
    real_sleep = requested_sleep
url = input("Enter your Webhook URL: ")
webhook = discord.SyncWebhook.from_url(url)

#Loop Section
while True:
    i = 0
    #Iterate over every region provided in targ_regions
    for current_region in targ_regions:
        #Call to the API, retreive messages
        api_region = api.region(current_region)
        api_messages = (api_region.messages)["post"]
        print(previous_messages)
        for post in api_messages:
            #Check that the post is new
            print(i)
            if post["id"] not in previous_messages[i]:
                #Make it pretty
                pretty_message = re.sub(r"\[quote=.*;\d*\]", "\n> ",post["message"])
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
                webhook.send("# {} in {} said:\n{}".format(pretty_name_nation,pretty_name_region,final_msg))
                previous_messages[i].append(post["id"])
            #Garbage collection to prevent previous messages from getting unecessarily big
            if len(previous_messages[i]) > 15:
                previous_messages[i].pop(0)
        i += 1
    print("RMB Search Complete, waiting {} secconds".format(real_sleep))
    time.sleep(real_sleep)    
