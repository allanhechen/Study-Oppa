from discord.ext import commands
import asyncio
from discord import Embed
from timer import Timer, TimerStatus

class Pomodoro(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.users = []
        self.timer = Timer()

    @commands.command()
    async def pomostart(self, ctx):
        try:

            if (self.timer.getStatus() == TimerStatus.RUNNING):
                await ctx.send("*Pomodoro already running.*")
                return
            else:
                self.timer.start()

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            await ctx.send("*Enter study minutes:*")
            try:
                studyMinutes = await self.client.wait_for('message', check=check)
            except asyncio.exceptions.TimeoutError:
                return
            studyMinutes = int(studyMinutes.content)
            if studyMinutes <= 0:
                self.timer.stop()
                await ctx.send("*Minutes must be positive.*")
                return

            await ctx.send("*Enter break minutes:*")
            try:
                breakMinutes = await self.client.wait_for('message', check=check)
            except asyncio.exceptions.TimeoutError:
                return
            breakMinutes = int(breakMinutes.content)
            if breakMinutes <= 0:
                self.timer.stop()
                await ctx.send("*Minutes must be positive.*")
                return

            embed = Embed(title="**Pomodoro Timer**", description = f"**{studyMinutes}** minute(s) study time\n**{breakMinutes}** minute(s) break time\n\n*React to be pinged!*", color=0x8EA8FB)
            startMsg = await ctx.send(embed=embed)
            global startID
            startID = startMsg.id

            await startMsg.add_reaction("✅")
            await startMsg.add_reaction("❌")

            cycle = 0
            while (self.timer.getStatus() == TimerStatus.RUNNING):

                studySeconds = 60 * int(studyMinutes)
                breakSeconds = 60 * int(breakMinutes)
                
                embed = Embed(title= f"**{studySeconds // 60} minute(s) {studySeconds % 60} seconds**", color=0xAFE1AF)
                message = await ctx.send(embed=embed)

                while studySeconds != 0:
                    
                    if (self.timer.getStatus() == TimerStatus.STOPPED):
                        await message.edit(embed=Embed(title= f"**Pomodoro has stopped.**", description = f'{cycle} cycle(s) completed', color=0x900C3F))
                        return

                    studySeconds -= 1

                    await message.edit(embed=Embed(title= f"**{studySeconds // 60} minute(s) {studySeconds % 60} seconds**", color=0xAFE1AF))
                    await asyncio.sleep(1)
                
                for userID in self.users:
                    await ctx.send(f'<@{userID}> Break time! ☕️')

                while breakSeconds != 0:

                    if (self.timer.getStatus() == TimerStatus.STOPPED):
                        await message.edit(embed=Embed(title= f"**Pomodoro has stopped.**", description = f'{cycle} cycle(s) completed', color=0x900C3F))
                        return

                    breakSeconds -= 1
                    await message.edit(embed=Embed(title= f"**{breakSeconds // 60} minute(s) {breakSeconds % 60} seconds**", color=0xFFC300))
                    await asyncio.sleep(1)

                cycle += 1
                await message.edit(embed=Embed(title= f"**Cycle {cycle} complete.**", color=0xAFE1AF))
                for userID in self.users:
                    await ctx.send(f'<@{userID}> Back to work! 📖')

        except ValueError:
            await ctx.send('*Entered time was not a number*')
            self.timer.stop()
        
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.message.id == startID:
            if reaction.emoji == "✅":
                if (user.id not in self.users):
                    self.users.append(user.id)
            if reaction.emoji == "❌":
                if (user.id in self.users):
                    self.users.remove(user.id)

    @commands.command()
    async def pomostop(self, ctx):
        self.users = []
        self.timer.stop()

def setup(client):
    client.add_cog(Pomodoro(client))

async def help(member, channel):
    embed = Embed(title="This is the help section for pomodoro", description="", color=0x8EA8FB)
    embed.add_field(name="!pomostart", value="Start a pomodoro timer and enter study and break minutes", inline=False)
    embed.add_field(name="!pomostop", value="End the pomodoro timer.", inline=False)
    await channel.send(embed=embed)