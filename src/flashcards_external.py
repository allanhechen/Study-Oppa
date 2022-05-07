import discord
import json
import pathlib
import datetime
from discord.ext import commands

async def study(client, member, channel):
  p = get_default_path(member)
  if not p.exists() or sum([1 for f in p.iterdir()]) == 0:
    embed=discord.Embed(title="You have no flashcards!", description="use \"!flashcards add\" to add some!", color=0x6bb3ff)
    await channel.send(embed=embed)
    return
  prefix = "flashcards\\" + str(member.id) + "\\"
  
  embed=discord.Embed(title="Available flashcards:", description="\"stop\" to exit", color=0x6bb3ff)
  for path in p.iterdir():
    name = str(path).removeprefix(prefix)[:-5]
    last_modified = datetime.datetime.fromtimestamp(path.stat().st_ctime)
    embed.add_field(name=name, value=last_modified, inline=False)
  await channel.send(embed=embed)

  def check(m):
    return m.author == member and m.channel == channel

  selection = await client.wait_for('message', check=check)
  selection = selection.content

  if (selection == exit):
    return

  p = p / (selection + ".json")
  if not p.exists():
    embed=discord.Embed(title="Invalid Selection", color=0x6bb3ff)
    await channel.send(embed=embed)
    study(client, member, channel)
  
  data = None
  with p.open("r") as f:
    data = json.load(f)

  data = sorted(data, key=lambda x: x["priority"])
  
  def reaction_check(reaction, user):
    return user == member and (str(reaction.emoji) == '🟢' or str(reaction.emoji) == '🟡' or str(reaction.emoji) == '🔴')

  next = []
  cont = 1
  while cont:
    for question in data:
      embed=discord.Embed(title="Question: " + question["question"], color=0x6bb3ff)
      await channel.send(embed=embed)
      await client.wait_for('message', check=check)
      embed=discord.Embed(title="Expected Answer: " + question["answer"], color=0x6bb3ff)
      sent_message = await channel.send(embed=embed)
      await sent_message.add_reaction('🔴')
      await sent_message.add_reaction('🟡')
      await sent_message.add_reaction('🟢')
      reaction = await client.wait_for('reaction_add', check=reaction_check)
      reaction = reaction[0].emoji
      if reaction == '🔴':
        question["priority"] = max(question["priority"] - 1, 1)
        next.append(question)
      if reaction == '🟢':
        question["priority"] = min(question["priority"] + 1, 3)
    
    embed=discord.Embed(title="End of flashcards in " + selection + ".", description="Type \"continue\" to start again.", color=0x6bb3ff)
    await channel.send(embed=embed)
    reply = await client.wait_for('message', check=check)
    reply = reply.content.lower()
    if reply != "continue":
      cont = 0

  if len(next) > 0:
    embed=discord.Embed(title="Go through hard questions again?" , description="Type \"yes\" to proceed.", color=0x6bb3ff)
    await channel.send(embed=embed)
    message = await client.wait_for('message', check=check)
    message = message.content.lower()
    if message == "yes":
      for question in next:
        embed=discord.Embed(title="Question: " + question["question"], color=0x6bb3ff)
        await channel.send(embed=embed)
        await client.wait_for('message', check=check)
        embed=discord.Embed(title="Expected Answer: " + question["answer"], color=0x6bb3ff)
        sent_message = await channel.send(embed=embed)
        await sent_message.add_reaction('🔴')
        await sent_message.add_reaction('🟡')
        await sent_message.add_reaction('🟢')
        reaction = await client.wait_for('reaction_add', check=reaction_check)
        reaction = reaction[0].emoji
        if reaction == '🔴':
          question["priority"] = max(question["priority"] - 1, 1)
        if reaction == '🟢':
          question["priority"] = min(question["priority"] + 1, 3)

  with p.open("w") as f:
    data = json.dump(data, f)
  

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

async def iterate_questions(client, channel, questions):
  pass