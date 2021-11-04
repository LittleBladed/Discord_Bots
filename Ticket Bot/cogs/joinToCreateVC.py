import discord, json, asyncio
from discord.ext import commands

config = json.load(open("config.json", "r+"))
personalVCJson = json.load(open("personalVC.json", "r+"))

class JoinToCreateVC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def hasPerms(self, userID, channelID: str):
        if channelID in personalVCJson:
            if personalVCJson[channelID]["creator"] == userID or userID in personalVCJson[channelID]["mods"]:
                return True

    def isOwner(self, userID, channelID):
         if channelID in personalVCJson:
            if personalVCJson[channelID]["creator"] == userID:
                return True
    

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel:
            if after.channel.name == config["joinToCreateVC"]:
                channel = await member.guild.create_voice_channel(name=member.name, category=after.channel.category, position = 99)
                await member.move_to(channel)

                personalVCJson[channel.id] =  {"creator": member.id, "mods": []}
                json.dump(personalVCJson, open("personalVC.json", "w"), indent=4)

        if before.channel:
            if self.isOwner(member.id, before.channel.id):
                personalVCJson.pop(before.channel.id, None)
                json.dump(personalVCJson, open("personalVC.json", "w"), indent=4)
                await before.channel.delete()
                
                
    
    @commands.group(invoke_without_command=True)
    async def channel(self, ctx):
        em = discord.Embed(title="Incorrect Usage", description="Please use `%shelp channel` for more info!" % self.bot.command_prefix, color=discord.Colour.red())
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        msg = await ctx.send(embed=em)
        await asyncio.sleep(10)
        await ctx.message.delete()
        await msg.delete()
    
    @channel.command(description="Delete personal VC")
    async def delete(self, ctx):
        if ctx.message.author.voice: 
            if self.hasPerms(ctx.message.author.id, ctx.message.author.voice.channel.id):
                await ctx.message.author.move_to(None)
                em = discord.Embed(title="Personal Channel", description="Personal VC successfully deleted!", color=discord.Colour.blurple())
                em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                msg = await ctx.send(embed=em)
            else:
                em = discord.Embed(title="Personal Channel", description="You can only do this in a channel you're promoted in!", color=discord.Colour.red())
                em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                msg = await ctx.send(embed=em)
        else:
            em = discord.Embed(title="Personal Channel", description="You can only do this while in a channel you're promoted in!", color=discord.Colour.red())
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            msg = await ctx.send(embed=em)
        await asyncio.sleep(10)
        await ctx.message.delete()
        await msg.delete()

    @channel.command(description="Lock personal Voice Channel")
    async def lock(self, ctx):
        if ctx.message.author.voice: 
            if self.hasPerms(ctx.message.author.id, ctx.message.author.voice.channel.id):
                await ctx.message.author.voice.channel.set_permissions(ctx.guild.default_role, connect=False)
                await ctx.message.author.voice.channel.set_permissions(ctx.message.author, connect=True)
                em = discord.Embed(title="Personal Channel", description="Personal VC is now locked!", color=discord.Colour.blurple())
                em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                msg = await ctx.send(embed=em)
            else:
                em = discord.Embed(title="Personal Channel", description="You can only do this in a channel you're promoted in!", color=discord.Colour.red())
                em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                msg = await ctx.send(embed=em)
        else:
            em = discord.Embed(title="Personal Channel", description="You can only do this while in a channel you're promoted in!", color=discord.Colour.red())
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            msg = await ctx.send(embed=em)
        await asyncio.sleep(10)
        await ctx.message.delete()
        await msg.delete()

    @channel.command(description="Open your personal Voice Channel after being locked")
    async def open(self, ctx):
        if ctx.message.author.voice: 
            if self.hasPerms(ctx.message.author.id, ctx.message.author.voice.channel.id):
                await ctx.message.author.voice.channel.set_permissions(ctx.guild.default_role, connect=None)
                em = discord.Embed(title="Personal Channel", description="Personal VC is now open!", color=discord.Colour.blurple())
                em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                msg =await ctx.send(embed=em)
            else:
                em = discord.Embed(title="Personal Channel", description="You can only do this in a channel you're promoted in!", color=discord.Colour.red())
                em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                msg = await ctx.send(embed=em)
        else:
            em = discord.Embed(title="Personal Channel", description="You can only do this while in a channel you're promoted in!", color=discord.Colour.red())
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            msg = await ctx.send(embed=em)
        await asyncio.sleep(10)
        await ctx.message.delete()
        await msg.delete()

    @channel.command(description="Guide to create a personal Voice Channel")
    async def create(self, ctx):
        channel = discord.utils.get(ctx.guild.channels, name=config["joinToCreateVC"])

        em = discord.Embed(title="Personal Channel", description="To create a personal VC, simply join <#%s>!" % (channel.id), color=discord.Colour.blurple())
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        msg = await ctx.send(embed=em)
        await asyncio.sleep(10)
        await ctx.message.delete()
        await msg.delete()

    @channel.command(description="Add a member to your private Voice Channel")
    async def add(self, ctx, member: discord.Member):
        if ctx.message.author.voice: 
            if self.hasPerms(ctx.message.author.id, ctx.message.author.voice.channel.id):
                await ctx.message.author.voice.channel.set_permissions(member, connect=True)
                em = discord.Embed(title="Personal Channel", description="Added %s to your personal VC!" % (member.name), color=discord.Colour.blurple())
                em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                msg = await ctx.send(embed=em)
            else:
                em = discord.Embed(title="Personal Channel", description="You can only do this in a channel you're promoted in!", color=discord.Colour.red())
                em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                msg = await ctx.send(embed=em)
        else:
            em = discord.Embed(title="Personal Channel", description="You can only do this while in a channel you're promoted in!", color=discord.Colour.red())
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            msg = await ctx.send(embed=em)
        await asyncio.sleep(10)
        await ctx.message.delete()
        await msg.delete()
    
    @channel.command(description="Remove a member from your Voice Channel")
    async def remove(self, ctx, member: discord.Member):
        if ctx.message.author.voice: 
            if self.hasPerms(ctx.message.author.id, ctx.message.author.voice.channel.id):
                await ctx.message.author.voice.channel.set_permissions(member, connect=False)
                em = discord.Embed(title="Personal Channel", description="Removed %s from your personal VC!" % (member.name), color=discord.Colour.blurple())
                em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                msg = await ctx.send(embed=em)
            else:
                em = discord.Embed(title="Personal Channel", description="You can only do this in a channel you're promoted in!", color=discord.Colour.red())
                em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                msg = await ctx.send(embed=em)
        else:
            em = discord.Embed(title="Personal Channel", description="You can only do this while in a channel you're promoted in!", color=discord.Colour.red())
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            msg = await ctx.send(embed=em)
        await asyncio.sleep(10)
        await ctx.message.delete()
        await msg.delete()

    @channel.command(description="Rename your personal Voice Channel")
    async def rename(self, ctx, newName):
        if ctx.message.author.voice: 
            if self.hasPerms(ctx.message.author.id, ctx.message.author.voice.channel.id):
                await ctx.message.author.voice.channel.edit(name=newName)
                em = discord.Embed(title="Personal Channel", description="Renamed your personal VC to %s!" % (newName), color=discord.Colour.blurple())
                em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                msg = await ctx.send(embed=em)
            else:
                em = discord.Embed(title="Personal Channel", description="You can only do this in a channel you're promoted in!", color=discord.Colour.red())
                em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                msg = await ctx.send(embed=em)
        else:
            em = discord.Embed(title="Personal Channel", description="You can only do this while in a channel you're promoted in!", color=discord.Colour.red())
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            msg = await ctx.send(embed=em)
        await asyncio.sleep(10)
        await ctx.message.delete()
        await msg.delete()

    @channel.command(description="Kick a member from your personal Voice Channel")
    async def kick(self, ctx, member: discord.Member):
        if ctx.message.author.voice: 
            if self.hasPerms(ctx.message.author.id, ctx.message.author.voice.channel.id) and member.voice.channel == ctx.author.voice.channel:
                await member.move_to(None)
                em = discord.Embed(title="Personal Channel", description="Kicked %s from your personal VC!" % (member.name), color=discord.Colour.blurple())
                em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                msg = await ctx.send(embed=em)
            else:
                em = discord.Embed(title="Personal Channel", description="You can only do this in a channel you're promoted in!", color=discord.Colour.red())
                em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                msg = await ctx.send(embed=em)
        else:
            em = discord.Embed(title="Personal Channel", description="You can only do this while in a channel you're promoted in!", color=discord.Colour.red())
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            msg = await ctx.send(embed=em)
        await asyncio.sleep(10)
        await ctx.message.delete()
        await msg.delete()
    
    @channel.command(description="Promote a member in your personal Voice Channel so they can do moderating actions within it")
    async def promote(self, ctx, member: discord.Member):
        if ctx.message.author.voice: 
            if self.isOwner(ctx.message.author.id, ctx.message.author.voice.channel.id):
                
                personalVCJson[ctx.message.author.voice.channel.id]["mods"].append(member.id)
                json.dump(personalVCJson, open("personalVC.json", "w"), indent=4)
                
                em = discord.Embed(title="Personal Channel", description="Promoted %s in your personal VC!" % (member.name), color=discord.Colour.blurple())
                em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                msg = await ctx.send(embed=em)
            else:
                em = discord.Embed(title="Personal Channel", description="You can only do this in a channel you're promoted in!", color=discord.Colour.red())
                em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                msg = await ctx.send(embed=em)
        else:
            em = discord.Embed(title="Personal Channel", description="You can only do this while in a channel you're promoted in!", color=discord.Colour.red())
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            msg = await ctx.send(embed=em)
        await asyncio.sleep(10)
        await ctx.message.delete()
        await msg.delete()
    
        
    

def setup(bot):
    bot.add_cog(JoinToCreateVC(bot))