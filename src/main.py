import asyncio
import discord
import json
from discord.ext import commands
import flashcards_external

intents = discord.Intents.default()
client = commands.Bot(command_prefix="!", intents=intents)
client.help_command = None

def init():
  client.run("OTcyMzc3MTIwNzY2NTYyMzU0.YnYKww.qh8S6x2h0AIDfXgj-8J30_3RjVM")

@client.event
async def on_ready():
  print("ready")

@client.command()
async def hello(ctx):
  await ctx.send("hello!")
  def check(m):
    return m.author == ctx.author and m.channel == ctx.channel
  msg = await client.wait_for('message', check=check)
  await ctx.send(msg.content)

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
  elif arg1 == "stop":
    return
  else:
    embed = discord.Embed(title="Invalid Option")
    await ctx.send(embed=embed)

init()