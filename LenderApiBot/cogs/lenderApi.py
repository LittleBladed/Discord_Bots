import discord
import requests
from discord.ext import commands

class LenderAPI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def lender(self, ctx, steamID: str):
        req = requests.get("http://api.steampowered.com/IPlayerService/IsPlayingSharedGame/v0001/?key=0209147DA0F52049EDE422B01D8748A3&steamid=%s&appid_playing=4000&format=json" % (steamID))
        if req.text == '{"response":{"lender_steamid":"0"}}':
            em = discord.Embed(title="Lender API Lookup", description="This person is either not online or does not have a family shared account")
            em.set_footer(text="Made by LittleBladed#5515")
        await ctx.send(embed=em)



def setup(bot):
    bot.add_cog(LenderAPI(bot))