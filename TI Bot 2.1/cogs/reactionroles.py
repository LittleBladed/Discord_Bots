import discord, sqlite3, re
from discord.ext import commands

conn = sqlite3.connect('Bot.db')
c = conn.cursor()

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        messageID = payload.message_id
        emoji = payload.emoji

        roleID = get_roleID(emoji, messageID)
        if roleID != None:
            userID = payload.user_id

            guild = discord.utils.get(self.bot.guilds, id=payload.guild_id)
            member = await guild.fetch_member(userID)
            role = guild.get_role(int(roleID))

            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        messageID = payload.message_id
        emoji = payload.emoji

        roleID = get_roleID(emoji, messageID)
        if roleID != None:
            userID = payload.user_id

            guild = discord.utils.get(self.bot.guilds, id=payload.guild_id)
            member = await guild.fetch_member(userID)
            role = guild.get_role(int(roleID))

            await member.remove_roles(role)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def createRR(self, ctx, channel: discord.TextChannel, messageID, role: discord.Role, emoji):
        c.execute("INSERT INTO rolereactions VALUES(?,?,?)", (emoji, messageID, role.id))
        conn.commit()

        msg = await channel.fetch_message(messageID)
        await msg.add_reaction(emoji)
        await ctx.send("Done! %s will now give the %s role" % (emoji, role))

def setup(bot):
    bot.add_cog(ReactionRoles(bot))

def get_roleID(emoji, messageID):
    c.execute("SELECT roleID FROM rolereactions WHERE emoji = ? AND messageID = ?", (str(emoji), messageID))
    out = c.fetchone()
    if out != None:

        return out[0]
    else: 
        return None