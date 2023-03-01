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

    if message.channel.name == "trivia-corner":
        if message.content.startswith(f'$help'):
            #TODO update to include all command calls a user can make
            await message.channel.send(f"Hello {str(message.author).split('#')[0]}!\nI'm the trivia bot!\nI can generate trivia questions, just message **`$trivia`** to start!!\nYou'll have 10 seconds to answer each question before I reveal the answer")

        # get trivia question
        if message.content == ('$trivia'):
            
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
            for i in range(20):
                try:
                    message = await bot.wait_for('message', timeout=1)
                    if message.author.bot or message.author.name in answers:
                        continue
                    if message.content != '$trivia':
                    # print(f"Submitting message: {message.content}")
                        answers[str(message.author.name)] = message.content.lower()
                    else:
                        continue
                except asyncio.TimeoutError:
                    continue

            # await asyncio.sleep(timeout)
            await message.channel.send("Answer ....**"+result["correctAns"]+"**")

            print(f"submitted answer dictionary: {answers}")

            # check user answers and update db to add or remove points
            for author, ans in answers.items():
                print(author, ans)
                if ans is None:
                    continue
                elif ans.lower() == result["correctAns"].lower():
                    add_score(author, result["point value"])
                else:
                    # if answer is wrong increment game played
                    add_game_data(author)


        # get current scoreboard
        if message.content == ('$leaderboard'):          
            # await message.channel.send('------ Scoreboard ------\n >>> {}'.format('\n'.join(get_scores())))
            await message.channel.send(f"```{get_scores()}```")
            await message.channel.send(file=discord.File(os.path.join(home_path,'score_chart.jpg')))

        if message.content == ('$chart'):
            # return pie chart of trivia questions returned thus far
            filename = get_question_chart()
            await message.channel.send(file=discord.File(os.path.join(home_path,filename)))


        # initialize db
        if message.content == ('$init') and message.author.name == 'wickabeast33':
            # connect to db
            conn = sqlite3.connect(pi_DBpath)
            print("db connected")
            c = conn.cursor()

            # create initial scoreboard and question log table
            c.execute(
                '''create table if not exists scoreboard 
            (id text primary key,
            username text not null,
            name text not null,
            score integer,
            q_played integer,
            numCorr integer);''')
            conn.commit()

            c.execute(
                '''create table if not exists triviaLog
                (id integer primary key autoincrement,
                datetime text,
                difficulty text,
                point_value integer,
                category text
                );''')
            conn.commit()

            # get all members in channel and load into db
            members = bot.get_all_members()
            for member in members:
                # only return message if member not bot role
                if not member.bot:
                    try:
                        c.execute(f"INSERT INTO scoreboard (id, username, name, score, q_played, numCorr) VALUES (?,?,?,?,?,?)", (str(member.id),str(member),str(member.name),0,0,0))
                        conn.commit()
                    except sqlite3.Error:
                        await message.channel.send(sqlite3.Error)          
            conn.close()
            await message.channel.send("`db initialization complete`")

            
# get bot token from .env and run client
# has to be at the end of the file
bot.run(os.getenv('TOKEN'))