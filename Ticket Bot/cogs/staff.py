import discord, json, asyncio
from discord.colour import Colour
from discord.ext import commands, tasks
from datetime import datetime, timedelta

config = json.load(open("config.json", "r+"))
punishmentLog = json.load(open("punishments.json", "r+"))

class Staff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        

    def canKick():
        def predicate(ctx):
            for role in (config["canBanRoles"] + config["canKickRoles"]):
                role = discord.utils.get(ctx.guild.roles, name=role)
                if role in ctx.message.author.roles:
                    return True
            return False
        return commands.check(predicate)
    
    def canBan():
        def predicate(ctx):
            for role in config["canBanRoles"]:
                role = discord.utils.get(ctx.guild.roles, name=role)
                if role in ctx.message.author.roles:
                    return True
            return False
        return commands.check(predicate)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.checkForExpired.start()

    @tasks.loop(minutes=1)
    async def checkForExpired(self):
        await self.CheckForExpiredPunishments()

    @commands.command(description="Bans a member from the discord server")
    @canBan()
    async def ban(self, ctx, member:discord.Member, *, reason : str = None):
        await self.sendAppeal(member, "banned", reason, ctx.guild)
        await ctx.guild.ban(member, reason=reason)
        em = discord.Embed(title="Member Banned", description="You have succesfully banned %s!" % (member), color=discord.Colour.red())
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        if reason != None:
            em.add_field(name="Reason", value=reason,inline=False)

        msg = await ctx.send(embed=em)
        

        em = discord.Embed(title="Member Banned", color=discord.Colour.red())
        em.add_field(name="Member:",  value=member,inline=False)
        em.add_field(name="Banned by:", value=ctx.author,inline=False)
        if member.avatar is not None: 
            em.set_thumbnail(url=member.avatar.url)
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        
        if reason != None:
            em.add_field(name="Reason", value=reason,inline=False)
        
        channel = discord.utils.get(ctx.guild.channels, name=config["moderationLogChannel"])
        await channel.send(embed=em)

        logPunishment(ctx.message.author, member, "Ban", reason, "Never")

        await asyncio.sleep(10)
        await ctx.message.delete()
        await msg.delete()
    
    @commands.command(description="Kicks a member from the discord server")
    @canKick()
    async def kick(self, ctx, member:discord.Member, *, reason : str = None):
        await self.sendAppeal(member, "kicked", reason, ctx.guild)
        await ctx.guild.kick(member, reason=reason)
        em = discord.Embed(title="Member Kicked", description="You have succesfully kicked %s!" % (member), color=discord.Colour.red())
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)

        if reason != None:
            em.add_field(name="Reason", value=reason,inline=False)

        msg = await ctx.send(embed=em)

        em = discord.Embed(title="Member Kicked", color=discord.Colour.red())
        em.add_field(name="Member:",  value=member,inline=False)
        em.add_field(name="Kicked by:", value=ctx.author,inline=False)
        if member.avatar is not None: 
            em.set_thumbnail(url=member.avatar.url)
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        if reason != None:
            em.add_field(name="Reason", value=reason,inline=False)
        
        channel = discord.utils.get(ctx.guild.channels, name=config["moderationLogChannel"])
        await channel.send(embed=em)

        logPunishment(ctx.message.author, member, "Kick", reason, "Never")

        await asyncio.sleep(10)
        await ctx.message.delete()
        await msg.delete()

    @commands.command(description="Tempbans a member from the discord server (length = time in minutes)")
    @canBan()
    async def tempban(self, ctx, member:discord.Member, length: int, *, reason : str = None):
        await ctx.message.delete()
        await self.sendAppeal(member, "tempbanned", reason, ctx.guild)
        await ctx.guild.ban(member, reason=reason)
        em = discord.Embed(title="Member Banned", description="You have succesfully tempbanned %s!" % (member), color=discord.Colour.red())
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        if reason != None:
            em.add_field(name="Reason", value=reason,inline=False)

        msg = await ctx.send(embed=em)
        
        expires = datetime.strftime(datetime.now()+timedelta(minutes=length), "%y-%m-%d %H:%M:%S")

        em = discord.Embed(title="Member Tempbanned", description="%s was banned (%s)" % (member, member.id), color=discord.Colour.red())
        em.add_field(name="Banned by:", value=ctx.author,inline=False)
        em.add_field(name="Expires On:", value=expires,inline=False)
        if member.avatar is not None: 
            em.set_thumbnail(url=member.avatar.url)
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        if reason != None:
            em.add_field(name="Reason", value=reason,inline=False)
        
        channel = discord.utils.get(ctx.guild.channels, name=config["moderationLogChannel"])
        await channel.send(embed=em)

        logPunishment(ctx.message.author, member, "Ban", reason, expires)

        await asyncio.sleep(10)
        await ctx.message.delete()
        await msg.delete()

    @commands.command(description="Mutes a member in the discord server")
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member:discord.Member):
        role = discord.utils.get(ctx.guild.roles, name=config["mutedRole"])
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(role, send_messages=False)
        await member.add_roles(role)

        em = discord.Embed(title="Member Muted", description="You have succesfully muted %s!" % (member), color=discord.Colour.red())
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)

        msg = await ctx.send(embed=em)

        em = discord.Embed(title="Member Muted", color=discord.Colour.red())
        em.add_field(name="Member:",  value=member,inline=False)
        em.add_field(name="Muted by:", value=ctx.author,inline=False)
        if member.avatar is not None: 
            em.set_thumbnail(url=member.avatar.url)
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        
        channel = discord.utils.get(ctx.guild.channels, name=config["moderationLogChannel"])
        await channel.send(embed=em)

        logPunishment(ctx.message.author, member, "Mute", "None", "Never")

        await asyncio.sleep(10)
        await ctx.message.delete()
        await msg.delete()
    
    @commands.command(description="Unmutes a member in the discord server")
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, member:discord.Member):
        role = discord.utils.get(ctx.guild.roles, name=config["mutedRole"])
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(role, send_messages=False)

        await member.remove_roles(role)

        em = discord.Embed(title="Member Unuted", description="You have succesfully unmuted %s!" % (member), color=discord.Colour.red())
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)

        msg = await ctx.send(embed=em)

        em = discord.Embed(title="Member Unmuted", color=discord.Colour.red())
        em.add_field(name="Member:",  value=member,inline=False)
        em.add_field(name="Unmuted by:", value=ctx.author,inline=False)
        if member.avatar is not None: 
            em.set_thumbnail(url=member.avatar.url)
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        
        channel = discord.utils.get(ctx.guild.channels, name=config["moderationLogChannel"])
        await channel.send(embed=em)

        await asyncio.sleep(10)
        await ctx.message.delete()
        await msg.delete()
    
    @commands.command(description="Tempmutes a member in the discord server (length = time in minutes)")
    @commands.has_permissions(manage_messages=True)
    async def tempmute(self, ctx, member:discord.Member, length: int):
        role = discord.utils.get(ctx.guild.roles, name=config["mutedRole"])
        await member.add_roles(role)

        em = discord.Embed(title="Member Tempmuted", description="You have succesfully muted %s!" % (member), color=discord.Colour.red())
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)

        msg = await ctx.send(embed=em)
        expires = datetime.strftime(datetime.now()+timedelta(minutes=length), "%y-%m-%d %H:%M:%S")


        em = discord.Embed(title="Member Tempmuted", color=discord.Colour.red())
        em.add_field(name="Member:",  value=member,inline=False)
        em.add_field(name="Muted by:", value=ctx.author,inline=False)
        em.add_field(name="Expires On:", value=expires,inline=False)
        if member.avatar is not None: 
            em.set_thumbnail(url=member.avatar.url)
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        
        channel = discord.utils.get(ctx.guild.channels, name=config["moderationLogChannel"])
        await channel.send(embed=em)

        logPunishment(ctx.message.author, member, "Mute", "None", expires)

        await asyncio.sleep(10)
        await ctx.message.delete()
        await msg.delete()

    @commands.command(description="Warns a member")
    @commands.has_any_role()
    async def warn(self, ctx, member:discord.Member, *, reason: str):
        em = discord.Embed(title="Member Warned", description="You have succesfully warned %s!" % (member), color=discord.Colour.red())
        em.add_field(name="Reason:", value=reason,inline=False)
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)

        msg = await ctx.send(embed=em)


        em = discord.Embed(title="Member Warned", color=discord.Colour.red())
        em.add_field(name="Member:",  value=member,inline=False)
        em.add_field(name="Warned by:", value=ctx.author)
        em.add_field(name="Warning:", value=reason)
        if member.avatar is not None: 
            em.set_thumbnail(url=member.avatar.url)
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        
        channel = discord.utils.get(ctx.guild.channels, name=config["moderationLogChannel"])
        await channel.send(embed=em)

        logPunishment(ctx.message.author, member, "Warn", reason, "Never")
        await asyncio.sleep(10)
        await ctx.message.delete()
        await msg.delete()

    @commands.command(description="Shows punishment history")
    @commands.has_permissions(manage_messages=True)
    async def history(self, ctx, member:discord.Member):
        if str(member.id) in punishmentLog:
            i = 1
            for punishment in punishmentLog[str(member.id)]:
                em = discord.Embed(title="Punishment for `%s`: #%s" % (member, i), color=discord.Colour.blurple())
                em.add_field(name="Punishment Type: ", value=punishment["punishment"],inline=False)
                em.add_field(name="Staff Member: ", value=punishment["staffmember"],inline=False)
                em.add_field(name="Reason: ", value=punishment["reason"],inline=False)
                em.add_field(name="Expires At: ", value=punishment["expires_at"],inline=False)
                if member.avatar is not None: 
                    em.set_thumbnail(url=member.avatar.url)
                em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                await ctx.send(embed=em)
                i += 1
        else:
            em = discord.Embed(title="Punishment History", description="This user doesn't have any past punishments!", color=discord.Colour.blurple())
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            if member.avatar is not None: 
                    em.set_thumbnail(url=member.avatar.url)
            
            await ctx.send(embed=em)

    
    @commands.command(description="Delete X amount of messages, `>purge all` for everything")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, limit):
        if limit == "All":
            await ctx.channel.delete()
            await ctx.guild.create_text_channel(name=ctx.channel.name, overwrites=ctx.channel.overwrites, topic=ctx.channel.topic, category=ctx.channel.category)
        else:
            count = 0
            async for message in ctx.channel.history(limit=int(limit)):
                await message.delete()
                count += 1
            await ctx.channel.purge(limit=int(limit))
            await ctx.send(':tada: **%s Messages removed**' % (count), delete_after=3) 
    
    @commands.command(description="Locks a channel, only staff can speak")
    @canBan()
    async def lock(self, ctx):
        staffrole = discord.utils.get(ctx.guild.roles, name=config["staffRole"])
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.channel.set_permissions(staffrole, send_messages=True)
        em = discord.Embed(title="Channel Lock", description="This channel is now locked!", color=discord.Colour.blurple())
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        await ctx.send(embed=em)
    
    @commands.command(description="Unlocks a channel after being locked")
    @canBan()
    async def unlock(self, ctx):
        staffrole = discord.utils.get(ctx.guild.roles, name=config["staffRole"])
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=None)
        em = discord.Embed(title="Channel Unlock", description="This channel is now unlocked!", color=discord.Colour.blurple())
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        msg = await ctx.send(embed=em)
        await asyncio.sleep(10)
        await ctx.message.delete()
        await msg.delete()

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        async for entry in member.guild.audit_logs(limit=1):
            if str(entry.action) == "AuditLogAction.kick" and entry.target == member and entry.user != self.bot.user:
                em = discord.Embed(title="Member Kicked (Rigth Click)", color=discord.Colour.red())
                em.add_field(name="Member:",  value=member,inline=False)
                em.add_field(name="Kicked by:", value=entry.user,inline=False)
                em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                if entry.reason != None:
                    em.add_field(name="Reason", value=entry.reason,inline=False)
                
                channel = discord.utils.get(member.guild.channels, name=config["moderationLogChannel"])
                await channel.send(embed=em)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        await asyncio.sleep(1)
        async for entry in guild.audit_logs(limit=1):
            if entry.user != self.bot.user:
                em = discord.Embed(title="Member Banned (Right Click)", color=discord.Colour.red())
                em.add_field(name="Member:",  value=member,inline=False)
                em.add_field(name="Banned by:", value=entry.user,inline=False)
                em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                if entry.reason != None:
                    em.add_field(name="Reason", value=entry.reason,inline=False)
                
                channel = discord.utils.get(guild.channels, name=config["moderationLogChannel"])
                await channel.send(embed=em)
    
    
                    



    async def CheckForExpiredPunishments(self):
        for key in punishmentLog:
            i = 0
            for punishment in punishmentLog[key]:
                if not punishment["expires_at"] == "Expired" and not punishment["expires_at"] == "Never":
                    check = datetime.strptime(punishment["expires_at"], "%y-%m-%d %H:%M:%S")
                    if check:
                        if datetime.now() > check:
                            punishmentLog[key][i]["expires_at"] = "Expired"
                            guild = await self.bot.fetch_guild(punishment["guildID"])
                            if punishment["punishment"] == "Ban":
                                user = await self.bot.fetch_user(key)
                                await guild.unban(user)
                            elif punishment["punishment"] == "Mute": 
                                role = discord.utils.get(guild.roles, name=config["mutedRole"])
                                member = await guild.fetch_member(key)
                                if member:
                                    await member.remove_roles(role)
                        i += 1
        json.dump(punishmentLog, open("punishments.json", "w"), indent=4, default=str)

    async def sendAppeal(self, user, type, reason, guild):
        em = discord.Embed(title="You have been %s from %s" % (type, guild), color=discord.Color.red())
        em.add_field(name="Reason: ", value=reason,inline=False)
        em.add_field(name="Appealing this punishment", value="If you wish to appeal this punishment, please join our appeal server at: \n%s" % config["appealServerInvite"],inline=False)
        await user.send(embed=em)
    



def logPunishment(staff, user, punishment, reason, expires):
    if not str(user.id) in punishmentLog:
        punishmentLog[str(user.id)] = []
    punishmentLog[str(user.id)].append({"guildID": user.guild.id, "username":user.name, "staffmember": staff.name, "punishment":punishment, "reason": reason, "expires_at": expires})
    json.dump(punishmentLog, open("punishments.json", "w"), indent=4, default=str)




def setup(bot):
    bot.add_cog(Staff(bot))