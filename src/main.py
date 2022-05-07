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
async def flashcards(ctx, arg1 = ""):
  channel = ctx.channel
  member = ctx.author
  
  if arg1 == "":
    def check(m):
      return m.author == ctx.author and m.channel == ctx.channel

    embed=discord.Embed(title="Please select an option:", color=0x6bb3ff)
    embed.add_field(name="Study", value="Study available flashcards", inline=False)
    embed.add_field(name="Add", value="Add new flashcards", inline=False)
    embed.add_field(name="Remove", value="Remove existing flashcards", inline=False)
    await ctx.send(embed=embed)

    arg1 = await client.wait_for('message', check=check)
    arg1 = arg1.content.strip().lower()

  if arg1 == "study":
    await flashcards_external.study(client, member, channel)
  elif arg1 == "add":
    await flashcards_external.add(client, member, channel)
  elif arg1 == "remove":
    print("remove")
  elif arg1 == "change preferences":
    print("change preferences")
  else:
    embed = discord.Embed(title="Invalid Option")
    await ctx.send(embed=embed)

init()