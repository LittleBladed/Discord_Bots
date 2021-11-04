import discord, sqlite3
from discord.ext import commands
from discord import Webhook, RequestsWebhookAdapter


conn = sqlite3.connect('Bot.db')
c = conn.cursor()

class AlternatePersona(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def createAlt(self, ctx, name, avatar = None):

        c.execute("SELECT * FROM alternatePersonas WHERE realDiscordId = ?", (str(ctx.message.author.id), ))
        check = c.fetchone()
        if check != None:
            embed = discord.Embed(description="You already have an alternate persona!")
            embed.set_author(name="Command failed", icon_url=ctx.message.author.avatar_url)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description="Your alternate persona has been created!")
            embed.set_author(name="Alternate persona created!", icon_url=ctx.message.author.avatar_url)
            if avatar == None:
                c.execute("INSERT INTO alternatePersonas VALUES (?,?,?)", (str(ctx.message.author.id), name, "None"))          
                conn.commit()
                embed.add_field(name="**Name**", value=name)
                embed.add_field(name="**Avatar**", value="None, set this using " + self.bot.command_prefix + "setPersonaAvatar <discord URL to avatar>")
            else:
                c.execute("INSERT INTO alternatePersonas VALUES (?,?,?)", (str(ctx.message.author.id), name, avatar))          
                conn.commit()
                embed.add_field(name="**Name**", value=name)
                embed.add_field(name="**Avatar**", value="See thumbnail")
                embed.set_thumbnail(url=avatar)

            test = await ctx.channel.webhooks()
            if test == []:
                await ctx.message.channel.create_webhook(name="alternatePersonas")
                test = await ctx.channel.webhooks()

            webhook = test[0]
            
            if avatar == None:
                await webhook.send(embed=embed, username=name)
            else:
                await webhook.send(embed=embed, username=name, avatar_url=avatar)
            

    @commands.command()
    async def alt(self, ctx, *, text):
        await ctx.message.delete()
        test = await ctx.channel.webhooks()
        if test == []:
            await ctx.message.channel.create_webhook(name="alternatePersonas")
            test = await ctx.channel.webhooks()

        webhook = test[0]

        c.execute("SELECT personaName FROM alternatePersonas WHERE realDiscordId = ?", (str(ctx.message.author.id), ))
        name = c.fetchone()

        if name == None:
            await ctx.send("You do not have an alternate persona yet")
            await ctx.send("Create one using " + self.bot.command_prefix + "createAlt <name> [avatar_url]")
        else:
            name = str(name)
            name = name.replace("'", "")
            name = name.strip('][').strip('()').strip(',')

            

            c.execute("SELECT personaAvatar FROM alternatePersonas WHERE realDiscordId = ?", (str(ctx.message.author.id), ))
            avatar = c.fetchone()

            if avatar != None:
                avatar = str(avatar)
                avatar = avatar.replace("'", "")
                avatar = avatar.strip('][').strip('()').strip(',')
                
                await webhook.send(text, username=name, avatar_url=avatar)
            else:
                await webhook.send(text, username=name)

    @alt.error
    async def alt_error(self, ctx, error):
        print(error)
        

    @commands.command()
    async def setPersonaName(self, ctx, name):
        c.execute("UPDATE alternatePersonas SET personaName = ?", (name,))
        conn.commit()
        await ctx.send("Your persona's name has been updated to %s" % (name))

    @commands.command()
    async def setPersonaAvatar(self, ctx, avatar):
        
        embed = discord.Embed(title="Your persona's avatar has been updated!")
        embed.set_thumbnail(url=avatar)
        await ctx.send(embed=embed)
        c.execute("UPDATE alternatePersonas SET personaAvatar = ? WHERE realDiscordId = ?", (avatar, str(ctx.message.author.id)))
        conn.commit()

    @commands.command()
    async def removeAlt(self, ctx):

        c.execute("DELETE FROM alternatePersonas WHERE realDiscordId = ?", (str(ctx.message.author.id), ))
        conn.commit()

        embed = discord.Embed(title="Your persona avatar has been deleted!")
        embed.set_thumbnail(url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)

        

    @setPersonaAvatar.error
    async def setPersonaAvatar_error(self, ctx, error):
        if "50035" in str(error):
            await ctx.send("This link is malformed, please make sure it is correct", delete_after=5)
    
    @createAlt.error
    async def createAlt_error(self, ctx, error):
        if "50035" in str(error):
            await ctx.send("This link is malformed, please update it with a correct link using " + self.bot.command_prefix + "setPersonaAvatar <discord URL to avatar>", delete_after=5)



def setup(bot):
    bot.add_cog(AlternatePersona(bot))