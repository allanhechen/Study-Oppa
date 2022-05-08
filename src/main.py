import asyncio
import discord
import json
from discord.ext import commands
from discord.ext import tasks
import flashcards_external
import pomodoro
import toDoList 

intents = discord.Intents.default()
client = commands.Bot(command_prefix="!", intents=intents)
client.help_command = None

def init():
  client.run("OTcyMzc3MTIwNzY2NTYyMzU0.YnYKww.qh8S6x2h0AIDfXgj-8J30_3RjVM")

@client.event
async def on_ready():
  print("ready")
  client.load_extension('pomodoro')
  await update_count()


@tasks.loop(minutes=10)
async def update_count():
  total = 0
  for guild in client.guilds:
    total += guild.member_count
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=" over " + str(total) + " users study"))


@client.command()
async def hello(ctx):
  await ctx.send("hello!")
  def check(m):
    return m.author == ctx.author and m.channel == ctx.channel
  msg = await client.wait_for('message', check=check)
  await ctx.send(msg.content)

@client.command()
async def help(ctx, arg1):
  if arg1 == "flashcards":
    await flashcards_external.help(ctx.author, ctx.channel)
  elif arg1 == "pomodoro":
    await pomodoro.help(ctx.author, ctx.channel)
    return

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

# @client.command()
# async def toDoList(ctx, arg1 = "", arg2 = ""):
#   channel = ctx.channel
#   member = ctx.author
  
#   if arg1 == "addItem":
#     await toDoList.add(ctx, *, item)
#   else:
#     embed = discord.Embed(title="Invalid Option")
#     await ctx.send(embed=embed)

 #dictionary key = scheduleTitle, value = dateTime
list = {}
@client.command()
async def add(ctx, *, item):
    dateTime = item[-16:len(item)]
    taskTitle = item[:-17]
    list[taskTitle] = dateTime
    # await ctx.send(f'Date & Time: {dateTime}\nTitle: {scheduleTitle}')
    
    p = "person1List.json"
    with p.open('a') as f:
      json.dump(list, f)
    msg = discord.Embed(
      title = 'Testing',
      description = f'Date & Time: {list.values()}\nTitle: {list.keys()}',
      color = 0x00FFFF
    )
    await ctx.send(embed=msg)

init()