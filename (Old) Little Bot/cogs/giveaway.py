import discord, asyncio, random
from discord.ext import commands

givelist = []

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        global givelist
        if user != self.bot.user:       
            if "GIVEAWAY" in reaction.message.clean_content:
                givelist.append(user)
            else:
                pass
        else:
            pass
    
    @commands.command()
    @commands.has_role('Owner')
    async def giveaway(self, ctx, time: int, *, item):
        global givelist
        await ctx.message.delete()
        chan = discord.utils.get(ctx.guild.channels, name='giveaways')
        time = round(time/60, 2)
        scale = 'hours'
        if time < 1:
            time = time * 60
            scale = 'minutes'
        elif time >= 24:
            time = time / 24
            scale = 'days'
        em = discord.Embed(title='%s' % (item), description='React to enter', colour=0x42ffff)
        em.set_footer(text='Giveaway ends in %s %s' % (time, scale))
        
        message = await chan.send('🎉**GIVEAWAY STARTED**🎉', embed=em)
        await message.add_reaction('🎉')
        await asyncio.sleep(time)
           
        winner = random.choice(givelist).mention
        await chan.send('%s you won the giveaway for %s' % (winner, item))
        givelist.clear()

def setup(bot):
    bot.add_cog(Giveaway(bot))