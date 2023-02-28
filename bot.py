import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from utils import *
import sqlite3
import asyncio

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

            # collect trivia answers
            global answers
            i=0
            answers={}
            for i in range(10):
                try:
                    message = await bot.wait_for('message', timeout=1)
                    if message.author.bot or message.author.name in answers:
                        continue
                    # print(f"Submitting message: {message.content}")
                    answers[str(message.author.name)] = message.content.lower()
                except asyncio.TimeoutError:
                    continue

            # await asyncio.sleep(timeout)
            await message.channel.send("Answer ....**"+result["correctAns"]+"**")

            # print(f"submitted answer dictionary: {answers}")

            # check user answers and update db to add or remove points
            for author, ans in answers.items():
                print(author, ans)
                if ans is None:
                    continue
                elif ans.lower() == result["correctAns"].lower():
                    print("add point value")
                    add_score(author, result["point value"])
                else:
                    # if answer is wrong increment game played
                    print("wrong: increment question count")
                    add_game_data(author)


        # get current scoreboard
        if message.content == ('$scoreboard'):          
            await message.channel.send('------ Scoreboard ------\n >>> {}'.format('\n'.join(get_scores())))

        # initialize db
        if message.content == ('$init'):
            # connect to db
            conn = sqlite3.connect("triviaBot.db")
            print("db connected")
            c = conn.cursor()

            # create initial table
            c.execute("create table if not exists scoreboard (id text primary key,username text not null,name text not null,score integer,q_played integer,numCorr integer);")
            
            # get all members in channel
            members = bot.get_all_members()
            
            for member in members:
                # only return message if member not bot role
                if not member.bot:
                    c.execute(f"INSERT INTO scoreboard (id, username, name, score, q_played, numCorr) VALUES (?,?,?,?,?,?)", (str(member.id),str(member),str(member.name),0,0,0))
            conn.commit()
            conn.close()
            await message.channel.send("db initialized")

            
# get bot token from .env and run client
# has to be at the end of the file
bot.run(os.getenv('TOKEN'))