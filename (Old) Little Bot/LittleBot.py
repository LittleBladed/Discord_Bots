import discord, os
from discord.ext import commands, tasks
import itertools


bot = commands.Bot(">", self_bot=False, help_command=None)
bot.remove_command("help")

statuslist = ['>', '>h', '>he', '>hel', '>help', '>', '>n', '>ne', '>new']
status = itertools.cycle(statuslist)


def read_token():
    with open('Bot.txt', 'r') as f:
            lines = f.readlines()
            return lines[0].strip()

token = read_token()

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension('cogs.%s' % (filename[:-3]))
        print(filename)

@bot.command()
async def reload(ctx, cog = "All"):
    await ctx.message.delete()
    if cog == "All":
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                bot.unload_extension('cogs.%s' % (filename[:-3]))
                bot.load_extension('cogs.%s' % (filename[:-3]))
        await ctx.send('Reloaded all cogs', delete_after=5)
    else:
        for filename in os.listdir('./cogs'):                      
            if filename.endswith('.py'):
                filename = filename[:-3] 
                if filename == cog:
                    bot.unload_extension('cogs.%s' % (filename))
                    bot.load_extension('cogs.%s' % (filename))
                    await ctx.send('Reloaded %s' % (filename), delete_after=5)
@bot.command()
async def unload(ctx, arg):
    bot.unload_extension(arg)
    await ctx.send('unloaded %s' % (arg), delete_after=5)

@bot.command()
async def load(ctx, cog):
    for filename in os.listdir('./cogs'):                      
            if filename.endswith('.py'):
                filename = filename[:-3] 
                if filename == cog:
                    bot.load_extension('cogs.%s' % (filename))
                    await ctx.send('loaded %s' % (filename), delete_after=5)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Game('>help | >new'))






    


        

        

      


    



        

      
    





   


        

bot.run(token, bot=True)