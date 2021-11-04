import discord
from discord.ext import commands

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def agree(self, ctx):
        await ctx.message.delete()
        member = ctx.message.author
        newGoer = discord.utils.get(member.guild.roles, name="New Theater Goer")
        goer = discord.utils.get(member.guild.roles, name="Theater Goer")
        await member.remove_roles(newGoer)
        await member.add_roles(goer)



def setup(bot):
    bot.add_cog(Verification(bot))