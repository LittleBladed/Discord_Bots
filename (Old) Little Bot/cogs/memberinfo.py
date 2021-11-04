import discord
from discord.ext import commands


class MemberInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        

    @commands.command()
    async def whois(self, ctx, member:discord.Member):
        
        embed = discord.Embed(title="WhoIs Lookup for: %s (%s)" % (member, member.id), color=0x8934eb)
        embed.add_field(name="**Joined at**", value=member.joined_at)
        embed.add_field(name="**Nickname**", value=member.nick)
        rolesl = []
        for role in member.roles:
            if role.name != "@everyone":
                rolesl.append(role.mention)
                roles = ', '.join(rolesl)
        embed.add_field(name="**Roles**", value=roles, inline=False)
        embed.add_field(name="**Account created**", value=member.created_at)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text="Lookup requested by %s" % (ctx.author))
        await ctx.send(embed=embed)
            


def setup(bot):
    bot.add_cog(MemberInfo(bot))