import discord, asyncio, time
from datetime import datetime
from discord.ext import commands

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, old, new):
        logChannel = discord.utils.get(old.guild.channels, name="mod-logging")
        old_roles = old.roles
        new_roles = new.roles
        removed = []
        added = []
        if old_roles != new_roles:
            embed = discord.Embed(timestamp = datetime.utcnow(), color=0x8934eb)
            embed.set_author(name="Roles updated: %s" % (old), icon_url=new.avatar_url)
            for role in new_roles:
                if role not in old_roles:
                    added.append(role.mention)
            for role in old_roles:
                if role not in new_roles:
                    removed.append(role.mention)

            if removed != []:
                embed.add_field(name="Roles Removed", value=", ".join(removed))
            if added != []:
                embed.add_field(name="Roles Added", value=", ".join(added))
            
            
            async for entry in old.guild.audit_logs(limit=1):
                
                if str(entry.action) == "AuditLogAction.member_role_update":
                    if entry.target == new:
                        whoDid = entry.user
                        embed.set_footer(text="Member updated by %s" % (whoDid))
                    else:
                        embed.set_footer(text="Member updated by system")
                else: 
                    embed.set_footer(text="Member updated by system")
            await logChannel.send(embed=embed)
        
        if old.nick != new.nick:
            logChannel = discord.utils.get(old.guild.channels, name="mod-logging")

            embed = discord.Embed(timestamp = datetime.utcnow(), color=0x8934eb)
            embed.set_author(name="Nickname updated: %s" % (new), icon_url=new.avatar_url)
            if str(old.nick) != "None":
                oldnick = old.nick 
            else:
                oldnick = old.name
            embed.add_field(name="Old Nickname", value=oldnick)
            if str(new.nick) != "None":
                newnick = new.nick 
            else:
                newnick = new.name
            embed.add_field(name="New Nickname", value=newnick)
            await logChannel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.content[0] != self.bot.command_prefix:
            logChannel = discord.utils.get(message.guild.channels, name="mod-logging")
            embed = discord.Embed(timestamp = datetime.utcnow(), color=0x8934eb)
            embed.add_field(name="**Content:**", value=message.content, inline=False)
            embed.add_field(name="**Channel:**", value=message.channel.mention)
            embed.set_author(name="Message deleted: %s (%s)" % (message.author, message.author.id), icon_url=message.author.avatar_url)
            
            await logChannel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, old, new):
        if new.content != "" and new.content != old.content:
            logChannel = discord.utils.get(old.guild.channels, name="mod-logging")
            embed = discord.Embed(description="[Jump to message](%s)" % (new.jump_url), color=0x8934eb, timestamp = datetime.utcnow())
            embed.set_author(name="Message edited: %s (%s)" % (old.author, old.author.id), icon_url=old.author.avatar_url)
            if old.content != "":
                embed.add_field(name="**Old Message**: ", value=old.content)
            embed.add_field(name="**New Message**: ", value=new.content)
            embed.add_field(name="**Channel:**", value=new.channel.mention, inline=False)
            
            await logChannel.send(embed=embed)


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        logChannel = discord.utils.get(member.guild.channels, name="mod-logging")
        async for entry in member.guild.audit_logs(limit=1):
            if str(entry.action) == "AuditLogAction.kick" and entry.target == member:
                embed = discord.Embed(title="%s was kicked" % (member), description="**Reason: **%s" % (entry.reason), color=0x8934eb, timestamp = datetime.utcnow())
                embed.set_footer(text="Member kicked by %s" % (entry.user))
                await logChannel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        logChannel = discord.utils.get(guild.channels, name="mod-logging")
        await asyncio.sleep(1)
        async for entry in guild.audit_logs(limit=1):
            embed = discord.Embed(title="%s was banned" % (member), description="**Reason: **%s" % (entry.reason), color=0x8934eb, timestamp = datetime.utcnow())
            embed.set_footer(text="Member banned by %s" % (entry.user))
            await logChannel.send(embed=embed)
 

        
    

def setup(bot):
    bot.add_cog(Logging(bot))