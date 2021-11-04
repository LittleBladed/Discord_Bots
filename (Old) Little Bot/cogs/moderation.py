import discord, sqlite3, random
from discord.ext import commands

conn = sqlite3.connect('Bot.db')
c = conn.cursor()

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member:discord.Member, *, reason : str = None):
        await ctx.message.delete()
        await ctx.guild.ban(member, reason=reason)
        if reason != None:
            embed = discord.Embed(title=f'{member} was banned for ``{reason}``!', colour = 0x42ffff)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=f'{member} was banned!', colour = 0x42ffff)
            await ctx.send(embed=embed)
            


    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason : str = None):
        await ctx.message.delete()
        await ctx.guild.kick(member, reason=reason)
        if reason != None:
            embed = discord.Embed(title=f'{member} was kicked for ``{reason}``!', colour = 0x42ffff)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=f'{member} was kicked!', colour = 0x42ffff)
            await ctx.send(embed=embed)


    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, limit: int):
        count = 0
        async for message in ctx.channel.history(limit=limit):
            await message.delete()
            count += 1
        await ctx.channel.purge(limit=limit)
        await ctx.send(':tada: **%s Messages removed**' % (count), delete_after=10) 

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, user: discord.Member, *, reason=None):
        await ctx.message.delete()
        if reason == None:
            c.execute("SELECT * FROM warnsinfo WHERE userID = ?", (user.id, ))
            warns = c.fetchall()
            if len(warns) > 20:
                embed1 = discord.Embed()
                embed2 = discord.Embed()
                embed1.set_author(name="Warnings for %s: Page 1" % (user.name), icon_url=user.avatar_url)
                embed2.set_author(name="Warnings for %s: Page 2" % (user.name), icon_url=user.avatar_url)
                counter = 0
 
                for rawwarn in warns:
                    warnedby = rawwarn[0]
                    username = rawwarn[1]
                    reason = rawwarn[2]
                    userID = rawwarn[3]
                    warnID = rawwarn[4]
                    
                    if counter < 20:
                        counter = counter + 1
                        embed1.add_field(name="Warning %s: by %s" % (counter, warnedby), value="``%s`` \n Id: %s \n" % (reason, warnID), inline=False)
                    else:
                        counter = counter + 1
                        embed2.add_field(name="Warning %s: by %s" % (counter, warnedby), value="``%s`` \n Id: %s \n" % (reason, warnID), inline=False)

                await ctx.send(embed=embed1)
                await ctx.send(embed=embed2)

            else:
                embed = discord.Embed()
                embed.set_author(name="Warnings for %s" % (user.name), icon_url=user.avatar_url)
                counter = 0
                for rawwarn in warns:
                    warnedby = rawwarn[0]
                    username = rawwarn[1]
                    reason = rawwarn[2]
                    userID = rawwarn[3]
                    warnID = rawwarn[4]
                    embed.add_field(name="Warning %s: by %s" % (counter, warnedby), value="``%s`` \n Id: %s \n" % (reason, warnID), inline=False)
                    counter = counter + 1
                await ctx.send(embed=embed)
        else:
            c.execute("INSERT INTO warnsinfo VALUES (?,?,?,?,?)", (ctx.message.author.name, user.name, reason, user.id, random.randint(1,10000)))
            conn.commit()

            embed = discord.Embed(title="Reason:", description=reason)
            embed.set_author(name="Warned %s" % (user), icon_url=user.avatar_url)

            notifembed = discord.Embed(title="Je bent gewaarschuwd in %s" % (ctx.message.guild.name))
            notifembed.add_field(name="Reden:", value=reason)
            await ctx.send(embed=embed)
            await user.send(embed=notifembed)
            
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removewarn(self, ctx, user: discord.Member, ID):
        await ctx.message.delete()
        c.execute("SELECT * FROM warnsinfo WHERE warnnumber = ? AND userID = ?", (ID, user.id))
        test = c.fetchone()
        if str(test) == "None":
            embed = discord.Embed(title="Warning with ID ``%s`` not found for ``%s``" % (ID, user))
            await ctx.send(embed=embed)
        else:
            c.execute("DELETE FROM warnsinfo WHERE warnnumber = ? AND userID = ?", (str(ID), user.id))
            conn.commit()
            embed = discord.Embed(title="Warning with ID ``%s`` removed for ``%s``" % (ID, user))
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Moderation(bot))