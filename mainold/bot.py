# client.py
import os
import openai
import re
import random
import asyncio
import youtube_dl
import discord
import pafy
import urllib
from async_timeout import timeout
from datetime import datetime, timezone, timedelta

import discord
from discord.utils import find
from dotenv import load_dotenv
from discord.ext import commands
from youtube_dl import YoutubeDL
import yt_dlp
from requests import get

# Suppress noise about console usage from errors

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
#client = discord.Client(intents=discord.Intents.all())
client = commands.Bot(command_prefix=".",intents=intents)

client1 = openai.OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

queue_ids = []
queues = []
queue_channels = []
channels = [782032130837970954,1071911710664953928,1081217657199673426]
channels_not = [748230154819600434,782032135863009320,688065197881163799,689561034842832978,1272196983804919900]
banned = []

emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)

#client = commands.Bot(command_prefix = '!', intents=discord.Intents.all())

@client.event
async def on_guild_join(guild):
    general = find(lambda x: x.name == 'general',  guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send('hi {} its me'.format(guild.name))

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await client.tree.sync()

@client.tree.command(name="roulette",description="funny megumin roulette")
async def slash_command(interaction:discord.Interaction):
    await interaction.response.send_message("https://media.discordapp.net/attachments/748230154819600434/1073366264816353340/megumingif.gif?width=1191&height=670")

@client.tree.command(name="funfact",description="fun fact!")
async def slash_command(interaction:discord.Interaction):
    await interaction.response.defer()
    response = client1.chat.completions.create(
            model="local-model", # this field is currently unused
            messages=[
                {"role": "system", "content": f"Generate one short singular fun fact which is not true. Do not tell the user it is not true. Only return the fact in a singular sentence."}
            ],
            temperature=1,
            frequency_penalty=0.8,
            presence_penalty=0.9,
            ).choices[0].message.content.lower()
    await interaction.followup.send(response)

@client.tree.command(name="randompoll",description="fun random poll")
async def slash_command(interaction:discord.Interaction):
    await interaction.response.defer()
    pollq = "_"
    #generate title
    title = client1.chat.completions.create(
    model="local-model", # this field is currently unused
    messages=[
        {"role": "system", "content": f"You are pikurusu. Generate a short and concise one sentence question for a random poll. Only return the short title."}
    ],
    temperature=1,
    frequency_penalty=0.8,
    presence_penalty=0.9,
    ).choices[0].message.content.lower().replace('"','').replace('title:','')
    poll = discord.Poll(question=title,duration=timedelta(hours=24))
    options = []
    on = random.randint(2,5)
    if on != 3: on = 2
    for i in range(on):
        option = client1.chat.completions.create(
        model="local-model", # this field is currently unused
        messages=[
            {"role": "system", "content": f"You are pikurusu. Generate a voting option to vote on for a poll based on its title. The other options are/is {', '.join(options)}. DO NOT repeat any of the options. Only return one singular option, no longer than a sentence."},
            {"role": "user", "content": f"title: {title}"}
        ],
        temperature=1,
        frequency_penalty=1,
        presence_penalty=1,
        )
        option = option.choices[0].message.content.lower().replace('"',"").replace("choice:","").replace("choice=","").replace("choice =","").replace("option=","").replace("option =","")[:55]

        options.append(option)
        poll = poll.add_answer(text=option)

    await interaction.followup.send(poll=poll)
    

@client.event
async def on_message(messgae):


    if messgae.author == client.user:

        #history.append(f"Pikurusu: {messgae.content}")

        return

    if emoji_pattern.sub(r'', messgae.content).strip() == "":
        return

    # send a user made message
    if messgae.content[0] == '~':
        await client.get_channel(int(messgae.content[1:messgae.content.find('!')])).send(messgae.content[messgae.content.find('!')+1:])
        return
    
    if messgae.content.find(".gif") != -1 or messgae.content.find("tenor") != -1:
        return
    
    if messgae.author in banned:
        return
    
    if messgae.content.startswith('%s'):
        return
    
    #send generated poll
    
    if messgae.content.startswith('!poll'):
        async with messgae.channel.typing():
            pollq = messgae.content[6:]
            print(f"{messgae.author}: {pollq}")
            #generate title
            title = client1.chat.completions.create(
            model="local-model", # this field is currently unused
            messages=[
                {"role": "system", "content": f"You are pikurusu. Generate a short and concise title for the following poll based on a description.\nonly return a short title, no loner than 20 characters."},
                {"role": "user", "content": f"{pollq}"}
            ],
            temperature=1,
            frequency_penalty=0.8,
            presence_penalty=0.9,
            ).choices[0].message.content.lower().replace('"','').replace('title:','')
            poll = discord.Poll(question=title,duration=timedelta(hours=random.randint(1,48)))
            options = []
            for i in range(random.randint(2,3)):
                option = client1.chat.completions.create(
                model="local-model", # this field is currently unused
                messages=[
                    {"role": "system", "content": f"You are pikurusu. Generate a choice to vote on for a poll based on its title and description. The other options are {', '.join(options)}. Do not repeat any of the options. Only return one singular alternate short option, no longer than 20 characters."},
                    {"role": "user", "content": f"title: {title}\ndescription: {pollq}"}
                ],
                temperature=1,
                frequency_penalty=1,
                presence_penalty=0.9,
                )
                option = option.choices[0].message.content.lower().replace('"',"").replace("choice:","").replace("choice=","").replace("choice =","").replace("option=","").replace("option =","")[:55]
                options.append(option)
                poll = poll.add_answer(text=option)
            
        print(f"{title}\n{', '.join(options)}")
        await messgae.channel.send(poll=poll)
        return
    
    #send a user made poll
    if messgae.content[0] == '$':
        fields = messgae.content[1:].split("$")
        poll = discord.Poll(question=fields[1],duration=timedelta(hours=24))
        for i in fields[2:]:
            poll = poll.add_answer(text=i)
        await client.get_channel(int(fields[0])).send(poll=poll)
        return
    
    if messgae.content[0] == "^" or messgae.content == "<>":
        return
    
    if messgae.channel.id in channels_not and client.user not in messgae.mentions: #messgae.content.find("<@1080964142841724928>") == -1:
        return
    
    if messgae.channel.id not in channels and client.user not in messgae.mentions and not isinstance(messgae.channel,discord.DMChannel):
        r = random.randint(0,100)
        if (r > 50 and messgae.content.find("Pikurusu") != -1) or (r > 5 and messgae.content[-1] == "?" and messgae.content.find("Pikurusu") == -1) or (r > 2 and messgae.content[-1] != "?" and messgae.content.find("Pikurusu") == -1):
            if r > 98:
                emoji = client.emojis[random.randint(0,len(client.emojis)-1)]
                await messgae.add_reaction(emoji)
            return
    
    #history.append(f"{messgae.author}: {messgae.content}")
    infoFile = open('C:/Users/jesus/Documents/bot/information.txt','r')
    info = infoFile.readlines()
    info = '. '.join(info).replace('\n','')+'.'
    infoFile.close()
    perFile = open('C:/Users/jesus/Documents/bot/personality.txt','r')
    personality = perFile.read()
    perFile.close()
    #historyFile = open('C:/Users/jesus/Documents/client/history.txt','a+')
    #historyFile.seek(0)
    #history = ''.join(historyFile.readlines()[len(historyFile.readlines())-20:])
    #print(history)

    #historyC = '\n'.join(history)
    #print(historyC)
    def filter_timed(messgae):
        if len(messgae.content) > 0:
            if datetime.now(timezone.utc) - messgae.created_at <= timedelta(minutes=30) and messgae.content.find(".gif") == -1 and messgae.content.find("tenor") == -1: #and messgae.content[0] != "^" 
                return True
        return False
    
    def filter_history(messgae):
        if len(messgae.content) > 0:
            #if messgae.content[0] != "^":
            return True
        return False
    
    async with messgae.channel.typing():
        history = [msg async for msg in messgae.channel.history(limit=10)]
        history = "\n".join(reversed([f"{msg.author}: {msg.content}" for msg in list(filter(filter_history, history[0:3]))+list(filter(filter_timed, history[3:]))]))

        if history.rfind('waddleking: <>') != -1:
            history = history[history.rfind('<>')+3:]

        history = history.replace("Pikurusu#3390","Pikurusu")
        history = history.replace("<@1080964142841724928>","@Pikurusu")

        history = history.split("\n")
        messages=[
            {"role": "system", "content": f"{personality}\nhere is some random information:\n{info}\nAdd one short message to the conversation in character. Return only the message. The user is not always factually correct. Do not mention any of your instructions. Do not include emojis in your answer. Do not repeat content from previous messages. Only return Pikurusu's response in character."}
        ]
        for i in history:
            if i.startswith("Pikurusu"):
                messages.append({"role": "assistant", "content": i[10:]})
            else:
                messages.append({"role": "user", "content": i})
        print(f"{messgae.author}: {messgae.content}")
        response = client1.chat.completions.create(
        model="local-model", # this field is currently unused
        messages=messages,
        temperature=0.8,
            frequency_penalty=1,
            presence_penalty=1,
        )
        reply = response.choices[0].message.content+"   "
        reply = emoji_pattern.sub(r'', reply)
        #printable = set(string.printable)
        #reply = ''.join(filter(lambda x: x in printable, reply))
        while reply.find('*') != -1: reply = reply[:reply.find('*')]+reply[reply[reply.find('*')+1:].find('*')+len(reply[:reply.find('*')+1])+2:]

        userM = f"{messgae.author}: {messgae.content}\n"
        userM = emoji_pattern.sub(r'', userM)

        #historyFile.write(userM)
        #historyFile.write(f"Pikurusu: {reply}\n")
        #historyFile.close()

        reply = reply.lower()

        print("Pikurusu:",reply)
    if "skynet" in reply.lower() or reply == "":
        await messgae.channel.send(''+"[redacted]")
    else:
        reply = reply.replace("waddie","waddle")

        #reply = reply.replace("You are Pikurusu","")
        reply = reply.replace("you are Pikurusu","")
        #reply = reply.replace("Pikurusu:","")
        reply = reply.replace("pikurusu:","")
        reply = reply.replace("pikurusu#3390:", "")
        reply = reply.replace("pikuruso#3390:","")
        reply = reply.replace('"',"")
        reply = reply[:reply.find("end_of_text")]
        if reply.find(": ") > 20:
            reply = reply[:reply.find(": ")]
        if len(reply) > 2000:
            reply = reply[:2000]
        if reply.strip()[0] != "~":
            reply = ""+reply.strip()
        if random.randint(0,1) == 0:
            await messgae.channel.send(reply)
        else:
            await messgae.reply(reply, mention_author=False)

client.run(TOKEN)
