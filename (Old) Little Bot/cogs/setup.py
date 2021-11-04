import discord, asyncio
from discord.ext import commands

class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logChannelName = "mod-logging"
    
    @commands.command()
    async def setup(self, ctx, arg = None):
        if arg == None:

            # Logging
            check = discord.utils.get(ctx.guild.channels, name=self.logChannelName)
            if check == None:
                overwrites = {ctx.guild.default_role:discord.PermissionOverwrite(read_messages=False)}
                await ctx.guild.create_text_channel(name=self.logChannelName, overwrites=overwrites)
            else:
                await ctx.send("Logging was already set up")
            
            #Tickets
            checkChannel = discord.utils.get(ctx.guild.channels, name="tickets")
            checkLogChannel = discord.utils.get(ctx.guild.channels, name="ticket-logs")
            checkCategory = discord.utils.get(ctx.guild.categories, name="Tickets")
            checkRole = discord.utils.get(ctx.guild.roles, name="Support")
            
            if checkCategory == None:
                await ctx.guild.create_category(name="Tickets")
            
            category = discord.utils.get(ctx.guild.categories, name="Tickets")
            await asyncio.sleep(1)
            if checkChannel == None:
                await ctx.guild.create_text_channel(name="tickets", category = category)

            if checkLogChannel == None:
                await ctx.guild.create_text_channel(name="ticket-logs", category = category)
            
            if checkRole == None:
                await ctx.guild.create_role(name="Support")


            

def setup(bot):
    bot.add_cog(Setup(bot))