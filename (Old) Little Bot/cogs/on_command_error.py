import discord
from discord.ext import commands

class OnCommandError(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.message.delete()
            em = discord.Embed(title="**An error occurred**", description="%s" % (error), colour = 0x42ffff)
            em.set_footer(text="Use >help *command* for more info!")
            await ctx.send(embed=em, delete_after=10)           
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.delete()
            em = discord.Embed(title="**An error occurred**", description="%s" % (error), colour = 0x42ffff)
            em.set_footer(text="Use >help *command* for more info!")
            await ctx.send(embed=em, delete_after=10)      
        elif isinstance(error, commands.MissingPermissions):
            await ctx.message.delete()
            em = discord.Embed(title="**An error occurred**", description="%s" % (error), colour = 0x42ffff)
            em.set_footer(text="Use >help *command* for more info!")
            await ctx.send(embed=em, delete_after=10)    
        elif isinstance(error, commands.CommandNotFound):
            await ctx.message.delete()
            await ctx.send('This command was not found, use `>help` for a list of commands', delete_after=5)
        else:
            print(error)

def setup(bot):
    bot.add_cog(OnCommandError(bot))

