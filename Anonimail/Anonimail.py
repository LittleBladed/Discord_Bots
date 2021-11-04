import discord, os
from discord.ext import commands, tasks



bot = commands.Bot(">", self_bot=False, help_command=None, intents=discord.Intents.all())
bot.remove_command("help")


def read_token():
    with open('Bot.txt', 'r') as f:
            lines = f.readlines()
            return lines[0].strip()

token = read_token()

@bot.event
async def on_message(message):
    if str(message.channel.type) == "private":
        guild = discord.utils.get(bot.guilds, name="No Limit Talking")
        channel = discord.utils.get(guild.channels, name="anonieme-vragen")
        em = discord.Embed(title="Nieuw Bericht", description=message.content, color=0x8934eb)
        await channel.send(embed=em)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Game('Stuur mij je anonieme vragen!'))






    


        

        

      


    



        

      
    





   


        

bot.run(token)