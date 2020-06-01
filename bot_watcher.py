import discord
import queue
import asyncio
import datetime
import os

from dotenv import load_dotenv
from discord.ext import commands
from discord.ext import tasks

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='$')
q = queue.Queue()

channel_set = False
misc_channel = {}
#misc_channel = 630354263134044177
misc_bot = {}
#misc_bot = 235088799074484224

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name = 'channel')
async def _channel(ctx, arg: int):
    global misc_channel
    guild_id = ctx.guild.id
    misc_channel[guild_id] = arg
    channel_set = True
    print("catch a channel command in server: ", guild_id , arg)
    print("Full list: ", misc_channel)
    await ctx.send("Music channel set up complete, channel id: " + str(arg))

@bot.command(name = 'player')
async def _player(ctx, arg: int):
    global misc_bot
    guild_id = ctx.guild.id
    misc_bot[guild_id] = arg
    print("catch a player command in server: ", guild_id , arg)
    print("Full list: ", misc_bot)
    await ctx.send("music bot set as: " + str(arg))

@bot.command(name = 'blk_list')
async def _blk(ctx, arg):
    player = arg
    print("arg")


@bot.event
async def on_message(msg):
    global q
    guild_id = msg.guild.id
    print(guild_id)
    #print('processing message id', msg.id)
    #print("inside",misc_channel,type(misc_channel))
    if msg.content.startswith("$"):
        await bot.process_commands(msg)
    else:
        if msg.channel.id != misc_channel[guild_id] and msg.content.startswith("!"):
            q.put(msg) #queue for print message
            print(datetime.datetime.now(), 'put', msg.id)
            await msg.delete()
        if msg.channel.id != misc_channel[guild_id] and msg.author.id == misc_bot[guild_id]:
            q.put(msg) #queue for print message
            print(datetime.datetime.now(), 'put', msg.id)
            await msg.delete()
        await bot.process_commands(msg)

@tasks.loop(seconds = 2)
async def watcher():
    global q
    if not q.empty():
        print(datetime.datetime.now(), ': awakened')
    while not q.empty():
        msg = q.get()
        guild_id = msg.guild.id
        ch = bot.get_channel(misc_channel[guild_id])
        print('\t', datetime.datetime.now(), 'processing id', msg.id)
        if msg.author.id != misc_bot[guild_id]:
            await ch.send(msg.author.mention + " ***All music commands needs to be send in this channel***")
            await ch.send(msg.content)
        elif msg.embeds != []:
            await ch.send(content = msg.content, embed = msg.embeds[0])
        else:
            await ch.send(msg.content)
    #await bot.wait_until_ready()
    #counter = 0

watcher.start()

bot.run(TOKEN)
