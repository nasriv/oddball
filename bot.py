import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import time
from utils import *

# If you are coding the bot on a local machine, use the python-dotenv pakcage to get variables stored in .env file of your project
from dotenv import load_dotenv
load_dotenv()

description = '''An example bot to showcase the discord.ext.commands extension
module.'''

# instantiate discord client
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='$', description=description, intents=intents)

# discord event to check when bot is online
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

# set bot commands
@bot.event
async def on_message(message): 
    # make sure bot doesn't respond to it's own messages to avoid infinite loop
    if message.author == bot.user:
        return  
    
    # lower case message
    message_content = message.content.lower()

    if message.channel.name == "trivia-corner":
        if message.content.startswith(f'$help'):
            await message.channel.send(f"Hello {str(message.author).split('#')[0]}!\nI'm the trivia bot!\nI can generate trivia questions, just message **`$trivia`** to start!!\nYou'll have 10 seconds to answer each question before I reveal the answer")

        if message.content.startswith(f'$trivia'):
            result = get_question()
            for k, v in result.items():
                if k == "q":
                    await message.channel.send("\n**"+str(v)+"**")
                elif k == "a":
                    await message.channel.send(">>> {}".format(v))
                elif k == "ans":
                    continue
                else:
                    await message.channel.send(str(k)+": *"+str(v)+"*")

            time.sleep(2)
            await message.channel.send("answer is.... "+result["ans"])
            
            

# get bot token from .env and run client
# has to be at the end of the file
bot.run(os.getenv('TOKEN'))