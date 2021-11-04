import discord, json
from discord.ext import commands

config = json.load(open("config.json", "r+"))
prefix = config["prefix"]
class OnCommandError(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.BadArgument) or isinstance(error, commands.ArgumentParsingError):
            await ctx.message.delete()
            em = discord.Embed(title="**An error occurred**", description="You badly used 1 or more arguments, use %shelp *command* to see correct usage!" % (prefix), color=discord.Colour.blurple())
            em.set_footer(text=f"Use {prefix}help *command* for more info!")
            await ctx.send(embed=em, delete_after=10)           
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.delete()
            em = discord.Embed(title="**An error occurred**", description="You are missing 1 or more arguments, use %shelp *command* to see correct usage!" % (prefix), color=discord.Colour.blurple())
            em.set_footer(text=f"Use {prefix}help *command* for more info!")
            await ctx.send(embed=em, delete_after=10)      
        elif isinstance(error, commands.MissingPermissions):
            await ctx.message.delete()
            em = discord.Embed(title="**An error occurred**", description="%s" % ("You don't have the correct role or permissions to do this!"), color=discord.Colour.blurple())
            em.set_footer(text=f"Use {prefix}help *command* for more info!")
            await ctx.send(embed=em, delete_after=10)    
        elif isinstance(error, commands.CheckFailure):
            await ctx.message.delete()
            em = discord.Embed(title="**An error occurred**", description="%s" % ("You don't have the correct role to do this!"), color=discord.Colour.blurple())
            em.set_footer(text=f"Use {prefix}help *command* for more info!")
            await ctx.send(embed=em, delete_after=10)   
        elif isinstance(error, commands.BotMissingPermissions) or isinstance(error, discord.Forbidden):
            await ctx.message.delete()
            em = discord.Embed(title="**An error occurred**", description="%s" % ("It appears I am missing the right permissions to perform this command (on this user)."), color=discord.Colour.blurple())
            em.set_footer(text=f"Use {prefix}help *command* for more info!")
            await ctx.send(embed=em, delete_after=10)   
        elif isinstance(error, commands.CommandNotFound):
            await ctx.message.delete()
            await ctx.send(f'This command was not found, use `{prefix}help` for a list of commands', delete_after=5)
        else: 
            await ctx.message.delete()
            em = discord.Embed(title="**An unknown error occurred**", description="%s" % ("Please contact the server owner / bot developer with the following error: \n %s!") % (error), color=discord.Colour.blurple())
            em.add_field(name="Message that triggered error:", value=ctx.message.content)
            em.set_footer(text=f"Use {prefix}help *command* for more info!")
            await ctx.send(embed=em, delete_after=10)   

def setup(bot):
    bot.add_cog(OnCommandError(bot))

