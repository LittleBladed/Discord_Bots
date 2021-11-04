import discord
from discord.ext import commands

blacklist = []
file = open("Blacklist.txt", "r")
lines = file.readlines()
for line in lines:
    line = line.rstrip()
    blacklist.append(line)


class AgreeMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def agreeMessage(self, ctx):
        embed = discord.Embed(title="Spirit theater rules agreement", color=0x8934eb)
        embed2 = discord.Embed(title="Please type -agree",description="This accepts the server rules and unlocks the other channels", color=0x8934eb)
        await ctx.send(embed=embed)
        await ctx.send(embed=embed2)


def setup(bot):
    bot.add_cog(AgreeMessage(bot))