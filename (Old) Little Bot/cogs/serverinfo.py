import discord
from discord.ext import commands

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def rules(self, ctx):
        em = discord.Embed(title="Server guidelines", description=""" :one: No advertising nowhere, we aren't a marketplace
        :two: No spamming in chat or you will be muted
        :three: No form of any NSFW content in this server
        :four: Make a ticket in <#627178797653032981> for requesting a bot
        :five: Make your suggestions to the staff team in <#627178799749922843>
        :six: Enjoy your stay""", colour=0x42ffff)
        await ctx.send(embed=em)

    @commands.command()
    async def payment(self, ctx):
        em = discord.Embed(title="Payment system", description="""We use our own payment system, credits.
        100 credits = 10$
        This is how you buy them:

        :one: Use the command ``>buy <amount>``, that will create a checkout.

        :two: Click the link in the embed and complete the checkout.

        :three: Once completed, look at the end of your link from coinbase, you will see a code. F.E. ``https://commerce.coinbase.com/charges/85Y2WCMP``
        In this case, the code is ``85Y2WCMP``. 

        :four: Use the command ``>check <your code>``, and your credits will be added to your account.

        :five: Congratz, you now have credits to buy the bot you want!""", colour = 0x42ffff)
        await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(ServerInfo(bot))