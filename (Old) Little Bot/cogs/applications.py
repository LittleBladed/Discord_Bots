import discord, sqlite3
from discord.ext import commands

conn = sqlite3.connect('Bot.db')
c = conn.cursor()

class Applications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def apply(self, ctx):
        author = ctx.message.author
        await ctx.message.delete()
        c.execute("SELECT * FROM apps WHERE type=?", ('mod', ))
        statu = c.fetchone()
        status = statu[0]
        if status == 'open':
            sureembed = discord.Embed(title="Are you sure you want to apply for moderator?", colour=0x42ffff)
            sureembed.set_footer(text="Please respond with yes or no, anything else will cancel")
            await author.send(embed=sureembed)
            check = await self.bot.wait_for('message', check=lambda message: message.author == ctx.message.author)
            if 'yes' in check.content or 'Yes' in check.content:
                emb = discord.Embed(title='Moderator application: %s' % (author.name), description="""As a moderator, you're supposed to keep the server clean""", colour=0x42ffff)
                emaskage = discord.Embed(title="Question 1", description="How old are you?", colour=0x42ffff)
                await author.send(embed=emb)
                await author.send(embed=emaskage)

                age = await self.bot.wait_for('message', check=lambda message: message.author == ctx.message.author)
                emaskmotivation = discord.Embed(title="Question 2", description="Why would you be a good moderator?", colour=0x42ffff)
                await author.send(embed=emaskmotivation)
            
                motivation = await self.bot.wait_for('message', check=lambda message: message.author == ctx.message.author)
                emaskaccept = discord.Embed(title="Question 3", description="Do you agree that we can remove your role, without needing to give you any reason?", colour=0x42ffff)
                await author.send(embed=emaskaccept)

                accept = await self.bot.wait_for('message', check=lambda message: message.author == ctx.message.author)
                emend = discord.Embed(title="End of the application", description="Thank you for your application, you'll get a reply ASAP", colour=0x42ffff)
                await author.send(embed=emend)

                app = discord.Embed(title="New moderator application", description="From %s" % (author), colour=0x42ffff)
                app.add_field(name="Age", value="%s" % (age.content))
                app.add_field(name="Motivation", value="%s" % (motivation.content))
                app.add_field(name="Agree to the terms", value="%s" % (accept.content))
                mod = discord.utils.get(ctx.guild.channels, name="applications")
                await mod.send(embed=app)
            elif 'no' in check.content or 'No' in check.content:
                await author.send('Application canceled')
            else:
                await author.send('Not yes or no received. Please try the apply command again.')
        elif status == 'closed':
            await author.send("Sorry, applications are closed at this time")

    @commands.command()
    @commands.has_role('Owner')
    async def openapps(self, ctx):
        await ctx.message.delete()
        c.execute("SELECT * FROM apps WHERE type=?", ('mod', ))
        statu = c.fetchone()
        status = statu[0]
        if status == 'open':
            await ctx.send("The apps are already open", delete_after=10)
        elif status == 'dicht':
            c.execute("UPDATE apps SET status = ? WHERE type=?", ('open', 'mod', ))
            conn.commit()
            await ctx.send("The apps are now open", delete_after=10)

    @commands.command()
    @commands.has_role('Owner')
    async def closeapps(self, ctx):
        await ctx.message.delete()
        c.execute("SELECT * FROM apps WHERE type=?", ('mod', ))
        statu = c.fetchone()
        status = statu[0]
        if status == 'closed':
            await ctx.send("The apps are already closed", delete_after=10)
        elif status == 'open':
            c.execute("UPDATE apps SET status = ? WHERE type=?", ('closed', 'mod', ))
            conn.commit()
            await ctx.send("The apps are now closed", delete_after=10)



def setup(bot): 
    bot.add_cog(Applications(bot))
