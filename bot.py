import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import time
from utils import *
import sqlite3

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

    if message.channel.name == "dev_test_env":
        if message.content.startswith(f'$help'):
            await message.channel.send(f"Hello {str(message.author).split('#')[0]}!\nI'm the trivia bot!\nI can generate trivia questions, just message **`$trivia`** to start!!\nYou'll have 10 seconds to answer each question before I reveal the answer")

        # get trivia question
        if message.content.startswith(f'$trivia'):
            result = get_question()
            for k, v in result.items():
                if k == "q":
                    await message.channel.send("\n**"+str(v)+"**")
                elif k == "a":
                    await message.channel.send(">>> {}".format(v))
                elif k == "correctAns":
                    continue
                else:
                    await message.channel.send(str(k)+": *"+str(v)+"*")

            answers={}
            for member in message.channel.members:
                if member.bot:
                    continue
                try:
                    message = await bot.wait_for('message', timeout=15.0, check=lambda m: m.author == member and not m.author.bot)
                    if message.author.bot or message.author.name in answers:
                        continue
                    answers[str(message.author.name)] = message.content
                except:
                    answers[message.author.name] = None
            print(answers)
            await message.channel.send("answer is.... "+result["correctAns"])

            # check user answers and update db to add or remove points
            for usr, ans in answers.items():
                if ans == result["correctAns"]:
                    print("db insert-->",usr, ans, result["correctAns"])
                    add_score(usr, result["point value"])
                else:
                    # if answer is wrong increment game played
                    add_game_data(usr)



        # get current scoreboard
        if message.content == ('$scoreboard'):
            await message.channel.send("------ Scoreboard ------")             
            conn = sqlite3.connect("triviaBot.db")
            c = conn.cursor()
            for row in c.execute("select name, score, cast(numCorr as real)*100/q_played as '% Correct' from scoreboard order by score desc"):
                await message.channel.send('\t'.join(map(str,row)))
            conn.close()

        # initialize db
        if message.content == ('$init'):
            # connect to db
            conn = sqlite3.connect("triviaBot.db")
            print("db connected")
            c = conn.cursor()

            # create initial table
            c.execute("create table if not exists scoreboard (id text primary key,username text not null,name text not null,score integer,q_played integer,numCorr integer,numWrong integer,perCorrect real);")
            
            # get all members in channel
            members = bot.get_all_members()
            
            for member in members:
                # only return message if member not bot role
                if not member.bot:
                    c.execute(f"INSERT INTO scoreboard (id, username, name, score, q_played, numCorr, numWrong, perCorrect) VALUES (?,?,?,?,?,?,)", (str(member.id),str(member),str(member.name),0,0,0))
            conn.commit()
            conn.close()
            await message.channel.send("db initialized")

            
# get bot token from .env and run client
# has to be at the end of the file
bot.run(os.getenv('TOKEN'))