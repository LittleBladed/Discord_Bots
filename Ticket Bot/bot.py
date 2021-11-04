import discord, os, json, asyncio
from discord.ext import commands

config = json.load(open("config.json", "r+"))

bot = commands.Bot(config["prefix"], self_bot=False, intents=discord.Intents.all())

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension('cogs.%s' % (filename[:-3]))


def read_token():
    with open('Bot.txt', 'r') as f:
            lines = f.readlines()
            return lines[0].strip()


token = read_token()


class MyNewHelp(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = discord.Embed(description=page)
            await destination.send(embed=emby)

bot.help_command = MyNewHelp()

@bot.event
async def on_message(message):
    if not str(message.channel.type) == "private" and not message.author == bot.user:
        staffrole = discord.utils.get(message.guild.roles, name=config["staffRole"])
        botCommandChannel = discord.utils.get(message.guild.channels, name=config["botChannel"])
        if message.content.startswith(bot.command_prefix):
            if message.channel != botCommandChannel:
                if not staffrole in message.author.roles:
                    em = discord.Embed(title="Command Error", description="This can only be used in <#%s>!" % (botCommandChannel.id), color=discord.Colour.red())
                    em.set_footer(text=bot.user.name, icon_url=bot.user.avatar.url)
                    msg = await message.channel.send(embed=em)
                    asyncio.sleep(3)
                    await msg.delete()
                    await message.delete()
                    return
        
    await bot.process_commands(message)

@bot.command(description="Reloads the bot")
async def reload(ctx, cog = "All"):
    await ctx.message.delete()
    if cog == "All":
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and not "func" in filename:
                bot.unload_extension('cogs.%s' % (filename[:-3]))
                bot.load_extension('cogs.%s' % (filename[:-3]))
        await ctx.send('Reloaded all cogs', delete_after=5)
    else:
        for filename in os.listdir('./cogs'):                      
            if filename.endswith('.py') and not "func" in filename:
                filename = filename[:-3] 
                if filename == cog:
                    bot.unload_extension('cogs.%s' % (filename))
                    bot.load_extension('cogs.%s' % (filename))
                    await ctx.send('Reloaded %s' % (filename), delete_after=5)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')



bot.run(token)