# Imports
import os
import time
import os.path
import discord
import json
import framework.auth
from datetime import datetime
from discord.ext import commands
from discord.ext.commands import *
from framework.logger import Logger

# User Configuration (edit stuff here)
prefix = "-"  # Default prefix is -, you can replace it with your preferred prefix
owner = "EMPTY_USERNAME#0000"  # Replace 'EMPTY_USERNAME#0000' with your Discord username

# Variables
intents = discord.Intents.all()
botVer = 'v1.2.1'
if os.name == 'nt': os.system('cls')
else: os.system('clear')
client = commands.Bot(command_prefix=str(prefix), intents=intents)  # READ COMMENT AT LINE 13 FOR MORE INFO
slash = SlashCommand(client, sync_commands=True)
global startTime
startTime = time.time()
client.remove_command('help')
homedir = os.getcwd()
config = {}

if os.name == 'nt': 
    with open(f'{homedir}\\config.json', 'r', encoding="utf-8") as f: config = json.load(f)
else: 
    with open(f'{homedir}/config.json', 'r', encoding="utf-8") as f: config = json.load(f)

snipe_log:bool = config[str("config")][str("logs")]["snipe"]
editsnipe_log:bool = config[str("config")][str("logs")]["editsnipe"]

if os.name == "nt":
    if not os.path.isdir(f"{homedir}\\snipe-bot-data"):
        os.mkdir(f"{homedir}\\snipe-bot-data")
        # Making log files (mode 'x' creates new file in that path if it doesn't exist. Open file and do not write to it)
        open(f"{homedir}\\snipe-bot-data\\snipe.log", 'x', encoding="utf-8")
        open(f"{homedir}\\snipe-bot-data\\editsnipe.log", 'x', encoding="utf-8")
        open(f"{homedir}\\snipe-bot-data\\errors.log", 'x', encoding="utf-8")
if os.name == "posix":
    if not os.path.isdir(f"{homedir}/snipe-bot-data"):
        os.mkdir(f"{homedir}/snipe-bot-data")
        open(f"{homedir}/snipe-bot-data/snipe.log", 'x', encoding="utf-8")
        open(f"{homedir}/snipe-bot-data/editsnipe.log", 'x', encoding="utf-8")
        open(f"{homedir}/snipe-bot-data/errors.log", 'x', encoding="utf-8")

logger = Logger(os.name, homedir)

@client.command()
async def help(ctx):
    e = discord.Embed(title='Command Help', description=f'Prefix: `{prefix}`\n\n`{str(prefix)}snipe`: See the most recently deleted message in this channel.\n`{str(prefix)}editsnipe`: See the most recently edited message in this channel.', color=discord.Color.random())
    await ctx.send(embed=e)

# API Events
@client.event
async def on_ready():
    print(f'Logged on to Discord as {client.user.name}')
    print('====================')
    print('Some client info:')
    print('------------------')
    print(f'  Latency: {round(client.latency * 1000)}ms')
    print(f'  Startup time: {round(startTime)}')
    print(f'  Owner: {str(owner)}')
    print('------------------')
    print('====================')

snipe_message_content = {}
snipe_message_author = {}
editsnipe_message_before_content = {}
editsnipe_message_after_content = {}
editsnipe_message_author = {}

@client.event
async def on_message_delete(message):
    if not message.author.bot:
        channel = message.channel
        snipe_message_author[message.channel.id] = message.author
        snipe_message_content[message.channel.id] = message.content
        if bool(snipe_log):
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"[{timestamp}] Message deleted in #{channel} ({message.guild}):\n   Message content: {message.content}")
            logger.snipe(f"[{timestamp}] Message deleted in #{channel} ({message.guild}): {message.content}")
        else: pass

@client.event
async def on_message_edit(message_before, message_after):
    if not message_after.author.bot:
        editsnipe_message_author[message_before.channel.id] = message_before.author
        guild = message_before.guild.id
        channel = message_before.channel
        editsnipe_message_before_content[channel.id] = message_before.content
        editsnipe_message_after_content[channel.id] = message_after.content
        if bool(editsnipe_log):
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"[{timestamp}] Message edited in #{channel} ({message_before.guild}):\n   Old message: {message_before.content}\n   New message: {message_after.content}")
            logger.editsnipe(f"[{timestamp}] Message edited in #{channel} ({message_before.guild}):\n   Old message: {message_before.content}\n   New message: {message_after.content}")
        else: pass

# Commands
@client.command()
async def snipe(ctx):
    channel = ctx.channel
    try:
        em = discord.Embed(title=f"Last deleted message in #{channel.name}", description=snipe_message_content[channel.id], color=discord.Color.random())
        em.set_footer(text=f"This message was sent by {snipe_message_author[channel.id]}")
        await ctx.send(embed=em)
    except KeyError: await ctx.send(f"There are no recently deleted messages in <#{channel.id}>")

@client.command()
async def editsnipe(ctx):
    channel = ctx.channel
    try:
        em = discord.Embed(description=f'**Message before**:```{editsnipe_message_before_content[ctx.channel.id]}```\n**Message after**:```{editsnipe_message_after_content[ctx.channel.id]}```', color=discord.Color.random())
        em.set_footer(text=f'This message was edited by {editsnipe_message_author[channel.id]}')
        await ctx.send(embed=em)
    except KeyError: await ctx.reply(f'There are no recently edited messages in <#{ctx.channel.id}>')

@slash.slash(
    name="snipe",
    description="Fetches the most-recently deleted message in this channel"
)
async def snipe(ctx: SlashContext):
    channel = ctx.channel
    try:
        em = discord.Embed(title=f"Last deleted message in #{channel.name}", description=snipe_message_content[channel.id], color=discord.Color.random())
        em.set_footer(text=f"This message was sent by {snipe_message_author[channel.id]}")
        await ctx.send(embed=em)
    except KeyError: await ctx.send(f"There are no recently deleted messages in <#{channel.id}>")

@slash.slash(
    name="editsnipe",
    description="Fetches the most-recently edited message in this channel"
)
async def editsnipe(ctx: SlashContext):
    channel = ctx.channel
    try:
        em = discord.Embed(description=f'**Message before**:```{editsnipe_message_before_content[ctx.channel.id]}```\n**Message after**:```{editsnipe_message_after_content[ctx.channel.id]}```', color=discord.Color.random())
        em.set_footer(text=f'This message was edited by {editsnipe_message_author[channel.id]}')
        await ctx.send(embed=em)
    except KeyError: await ctx.reply(f'There are no recently edited messages in <#{ctx.channel.id}>')

# Initialization
token = framework.auth.get_token()
if token != "": 
    try: client.run(token)
    except Exception as exc:
        print(f"[main/CLIENT] Error: Unable to start client: {type(exc).__name__}: {exc}")
        raise SystemExit
else:
    print("[main/CLIENT] Error: Unable to start client: No Discord bot token found. Please insert one in the \"token\" value in the config.json file and try again.\nYou can get a Discord bot token from https://discord.com/developers by making a new application.")
    raise SystemExit
