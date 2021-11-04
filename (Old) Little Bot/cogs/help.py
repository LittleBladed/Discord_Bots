import discord, sqlite3
from discord.ext import commands

conn = sqlite3.connect('Bot.db')
c = conn.cursor()

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, arg = None):
        await ctx.message.delete()
        if arg == None:
            em = discord.Embed(title="Little Bot | help", description="The prefix we use is `>`", colour=0x42ffff)
            c.execute("SELECT * FROM help WHERE category = ?", ("Moderation", ))
            command = c.fetchall()
            commands = []
            for i in command:
                name = i[0]
                commands.append('%s' % (name)) 
            mod = ', '.join(commands)        

            c.execute("SELECT * FROM help WHERE category = ?", ("Tickets", ))
            command = c.fetchall()
            commands = []
            for i in command:
                name = i[0]
                commands.append('%s' % (name)) 
            tickets = ', '.join(commands)     

            c.execute("SELECT * FROM help WHERE category = ?", ("Credits", ))
            command = c.fetchall()
            commands = []
            for i in command:
                name = i[0]
                commands.append('%s' % (name)) 
            credits = ', '.join(commands)     


            c.execute("SELECT * FROM help WHERE category = ?", ("Owner", ))
            command = c.fetchall()
            commands = []
            for i in command:
                name = i[0]
                commands.append('%s' % (name)) 
            owner = ', '.join(commands)   

            c.execute("SELECT * FROM help WHERE category = ?", ("Other", ))
            command = c.fetchall()
            commands = []
            for i in command:
                name = i[0]
                commands.append('%s' % (name)) 
            other = ', '.join(commands)     

            em.add_field(name="**Moderation commands**", value=mod, inline=False)
            em.add_field(name="**Ticket commands**", value=tickets, inline=False)
            em.add_field(name="**Credits commands**", value=credits, inline=False)
            em.add_field(name="**Owner commands**", value=owner, inline=False)
            em.add_field(name="**Other commands**", value=other, inline=False)


            await ctx.send(embed=em)
        elif arg != None:
            code = arg
            c.execute("SELECT * FROM help WHERE code=?", (code, ))
            row = c.fetchone()
            des = row[1]
            usage = row[2]
            em = discord.Embed(title='More info on the **%s** command' % (code), description='%s' % (des), colour=0x42ffff)
            em.add_field(name='**Correct usage**', value='%s' % (usage))
            await ctx.send(embed=em)

    @commands.command()
    async def listCommands(self, ctx):
        await ctx.message.delete()
        array = []
        commands = c.execute("SELECT code FROM help ORDER BY code ASC")
        for i in commands:
            command = i[0]
            command = '%s' % (command)
            array.append('- %s' % (command))
        commands = '\n'.join(array)

        em = discord.Embed(title='**AVAILABLE COMMANDS**', colour=0x42ffff, description=commands)
        await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Help(bot))