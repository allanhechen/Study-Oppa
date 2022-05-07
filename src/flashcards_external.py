import discord
import json
import pathlib
import datetime
from discord.ext import commands

async def study(client, member, channel):
  p = get_default_path(member)
  preferences = await load_preferences(member, channel)
  timeout = preferences["timeout"]
  color = preferences["color"]

  if not p.exists() or sum([1 for f in p.iterdir()]) == 0:
    embed=discord.Embed(title="You have no flashcards!", description="use \"!flashcards add\" to add some!", color=color)
    await channel.send(embed=embed)
    return
  prefix = "flashcards\\" + str(member.id) + "\\"
  
  embed=discord.Embed(title="Available flashcards:", description="\"stop\" to exit", color=color)
  for path in p.iterdir():
    name = str(path).removeprefix(prefix)[:-5]
    last_modified = datetime.datetime.fromtimestamp(path.stat().st_ctime)
    embed.add_field(name=name, value=last_modified, inline=False)
  await channel.send(embed=embed)

  def check(m):
    return m.author == member and m.channel == channel

  selection = await client.wait_for('message', check=check, timeout=timeout)
  selection = selection.content

  if (selection == exit):
    return

  p = p / (selection + ".json")
  if not p.exists():
    embed=discord.Embed(title="Invalid Selection", color=color)
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
      embed=discord.Embed(title="Question: " + question["question"], color=color)
      await channel.send(embed=embed)
      await client.wait_for('message', check=check)
      embed=discord.Embed(title="Expected Answer: " + question["answer"], color=color)
      sent_message = await channel.send(embed=embed)
      await sent_message.add_reaction('🔴')
      await sent_message.add_reaction('🟡')
      await sent_message.add_reaction('🟢')
      reaction = await client.wait_for('reaction_add', check=reaction_check, timeout=timeout)
      reaction = reaction[0].emoji
      if reaction == '🔴':
        question["priority"] = max(question["priority"] - 1, 1)
        next.append(question)
      if reaction == '🟢':
        question["priority"] = min(question["priority"] + 1, 3)
    
    embed=discord.Embed(title="End of flashcards in " + selection + ".", description="Type \"continue\" to start again.", color=color)
    await channel.send(embed=embed)
    reply = await client.wait_for('message', check=check, timeout=timeout)
    reply = reply.content.lower()
    if reply != "continue":
      cont = 0

  if len(next) > 0:
    embed=discord.Embed(title="Go through hard questions again?" , description="Type \"yes\" to proceed.", color=color)
    await channel.send(embed=embed)
    message = await client.wait_for('message', check=check, timeout=timeout)
    message = message.content.lower()
    if message == "yes":
      for question in next:
        embed=discord.Embed(title="Question: " + question["question"], color=color)
        await channel.send(embed=embed)
        await client.wait_for('message', check=check, timeout=timeout)
        embed=discord.Embed(title="Expected Answer: " + question["answer"], color=color)
        sent_message = await channel.send(embed=embed)
        await sent_message.add_reaction('🔴')
        await sent_message.add_reaction('🟡')
        await sent_message.add_reaction('🟢')
        reaction = await client.wait_for('reaction_add', check=reaction_check, timeout=timeout)
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
  preferences = await load_preferences(member, channel)
  timeout = preferences["timeout"]
  color = preferences["color"]

  def check(m):
    return m.author == member and m.channel == channel

  embed=discord.Embed(title="Enter category name:", color=color)
  await channel.send(embed=embed)
  
  name = await client.wait_for('message', check=check, timeout=timeout)
  name = name.content
  name = name.replace("<", "").replace(">", "").replace(":", "").replace("\"", "").replace("/", "").replace("\\", "").replace("|", "").replace("?", "").replace("*", "")
  # name.replace(" ", "_")

  output = []
  while 1:
    embed=discord.Embed(title="Please enter a question:", description="\"stop\" to exit", color=color)
    await channel.send(embed=embed)
    question = await client.wait_for('message', check=check, timeout=timeout)
    question = question.content
    
    if question == "stop":
      break

    embed=discord.Embed(title="Please enter an answer:", color=color)
    await channel.send(embed=embed)
    answer = await client.wait_for('message', check=check, timeout=timeout)
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
    embed=discord.Embed(title="Category " + name + " added.", color=color)
    await channel.send(embed=embed)

async def remove(client, member, channel):
  def check(m):
    return m.author == member and m.channel == channel

  preferences = await load_preferences(member, channel)
  timeout = preferences["timeout"]
  color = preferences["color"]

  embed=discord.Embed(title="Please enter an item to remove.", description="Type \"stop\" to exit", color=color)
  embed.add_field(name="Question", value="Remove a question from a section", inline=False)
  embed.add_field(name="Section", value="Remove an entire section", inline=False)
  await channel.send(embed=embed)
  selection = await client.wait_for('message', check=check)
  selection = selection.content
  if selection == "stop":
    return
  elif selection == "question":
    p = get_default_path(member)
    section = await get_options(client, member, channel)
    if section == -1:
      return
    p = p / section
    data = None
    with p.open("r") as f:
      data = json.load(f)
    embed=discord.Embed(title="Please enter the question.")
    await channel.send(embed=embed)
    question = await client.wait_for('message', check=check, timeout=timeout)
    question = question.content
    for i in range(len(data)):
      if data[i]["question"] == question:
        data.pop(i)
    with p.open("w") as f:
      data = json.dump(data, f)
    embed=discord.Embed(title="Question " + question + " removed.", color=color)
    await channel.send(embed=embed)
    return
  elif selection == "section":
    p = get_default_path(member)
    section = await get_options(client, member, channel)
    if section == -1:
      return
    p = p / section
    p.unlink()
    embed=discord.Embed(title="Section " + section[:-5] + " removed.", color=color)
    await channel.send(embed=embed)
    return
  else:
    embed=discord.Embed(title="Invalid option.", description="Type \"stop\" to exit.", color=color)
    await channel.send(embed=embed)
    await remove(client, member, channel)

async def change_preferences(client, member, channel):
  def check(m):
    return m.author == member and m.channel == channel

  p = pathlib.Path("config/" + str(member.id) + ".json")
  preferences = await load_preferences(member, channel)
  color = preferences["color"]
  timeout = preferences["timeout"]

  embed=discord.Embed(title="Enter the preference you would like to change.", color=color)
  embed.add_field(name="Color", value="Change the embed color.", inline=False)
  embed.add_field(name="Timeout", value="Change the amount of time you have to respond to questions.", inline=False)
  await channel.send(embed=embed)
  selection = await client.wait_for('message', check=check, timeout=timeout)
  selection = selection.content.lower()

  if selection == "color":
    embed=discord.Embed(title="Enter your new color (0x6bb3ff by default).", color=color)
    new_color = await client.wait_for('message', check=check, timeout=timeout)
    new_color = hex(new_color.content)
    preferences["color"] = new_color
  elif selection == "timeout":
    embed=discord.Embed(title="Enter your new timeout (15s default).", color=color)
    new_timeout = await client.wait_for('message', check=check, timeout=timeout)
    new_timeout = int(new_timeout.content)
    preferences["timeout"] = new_timeout
  else:
    embed=discord.Embed(title="Invalid Option.", color=color)
    await channel.send(embed=embed)
    return
  with p.open("w") as f:
    json.dump(preferences, f)

def get_default_path(member):
  return pathlib.Path("flashcards/" + str(member.id))

async def get_options(client, member, channel):
  p = get_default_path(member)

  preferences = await load_preferences(member, channel)
  timeout = preferences["timeout"]
  color = preferences["color"]

  if not p.exists() or sum([1 for f in p.iterdir()]) == 0:
    embed=discord.Embed(title="You have no flashcards!", color=color)
    await channel.send(embed=embed)
    return -1
  prefix = "flashcards\\" + str(member.id) + "\\"
  
  embed=discord.Embed(title="Available flashcards:", description="Type \"stop\" to exit", color=color)
  for path in p.iterdir():
    name = str(path).removeprefix(prefix)[:-5]
    last_modified = datetime.datetime.fromtimestamp(path.stat().st_ctime)
    embed.add_field(name=name, value=last_modified, inline=False)
  await channel.send(embed=embed)

  def check(m):
    return m.author == member and m.channel == channel

  selection = await client.wait_for('message', check=check, timeout=timeout)
  return selection.content + ".json"

async def load_preferences(member, channel):
  p = pathlib.Path("config/" + str(member.id) + ".json")
  if p.exists():
    with p.open("r") as f:
      result = json.load(f)
      return result
  else:
    settings = {}
    settings["timeout"] = 15
    settings["color"] = 0x6bb3ff
    with p.open("w") as f:
      json.dump(settings, f)
    await help(member, channel)
    return settings

async def help(member, channel):
  pass