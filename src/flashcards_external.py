import discord
import json
import pathlib
import datetime
from discord.ext import commands

async def study(client, member, channel):
  p = get_default_path(member)
  if not p.exists():
    embed=discord.Embed(title="You have no flashcards!", description="use \"!flashcards add\" to add some!", color=0x6bb3ff)
    await channel.send(embed=embed)
    return
  prefix = "flashcards\\" + str(member.id) + "\\"
  
  embed=discord.Embed(title="Available flashcards:", color=0x6bb3ff)
  for path in p.iterdir():
    name = str(path).removeprefix(prefix)[:-5]
    last_modified = datetime.datetime.fromtimestamp(path.stat().st_ctime)
    embed.add_field(name=name, value=last_modified, inline=False)
  await channel.send(embed=embed)

  

async def add(client, member, channel):
  p = get_default_path(member)
  p.mkdir(parents=True, exist_ok=True)

  def check(m):
    return m.author == member and m.channel == channel

  embed=discord.Embed(title="Enter category name:", color=0x6bb3ff)
  await channel.send(embed=embed)
  
  name = await client.wait_for('message', check=check)
  name = name.content
  name.replace("<>:\"/\\|?*;", "")
  name.replace(" ", "_")

  output = []
  while 1:
    embed=discord.Embed(title="Please enter a question:", description="\"stop\" to exit", color=0x6bb3ff)
    await channel.send(embed=embed)
    question = await client.wait_for('message', check=check)
    question = question.content
    
    if question == "stop":
      break

    embed=discord.Embed(title="Please enter an answer:", color=0x6bb3ff)
    await channel.send(embed=embed)
    answer = await client.wait_for('message', check=check)
    answer = answer.content
    current = {}
    current["question"] = question
    current["answer"] = answer
    current["priority"] = 2
    output.append(current)

  if len(output) > 0:
    p = p / (name + ".json")
    with p.open('a') as f:
      json.dump(output, f)
    embed=discord.Embed(title="Category " + name + " added.", color=0x6bb3ff)
    await channel.send(embed=embed)

async def remove(member, channel):
  pass

async def change_preferences(member, channel):
  pass

def get_default_path(member):
  return pathlib.Path("flashcards/" + str(member.id))