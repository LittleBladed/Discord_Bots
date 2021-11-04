import discord, sqlite3, re
from discord.ext import commands

conn = sqlite3.connect('Bot.db')
c = conn.cursor()

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reactionrole(self, ctx, channel:discord.TextChannel, messageID, role: discord.Role, emoji):
        await ctx.message.delete()
        message = await channel.fetch_message(messageID)
        
        if ":" in str(emoji):
            emoji = re.search(":(\d.+?)>", emoji)
            emoji = emoji.group(1)
            
            emoji = await ctx.message.guild.fetch_emoji(emoji)
            c.execute("INSERT INTO reactionroles VALUES (?,?,?,?)", (str(channel.id), str(message.id), str(emoji), str(role.id)))
            conn.commit()

            
        else:
            c.execute("INSERT INTO reactionroles VALUES (?,?,?,?)", (channel.id, message.id, emoji, role.id))
            conn.commit()

        embed = discord.Embed(title="Reaction role added")
        embed.add_field(name="Channel", value=channel.mention)
        embed.add_field(name="Message", value="[Jump to message](%s)" % (message.jump_url))
        embed.add_field(name="Role", value=role.mention, inline=False)
        embed.add_field(name="Emoji", value=emoji)
        await message.add_reaction(emoji)
        await ctx.send(embed=embed)

        
        
        

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        guild = self.bot.get_guild(payload.guild_id)
        user = guild.get_member(payload.user_id)
        reaction = payload.emoji

        c.execute("SELECT roleID FROM reactionroles WHERE messageID = ? AND emojiID = ?", (str(message.id), str(reaction)))
        roleid = c.fetchone()
        if str(roleid) != "None" and user != self.bot.user:
            roleid = roleid[0]
            role = discord.utils.get(guild.roles, id=int(roleid))
            await user.add_roles(role)
        
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        guild = self.bot.get_guild(payload.guild_id)
        user = guild.get_member(payload.user_id)
        reaction = payload.emoji

        c.execute("SELECT roleID FROM reactionroles WHERE messageID = ? AND emojiID = ?", (str(message.id), str(reaction)))
        roleid = c.fetchone()
        if str(roleid) != "None" and user != self.bot.user:
            roleid = roleid[0]
            role = discord.utils.get(guild.roles, id=int(roleid))
            await user.remove_roles(role)


def setup(bot):
    bot.add_cog(ReactionRoles(bot))