import discord, os
from datetime import datetime
from discord.ext import commands

u1 = '--------------------------------'
u2 = '\nError: unicodeException Raised'
u3 = u1 + u2
e1 = '--------------------------------'
e2 = '\nError: Exception Raised'
e3 = e1 + e2

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        global u3
        global e3
        time = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')

        if not os.path.exists(f'Logs/{message.guild.name}'):
            print('no bro')
            os.mkdir(f'Logs/{message.guild.name}')

        v1 =  '--------------------------------'    
        v2 = f'\nDate & Time: {time}'                                                                                                                                             
        v3 = f'\nServer: {message.guild.name}' 
        v4 = f'\nUsername: {message.author.name}'  
        v5 = f'\nChannel: {message.channel.name}'       
        v6 = f'\nServer Id: {message.guild.id}'                                                                                                 
        v7 = f'\nUsername Id: {message.author.id}'                                                                                                  
        v8 = f'\nChannel Id: {message.channel.id}'  
        v9 = f'\nMessage Id: {message.id}'                       
        v10 = f'\nMessage Url: {message.jump_url}'                                                                                          
        v11 = f'\nMessage: {message.clean_content}' 
        v12 = f'\nAttachments: {message.attachments}' 
        v13 = f'\nEmbeds: {message.embeds}'                                                                                     
        v14 = v1 + v2 + v3 + v4 + v5 + v6 + v7 + v8 + v9 + v10 + v11 + v12 + v13

        try:                                                                                                                   
            print(v14)
                                                                                                
        except:                                                                                                              
                print(e3)                                                                                                     
        try:
            file = open(f'Logs\{message.guild.name}\{message.channel.name}.txt', 'a', encoding="utf-8")
            file.write(f'{v14}\n')
            file.close                                                                                                       
        except UnicodeError:                                                                                                   
                print(u3)                                                                                                      
                file = open(f'Logs\{message.guild.name}\{message.channel.name}.txt', 'a')                                                                  
                file.write(f'{u3}\n')                                                                                               
                file.close                                                                                                      
        except:                                                                                                              
                print(e3)                                                                                                   
                file = open(f'Logs\{message.guild.name}\{message.channel.name}.txt', 'a')                                                                  
                file.write(f'{e3}\n')                                                                                               
                file.close
        
    @commands.command()
    @commands.has_role('Support')
    async def transcript(self, ctx, arg = ""):
        if arg == "":
            await ctx.message.delete()
            await ctx.send(file=discord.File(f'Logs/{ctx.message.guild.name}/{ctx.message.channel.name}.txt'))
        elif arg != "":
            await ctx.message.delete()
            await ctx.send(file=discord.File(f'Logs/{ctx.message.guild.name}/{arg}.txt'))


def setup(bot):
    bot.add_cog(Logs(bot))