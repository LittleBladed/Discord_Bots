import discord, sqlite3, re, random
from discord.ext import commands

conn = sqlite3.connect('Bot.db')
c = conn.cursor()

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def new(self, ctx, *, arg = None):
        guild = ctx.guild
        category = discord.utils.get(guild.categories, name='Tickets')
        tickets = discord.utils.get(guild.channels, name= 'tickets')
        tid = tickets.id
        Support = discord.utils.get(guild.roles, name='Support')
        user = self.bot.get_user(ctx.author.id)
        overwrites = {
                        guild.default_role:
                            discord.PermissionOverwrite(read_messages=False),
                        Support:
                            discord.PermissionOverwrite(read_messages=True),
                        user:
                            discord.PermissionOverwrite(read_messages=True),
                        self.bot.user:
                            discord.PermissionOverwrite(read_messages=True, send_messages=True)
                    } 
        channel = ctx.message.channel.name
        if 'tickets' in channel:
            await ctx.message.delete()
            c.execute("UPDATE number SET num = num + 1")
            conn.commit()
            c.execute("SELECT * FROM number ORDER BY num DESC LIMIT 1;")
            numb = str(c.fetchone())
            numbe = re.findall(r'\b\d+\b', numb)
            for item in numbe:
                numbe = item
            conn.commit()
            ticket = await ctx.guild.create_text_channel(f'Ticket-00{numbe}', category=category, overwrites=overwrites)
            createdchannel = discord.utils.get(guild.channels, name=f'ticket-00{numbe}')
            id = createdchannel.id
            au = ctx.message.author
            embed = discord.Embed(title = 'Ticket created', description = f'<#{id}>', colour = 0x42ffff)
            embed.add_field(name = 'Please have patience', value = 'Staff will assist you as soon as possible', inline=False)
            embed.set_footer(text = f'ticket opened by {au}')

            embedd = discord.Embed(title='Ticket created', colour=0x42ffff)
            embedd.add_field(name = 'Ticket tag', value = f'<#{id}>', inline=False)
            embedd.add_field(name="Information", value="%s" % (arg))
            embedd.set_footer(text = f'ticket opened by {au.name}')
            ticketem = discord.Embed(title = 'Please have patience', description = 'Staff will assist you as soon as possible', inline=False, colour=0x42ffff)
            ticketem.add_field(name="Ticket info", value="%s" % (arg))
            loggg = discord.utils.get(ctx.guild.channels, name='ticket-logs')
            await ctx.send(embed=embed, delete_after=600)
            await loggg.send(embed=embedd)
            await ticket.send(embed=ticketem)
        else: 
            embed = discord.Embed(title = 'Command error', description = f'This command can only be used in <#{tid}>', colour = 0x42ffff)
            await ctx.message.delete()
            await ctx.send(embed=embed) 

    @commands.command()
    async def ticketinfo(self, ctx):
        em = discord.Embed(title="**Open a ticket**", description="Type `>new` or react to open a ticket", colour=0x42ffff)
        await ctx.send(embed=em)

    @commands.command()
    async def close(self, ctx, *, reason = None):
        channel = ctx.message.channel.name
        if 'ticket-00' in channel:
            await ctx.message.delete()
            await ctx.channel.delete()
            em = discord.Embed(title="Ticket closed", description="%s" % (channel), colour=0x42ffff)
            em.add_field(name="Reason", value="%s" % (reason))
            em.set_footer(text="Ticket closed by %s" % (ctx.author.name))
            logs = discord.utils.get(ctx.guild.channels, name='ticket-logs')
            await logs.send(embed=em)
        else:
            await ctx.message.delete()
            embed = discord.Embed(title = 'Command error', description = 'This command can only be used in a ticket', colour = 0x42ffff)
            await ctx.send(embed=embed)
        
    @commands.command()
    async def addstaff(self, ctx):
        await ctx.message.delete()
        guild = ctx.guild
        role = discord.utils.get(guild.roles, name="Support")
        channel = ctx.message.channel.name
        if 'ticket-00' in channel:
            await ctx.message.channel.set_permissions(role, read_messages=True, send_messages=True)
            embed = discord.Embed(title='Staff was added to the ticket', colour = 0x42ffff)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title = 'Command error', description = 'This command can only be used in a ticket', colour = 0x42ffff)
            await ctx.send(embed=embed)
    
    @commands.command()
    async def removestaff(self, ctx):
        await ctx.message.delete()
        guild = ctx.guild
        role = discord.utils.get(guild.roles, name="Support")
        channel = ctx.message.channel.name
        if 'ticket-00' in channel:
            await ctx.message.channel.set_permissions(role, read_messages=False, send_messages=False)
            embed = discord.Embed(title='Staff was removed from the ticket', colour = 0x42ffff)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title = 'Command error', description = 'This command can only be used in a ticket', colour = 0x42ffff)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def closeAll(self, ctx):
        await ctx.message.delete()
        for channel in ctx.guild.channels:
            if 'ticket-00' in channel.name:
                await channel.delete()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def resetcounter(self, ctx):
        await ctx.message.delete()
        c.execute("UPDATE number SET num = 0")
        conn.commit()

    @commands.command()
    async def add(self, ctx, member: discord.Member):
        if "ticket-00" in ctx.message.channel.name:
            await ctx.message.delete()
            embed = discord.Embed(title='Member added', description=f"{member.mention} was added to the support ticket", colour = 0x42ffff)
            await ctx.message.channel.set_permissions(member, read_messages=True, send_messages=True)
            await ctx.send(embed=embed)

    @commands.command()
    async def remove(self, ctx, member: discord.Member):
        if "ticket-00" in ctx.message.channel.name:
            await ctx.message.delete()
            embed = discord.Embed(title='Member removed', description=f"{member.mention} was removed from the support ticket", colour = 0x42ffff)
            await ctx.message.channel.set_permissions(member, read_messages=False, send_messages=False)
            await ctx.send(embed=embed)

    @commands.command()
    async def suggest(self, ctx, *, sug:str):
        await ctx.message.delete()
        Id = random.randint(1,1000)
        user = ctx.message.author
        c.execute("INSERT INTO Sugestions VALUES (?, ?)", (Id, sug))
        conn.commit()
        guild = ctx.guild
        thanksug = discord.Embed(title="Suggestion made", description="Thanks for your suggestion. We appreciate any kind of feedback/tips", colour = 0x42ffff)
        channel = discord.utils.get(guild.channels, name='suggestion-logs')
        sugmade = discord.Embed(title='Suggestion made', colour = 0x42ffff)
        sugmade.add_field(name='A user has made the following suggestion:', value=f'{sug}')
        sugmade.set_footer(text=f'Suggestion made by {user}')
        await channel.send(embed=sugmade)
        await ctx.send(embed=thanksug)




def setup(bot): 
    bot.add_cog(Tickets(bot))