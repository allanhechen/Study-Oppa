from turtle import title
import discord
import json
import pathlib
import datetime
import asyncio
from discord.ext import commands

async def add(ctx, *, item):
    dateTime = item[-15:len(item)]
    title = item[:-16]
    await ctx.send(f'Date & Time: {dateTime}\nTitle: {title}')
    
# async def help(member, channel):
#   embed=discord.Embed(title="This is the help section for flashcards", description="Type \"stop\" to stop in any submenus", color=0x6bb3ff)
#   embed.add_field(name="Add", value="Make a new study section or append to a current study section", inline=False)
#   embed.add_field(name="Study", value="Review flashcards in a study section", inline=False)
#   embed.add_field(name="Remove", value="Remove either a section or a question from a sesction", inline=False)
#   embed.add_field(name="Change Preferences", value="Change either color or timeout", inline=False)
#   await channel.send(embed=embed)