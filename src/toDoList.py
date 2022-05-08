import discord
import json
import pathlib
import datetime
from discord import Embed
from discord.ext import commands
from datetime import date

class ToDoList(commands.Cog):

    def __init__(self,client):
        self.client = client
    
    @commands.command()
    async def add(self,ctx, *, task):
        toDoList = {}
        priority = {}
        newList = {}
        
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
                    newList[taskName] = dueDate

                    await ctx.send("What is the priority of the task? [High, Med, Low, None]")
                    priorityA = await self.client.wait_for("message", check=check)
                    while (priorityA.content.lower() != 'high' and priorityA.content.lower() != 'med' and priorityA.content.lower() != 'low' and priorityA.content.lower() != 'none'):
                        await ctx.send("Invalid input. Please try again!\nWhat is the priority of the task? [High, Med, Low, None]")
                        priorityA = await self.client.wait_for("message", check=check)
                    if (priorityA.content.lower() == 'high'):
                        priority["HIGH"] = newList
                    elif (priorityA.content.lower() == 'med'):
                        priority["MED"] = newList
                    elif (priorityA.content.lower() == 'low'):
                        priority["LOW"] = newList
                    else:
                        priority["NONE"] = newList

                    # json file format for printSchedule function
                    fileName = str(ctx.author) + ".json"
                    name = fileName.replace("#", "")
                    path = pathlib.Path("todolists/" + name)
                    output1 = []
                    output1.append(priority)
                    prior1 = []
                    if (path.exists()):
                        with path.open("r") as file:
                            prior1 = json.load(file)
                    for item in prior1:
                        output1.append(item)
                    with path.open("w") as file:
                        json.dump(output1, file)

                    # json file format for remove function
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
                        description = f'Successfully Added Task :)\nTask: {taskName}\nDue Date & Time: {dueDate}\nPriority: {priorityA.content.upper()}',
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

    @commands.command()
    async def printSchedule(self, ctx):

        def check(m):
            author = ctx.author
            channel = ctx.channel
            return m.author == author and m.channel == channel
        
        fileName = str(ctx.author) + ".json"
        name = fileName.replace("#", "")
        path = pathlib.Path("todolists/" + name)
        f = path.open(fileName)
        data = json.load(f)
        
        # @param list 
        # @returns a sorted list
        def sort_dates(dates):
            return dates[6:10], dates[:2], dates[3:5], dates[11:13], dates[14:16]

        # @param Dictionary
        # @return Print chronologically ordered list
        def chronological_order(list):
            
            String = ""

            normalList = []
            
            for priority in list.keys():
                for task in list[priority].keys():
                    normalList.append( list[priority].get(task) )
            
            normalList.sort(key=sort_dates)
            
            count = 1
            
            String += "```__To-Do List__\n"
            
            # This double nested for loop essentially looks for the value that matches with the value within
            # the list given then prints out the task and date/time in chronological order
            for i in normalList:
                for priority in list.keys():
                    for task in list[priority].keys():
                        if list[priority][task] == i:        
                            String += str(count)
                            String += ". {0:20}  {1}\n".format(task, i) 
                            count+=1

            String+= "```"
            
            return String


        # @param Dictionary
        # @return Print priority ordered list
        def priority_order(list):
            
            String = ""
            
            String += "```__To-Do List__\n"
            
            count = 1
            
            highList = []
            for task in list["HIGH"].keys():
                highList.append(list["HIGH"].get(task))
            highList.sort(key=sort_dates)
            for i in highList:
                for priority in list.keys():
                    for task in list[priority].keys():
                        if list[priority][task] == i:  
                            String+= str(count)
                            String+= ". {0:20}  {1} **HIGH**\n".format(task, i) 
                            count+=1
            
            medList = []
            for task in list["MED"].keys():
                medList.append(list["MED"].get(task))
            medList.sort(key=sort_dates)
            for i in medList:
                for priority in list.keys():
                    for task in list[priority].keys():
                        if list[priority][task] == i:  
                            String+= str(count) 
                            String+= ". {0:20}  {1} **MED**\n".format(task, i) 
                            count+=1
                
            
            lowList = []
            for task in list["LOW"].keys():
                lowList.append(list["LOW"].get(task))
            lowList.sort(key=sort_dates)
            for i in lowList:
                for priority in list.keys():
                    for task in list[priority].keys():
                        if list[priority][task] == i:  
                            String+= str(count)
                            String+= ". {0:20}  {1} **LOW**\n".format(task, i) 
                            count+=1
                
            noneList = []
            for task in list["NONE"].keys():
                noneList.append(list["NONE"].get(task))
            noneList.sort(key=sort_dates)
            for i in noneList:
                for priority in list.keys():
                    for task in list[priority].keys():
                        if list[priority][task] == i:  
                            String+= str(count)
                            String+= ". {0:20}  {1} **NONE**\n".format(task, i) 
                            count+=1
                            
            String+= "```"
            
            return String
            
        # @param dictionary 
        # @return priority_order() or chronological_order()
        def printSortedSchedule(list, word):
            
            if "chronological" in word or "Chronological" in word:
                return chronological_order(list)
            elif "priority" in word or "Priority" in word:
                return priority_order(list)

            return discord.Embed(title= word + " invalid, call command again.\n")
        
        #Asks user which sorted method they want to see the schedule
        embed=discord.Embed(title="Sort schedule by...", description="\"chronological\" or \"priority\" order?")
        await ctx.send(embed=embed)
        
        word = await self.client.wait_for('message', check=check)
        word = word.content
        
        await ctx.send(printSortedSchedule(data, word))

def setup(client):
    client.add_cog(ToDoList(client))

async def help(member, channel):
    embed = Embed(title="This is the help section for to-do list", description="", color=0x8EA8FB)
    embed.add_field(name="!add", value="Adds a new task to the to-do list following the format: task name - due date due time\nFor Example: Submit Hackathon Project - 05/08/2022 09:30\n*The time should by given in 24 hour clock style*", inline=False)
    embed.add_field(name="!remove", value="Removes task from the to-do list.", inline=False)
    await channel.send(embed=embed)