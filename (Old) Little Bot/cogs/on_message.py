import discord
from discord.ext import commands
from discord.enums import ChannelType, MessageType




class OnMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot




   

def setup(bot):
    bot.add_cog(OnMessage(bot))