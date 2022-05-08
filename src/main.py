import asyncio
from datetime import datetime
import discord
import json
from discord.ext import commands
from discord.ext import tasks
import pathlib
import flashcards_external
import pomodoro
import todolist

def read_config():
  p = pathlib.Path("config/config.json")
  with p.open("r") as f:
    config = json.load(f)
    return config

config = read_config()
intents = discord.Intents.default()
client = commands.Bot(command_prefix=config["prefix"], intents=intents)
client.help_command = None

def init():
  client.run(config["ID"])

@client.event
async def on_ready():
  client.load_extension('pomodoro')
  client.load_extension("todolist")
  print("ready")
  await update_count()

@tasks.loop(minutes=10)
async def update_count():
  total = 0
  for guild in client.guilds:
    total += guild.member_count
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=str(total) + " users studying"))


@client.command()
async def hello(ctx):
  await ctx.send("hello!")
  def check(m):
    return m.author == ctx.author and m.channel == ctx.channel
  msg = await client.wait_for('message', check=check)
  await ctx.send(msg.content)

@client.command()
async def help(ctx, arg1 = ""):
  embed=discord.Embed(title="This is Study Oppa's default help menu.", description="Choose one of the options below to learn more", color=0x8EA8FB)
  embed.add_field(name="flashcards", value="flashcards but in Discord!", inline=False)
  embed.add_field(name="pomodoro", value="advanced studying technique", inline=False)
  embed.add_field(name="todolist", value="keeps track of what's left to do", inline=False)
  await ctx.send(embed=embed)
  if arg1 == "flashcards":
    await flashcards_external.help(ctx.author, ctx.channel)
    return
  elif arg1 == "pomodoro":
    await pomodoro.help(ctx.author, ctx.channel)
    return
  elif arg1 == "todolist":
    await todolist.help(ctx.author, ctx.channel)
  elif "!" in arg1:
    return
  else:
    embed=discord.Embed(title="Invalid Options")
    await ctx.send(embed=embed)

@client.command()
async def flashcards(ctx, arg1 = "", arg2 = ""):
  channel = ctx.channel
  member = ctx.author
  
  if arg1 == "":
    def check(m):
      return m.author == ctx.author and m.channel == ctx.channel
    preferences = await flashcards_external.load_preferences(ctx.author, ctx.channel)
    color = preferences["color"]
    timeout = preferences["timeout"]

    embed=discord.Embed(title="Please select an option:", color=color)
    embed.add_field(name="Study", value="Study available flashcards", inline=False)
    embed.add_field(name="Add", value="Add new flashcards", inline=False)
    embed.add_field(name="Remove", value="Remove existing flashcards", inline=False)
    embed.add_field(name="Change Preferences", value="Change color and timeout", inline=False)
    await ctx.send(embed=embed)
    try:
      arg1 = await client.wait_for('message', check=check, timeout=timeout)
    except asyncio.exceptions.TimeoutError:
      return
    arg1 = arg1.content.strip().lower()

  if arg1 == "study":
    await flashcards_external.study(client, member, channel)
  elif arg1 == "add":
    await flashcards_external.add(client, member, channel)
  elif arg1 == "remove":
    await flashcards_external.remove(client, member, channel)
  elif arg1 == "change" and arg2 == "preferences" or arg1 == "change preferences":
    await flashcards_external.change_preferences(client, member, channel)
  elif arg1 == "help":
    await flashcards_external.help(ctx.author, ctx.channel)
  elif arg1 == "stop":
    return
  elif "!" in arg1:
    return
  else:
    embed = discord.Embed(title="Invalid Option")
    await ctx.send(embed=embed)

init()