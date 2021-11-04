import discord
from discord.ext import commands

blacklist = []
file = open("Blacklist.txt", "r")
lines = file.readlines()
for line in lines:
    line = line.rstrip()
    blacklist.append(line)
file.close()


class Blacklist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        for word in blacklist: 
            if word in message.content.lower():
                await message.delete()
                await message.author.send("Please refrain from using that language %s!" % (message.author.mention), delete_after=10)

    @commands.command(description="Reload the blacklist")
    @commands.has_permissions(administrator=True)
    async def reloadblacklist(self, ctx):
        file = open("Blacklist.txt", "r")
        lines = file.readlines()
        for line in lines:
            line = line.rstrip()
            blacklist.append(line)
        file.close()
        await ctx.send("Done!", delete_after=1)


def setup(bot):
    bot.add_cog(Blacklist(bot))