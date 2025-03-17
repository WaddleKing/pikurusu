from dotenv import load_dotenv
import discord
import os
import re
import random
import subprocess
import ollama
import base64
from openai import OpenAI
from discord.utils import find
from datetime import datetime, timezone, timedelta
from discord.ext import commands

client_ai = OpenAI(api_key="lm-studio", base_url="http://127.0.0.1:1234/v1")

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

channels = [782032130837970954,1071911710664953928,1081217657199673426,1071519598781927438]
channels_not = [748230154819600434,782032135863009320,688065197881163799,689561034842832978,1272196983804919900]
banned = []

emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)

client = commands.Bot(command_prefix=".",intents=intents)

model = "hf.co/leafspark/Llama-3.2-11B-Vision-Instruct-GGUF:Q4_K_M"
model = "hf.co/bartowski/MN-12B-Celeste-V1.9-GGUF:Q4_0"
model = "hf.co/bartowski/NemoMix-Unleashed-12B-GGUF:Q4_K_M"
model = "hf.co/TheBloke/Llama-2-13B-chat-GGUF:Q4_0"
model = "hf.co/Orenguteng/Llama-3-8B-LexiFun-Uncensored-V1-GGUF:Q8_0"
model = "hf.co/bartowski/gemma-2-9b-it-abliterated-GGUF:Q5_K_M"
model = "hf.co/mlabonne/Meta-Llama-3.1-8B-Instruct-abliterated-GGUF:Q8_0"
model = "hf.co/TheDrummer/UnslopNemo-12B-v2-GGUF:Q4_K_M"
model = "hf.co/NousResearch/Hermes-3-Llama-3.1-8B-GGUF:Q8_0"

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    subprocess.Popen(["ollama", "serve"])
    subprocess.Popen(["ollama", "pull", model])
    await client.tree.sync()

@client.event
async def on_guild_join(guild):
    general = find(lambda x: x.name == 'general',  guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send('hi {} its me'.format(guild.name))

@client.event
async def on_message(message):
    if message.author == client.user or message.author in banned or message.content == "<>":
        return

    if message.content.startswith("~"):
        id = message.content[1:message.content[1:].find("~")+1]
        text = message.content[message.content[1:].find("~")+2:]
        channel = client.get_channel(int(id))
        await channel.send(text)
    
    #filters and stuff
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

    #to do it or not
    if message.channel.id in channels_not and client.user not in message.mentions:
        return
    
    if message.channel.id not in channels and client.user not in message.mentions and not isinstance(message.channel,discord.DMChannel):
        r = random.randint(0,100)
        if (r > 50 and message.content.find("Pikurusu") != -1) or (r > 5 and message.content[-1] == "?" and message.content.find("Pikurusu") == -1) or (r > 2 and message.content[-1] != "?" and message.content.find("Pikurusu") == -1):
            if r > 98:
                emoji = client.emojis[random.randint(0,len(client.emojis)-1)]
                await message.add_reaction(emoji)
            return
        
    #actually do the message
    async with message.channel.typing():
        history = [msg async for msg in message.channel.history(limit=30)]
        history = list(filter(filter_history, history[0:3]))+list(filter(filter_timed, history[3:]))
        history.reverse()
        # hist = "\n".join(reversed([f"{msg.author}: {msg.content}" for msg in hist]))

        # if history.rfind('waddleking: <>') != -1:
        #     history = history[history.rfind('<>')+3:]
        wipe = 0
        for i in range(len(history)):
            if history[i].content.find("<>") != -1 or history[i].content.find("A second queen to E4") != -1:
                wipe = i+1

        history = history[wipe:]
        

        # history = history.replace("Pikurusu#3390","Pikurusu")
        # history = history.replace("<@1080964142841724928>","@Pikurusu")

        # history = history.split("\n")
        messages=[
            {"role": "system", "content": open("prompt.txt", "r").read()+"\nHere is some additional information. You do NOT have to use it:\n"+open("information.txt", "r").read()+"\n"+open("example.txt", "r").read()},
            # {"role": "assistant", "content": "kys my man"}
        ]
        # for i in history:
        #     if i.content.startswith("Pikurusu"):
        #         messages.append({"role": "assistant", "content": i.content[10:]})
        #     else:
        #         if len(i.attachments) > 0:
        #             if i.attachments[0].content_type.startswith("image"):
        #                 messages.append({"role": "user", "content": i.content, "images": await i.attachments[0].read()})
        #         else:
        #             messages.append({"role": "user", "content": i.content})

        for i in history:
            if i.author == client.user:
                messages.append({"role": "assistant", "content": i.content})
            else:
                messages.append({"role": "user", "content": str(i.author)+": "+i.content})

        for i in messages:
            print(i["role"], i["content"])

        print(f"{message.author}: {message.content}")
        response = ollama.chat(
            model=model,  # Replace with the name of your loaded model
            messages=messages,
            options={
                "temperature": 0.7
            },
        )['message']['content']

        reply = emoji_pattern.sub(r'', response).lower()[:2000]
        while reply.find('*') != -1: reply = reply[:reply.find('*')]+reply[reply[reply.find('*')+1:].find('*')+len(reply[:reply.find('*')+1])+2:]
    
        reply = re.sub(' +', ' ', reply)
        reply = re.sub(r'\n\s*\n', '\n\n', reply)
        reply = reply.replace("Pikurusu:", "").replace("pikurusu:", "")
    await message.reply(reply, mention_author=False)

        # bot_msg = await message.reply("...", mention_author=False)
        # stream = ollama.chat(
        #     model=model,
        #     messages=messages,
        #     stream=True,
        # )
        # response = ""
        # for chunk in stream:
        #     response += chunk['message']['content']
        #     await bot_msg.edit(content=response)

        



@client.tree.command(name="funfact",description="fun fact!")
async def slash_command(interaction:discord.Interaction):
    await interaction.response.defer()
    response = ollama.chat(
            model=model, # this field is currently unused
            messages=[
                {"role": "system", "content": f"Generate one short singular fun fact which is not true. Do not tell the user it is not true. Only return the fact in a singular sentence."}
            ],
            options={
                "temperature": 1
            },
            )['message']['content']
    await interaction.followup.send(response)

client.run(os.getenv('TOKEN'))
