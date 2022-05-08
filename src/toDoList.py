import discord
import json
import pathlib
import datetime
from discord.ext import commands
from datetime import date

class ToDoList(commands.Cog):

    def __init__(self,client):
        self.client = client
    
    @commands.command()
    async def add(self,ctx, *, task):
        toDoList = {}
        
        taskName = task
        dueDate = None
        today = date.today()
        currentDate = today.strftime("%m/%d/%Y")

        def check(m):
            author = ctx.author
            channel = ctx.channel
            return m.author == author and m.channel == channel

        for i in task:
            if (i == "-"): 
                taskName = task[:task.index(i)-1]
                dueDate = task[task.index(i)+1:len(task)]
                dueDate = dueDate.strip()
                try:
                    datetime.datetime.strptime(dueDate, "%m/%d/%Y %H:%M")
                    toDoList['Task Name'] = taskName
                    toDoList['Due Date'] = dueDate
                    fileName = str(ctx.author.id) + ".json"
                    path = pathlib.Path("todolists/" + fileName)
                    output = []
                    output.append(toDoList)
                    prior = []
                    if (path.exists()):
                        with path.open("r") as file:
                            prior = json.load(file)
                    for item in prior:
                        output.append(item)
                    with path.open("w") as file:
                        json.dump(output, file)
                    msg = discord.Embed(
                        title = taskName,
                        description = f'Successfully Added Task:\nTitle: {taskName}\nDue Date & Time: {dueDate}',
                        color = 0x00FFFF
                    )
                    await ctx.send(embed=msg)
                except ValueError:
                    await ctx.send("Sorry, that is in the incorrect format. Please try the function again.\n*Reminder: The format for due date is mm/dd/yyyy hh:mm (e.g 08/05/2022 22:14)*")
 
    @commands.command()
    async def remove(ctx, *, taskTitle):
        fileName = str(ctx.author.id) + ".json"
        f = open(fileName)
        data = json.load(f)

        removed = [i for i in data if not (i["Task Name"] == taskTitle)]

        path = pathlib.Path(fileName)
        output = removed
        with path.open("w") as file:
            json.dump(output, file)
        msg = discord.Embed(
            title = taskTitle,
            description = f'Successfully Removed Task: {taskTitle}',
            color = 0x00FFFF
        )
        await ctx.send(embed=msg)

def setup(client):
    client.add_cog(ToDoList(client))