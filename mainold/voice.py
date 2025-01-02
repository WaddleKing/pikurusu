import discord
import os
import wave
import asyncio
import azure.cognitiveservices.speech as speechsdk
import numpy as np
import re
from pydub import AudioSegment
from audiostretchy.stretch import stretch_audio
from gtts import gTTS
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get

bot = commands.Bot(command_prefix='%', intents=discord.Intents.all())

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
speech_key = os.getenv('speech_key')
@bot.command()
async def join(ctx):
    voice_channel = ctx.author.voice.channel
    try:
        await voice_channel.connect() 
    except:
        pass
    await ctx.message.delete()
    

@bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()
    await ctx.message.delete()

@bot.command()
async def s(ctx):
    if ctx.author.id != 753730641996152862:
        return
    print(str(ctx.message.content))
    
# Creates an instance of a speech config with specified subscription key and service region.

    text = str(ctx.message.content).replace("%s ", "")
    print(text)
    
    file_name = "C:/Users/jesus/Documents/bot/tts/"+text.replace("?", "").replace("!", "").replace(":", "")+".wav"

    if os.path.isfile(file_name):
        pass
    else:
        service_region = "northeurope"
        file_config = speechsdk.audio.AudioOutputConfig(filename=file_name)

        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        # Note: the voice setting will not overwrite the voice element in input SSML.
        speech_config.speech_synthesis_voice_name = "en-US-LunaNeural"

        # use the default speaker as audio output.
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=file_config)

        result = speech_synthesizer.speak_text_async(text).get()
        # Check result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}], and the audio was saved to [{}]".format(text, file_name))
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))

        semitone_change = 2.925

        audio = AudioSegment.from_wav(file_name)
        new_sample_rate = int(audio.frame_rate * (2.0 ** (semitone_change / 12.0)))
        pitched_audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate})
        pitched_audio = pitched_audio.set_frame_rate(audio.frame_rate)
        pitched_audio.export(file_name, format="wav")
    
    #stretch_audio("C:/Users/jesus/Documents/bot/tts/output.wav", "C:/Users/jesus/Documents/bot/tts/output.wav", ratio=0.9)

    # grab the user who sent the command
    voice_channel = ctx.author.voice.channel
    
    # only play music if user is in a voice channel
    if voice_channel!= None:
        # create StreamPlayer
        try:
            vc = await voice_channel.connect() 
        except:
            vc = get(bot.voice_clients, guild=ctx.guild)
        vc.play(discord.FFmpegPCMAudio(file_name))
    await ctx.message.delete()
    

@bot.event
async def on_ready():
    print('Logged in as: {0.user.name}'.format(bot))

bot.run(TOKEN)