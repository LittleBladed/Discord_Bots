import discord, json, asyncio
from discord.errors import HTTPException
from discord.ext import commands
from bot import bot
from datetime import datetime, timedelta


config = json.load(open("config.json", "r+"))
suggestionJson = json.load(open("suggestions.json", "r+"))

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def canBan():
        def predicate(ctx):
            for role in config["canBanRoles"]:
                role = discord.utils.get(ctx.guild.roles, name=role)
                if role in ctx.message.author.roles:
                    return True
            return False
        return commands.check(predicate)

    async def createTicket(categoryName, interaction):
        guild = discord.utils.get(bot.guilds, id=interaction.guild_id)

        support = discord.utils.get(guild.roles, name=config["ticketAccessRole"])
        access = {guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        support: discord.PermissionOverwrite(read_messages=True),
                        bot.user: discord.PermissionOverwrite(read_messages=True)}

        category = discord.utils.get(guild.categories, name = "Unreplied")
        category2 = discord.utils.get(guild.categories, name = "Replied")
        if not category:
            category = await guild.create_category("Unreplied", overwrites=access)

        if not category2:
            await guild.create_category("Replied", overwrites=access)

        access[interaction.user] = discord.PermissionOverwrite(read_messages=True)
        channel = await guild.create_text_channel("%s-%s" % (categoryName, interaction.user.name),  category=category, topic=interaction.user.id, overwrites=access)

        em = discord.Embed(title="Welcome!", description=config["ticketCategories"][categoryName]["message"], color= discord.Colour.blurple())
        await channel.send(embed=em)

        if not config["ticketCategories"][categoryName]["questions"] == []:
            answers = {}
            questions = config["ticketCategories"][categoryName]["questions"]
            em = discord.Embed(title="Ticket Question", color= discord.Colour.blurple())
            em.set_footer(text=bot.user.name, icon_url=bot.user.avatar.url)

            for question in questions:
                answer = await askQuestion(channel, question, answers, interaction.user)
                if not answer == None:
                    answers[question["question"]] = answer
                
            em.title = "Question Responses"
            em.description = "Here are the given responses to the questions"
            for key in answers:
                em.add_field(name=key, value=answers[key], inline=False)
            await channel.send(embed=em)
        return channel


    
    async def createTranscript(self, channel):
        path = "transcripts/%s - %s.txt" % (channel.name, datetime.now().date())
        file = open(path, "w", encoding="utf-8")
        async for msg in channel.history(oldest_first=True):
            file.write("---------------------------------------\n")
            file.write("%s at %s: \nContent: %s \n" % (msg.author, msg.created_at, msg.content))
            if msg.embeds:
                for embed in msg.embeds:
                    file.write("Embed: \nTitle = %s | Description = %s\n" % (embed.title, embed.description))
            if msg.attachments:
                for attached in msg.attachments:
                    filename = "transcripts/downloads/%s - %s" % (datetime.now().date(), attached.filename)
                    await attached.save(filename)
                    file.write("Attachment saved at: %s\n" % (filename))
            file.write("---------------------------------------\n\n")
            
        file.close()
    
        return discord.File(path)
    
    def isBanned(self, id):
        if id in config["ticketBanned"]:
            return True
        else:
            return False

    async def closeTicket(self, channel, closedBy):
        file = await self.createTranscript(channel)
        logChannel = discord.utils.get(channel.guild.channels, name=config["ticketLogChannel"])
        if not logChannel:
            em = discord.Embed(title="Command Error", description="The log channel has not been made! \nCurrent configurated log channel name: %s" % (config["logChannel"]), color=discord.Colour.red())
            await channel.send(embed=em)
            return
        
        em = discord.Embed(title="Ticket Closed - %s" % (channel.name), color= discord.Colour.blurple())
        em.add_field(name="Ticket Creator:", value=await channel.guild.fetch_member(channel.topic), inline=False)
        em.add_field(name="Closed By:", value=closedBy, inline=False)
        em.add_field(name="Transcript", value="Transcript has been attached to this message", inline=False)
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        await logChannel.send(embed=em)
        await logChannel.send(file=file)

        user = await channel.guild.fetch_member(channel.topic)
        
        file = await self.createTranscript(channel)
        await user.send(embed=em)
        await user.send(file=file)

        await channel.delete()


    @commands.group(invoke_without_command=True)
    async def ticket(self, ctx):
        em = discord.Embed(title="Incorrect Usage", description="Please use `%shelp ticket` for more info!" % self.bot.command_prefix, color=discord.Colour.red())
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        msg = await ctx.send(embed=em)
        await asyncio.sleep(10)
        await ctx.message.delete()
        await msg.delete()
    
    @ticket.command(description="Guides you through creating a ticket creating embed")
    @canBan()
    async def createembed(self, ctx):
        categories = list(config["ticketCategories"].keys())
        em = discord.Embed(title="Ticket Creation Tool", description="Let's get you set up! \nWhat category would you like to make a ticket for?", colour=discord.Colour.blurple())
        em.add_field(name="Options", value="%s \n\n or ``new`` to create a new category. \n Send anything else to cancel" % "\n".join(categories))
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        msg = await ctx.send(embed=em)

        response = await self.bot.wait_for('message', check=lambda message: message.author == ctx.message.author)
        await response.delete()

        if response.content in categories:
            category = response.content
        elif response.content == "new":
            em.description = "To create a new category, please edit config.json"
            em.remove_field(0)
            await msg.edit(embed=em)
            return
        else:
            em.description = "This category was not found, cancelling"
            em.remove_field(0)
            await msg.edit(embed=em)
            return
        
        em.description = "Got it! \n The ticket will be in ``%s`` \n\n **What channel would you like the embed to be sent?**" % category
        em.remove_field(0)
        await msg.edit(embed=em)

        response = await self.bot.wait_for('message', check=lambda message: message.author == ctx.message.author)

        channel = discord.utils.get(ctx.guild.channels, name=response.content)

        if not channel:
            channel = discord.utils.get(ctx.guild.channels, id=response.content)
        
        if not channel:
            em.description = "This channel was not found, cancelling"
            em.remove_field(0)
            await msg.edit(embed=em)
            return
        
        

        view = TicketButtons(category)
        view.category = category

        ticketEmbed = discord.Embed(title="Ticket - %s " % category, description=config["ticketCategories"][category]["description"])
        ticketEmbed.add_field(name="Opening a ticket", value="Please click the button below to open a ticket!")
        ticketEmbed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        await channel.send(embed=ticketEmbed, view=view)
        
        
        em.description = "Alright! \n The ticket embed was sent in <#%s>" % channel.id
        await msg.edit(embed=em)
        await asyncio.sleep(10)
        await ctx.message.delete()
        await msg.delete()
    
    @ticket.command(description="Gives you a transcript file from the ticket")
    async def transcript(self, ctx):
        try:
            await ctx.guild.fetch_member(int(ctx.channel.topic))
            em = discord.Embed(title="Please wait", description="Generating Transcript")
            em.set_footer(text=bot.user.name, icon_url=bot.user.avatar.url)
            msg = await ctx.send(embed=em)

            file = await self.createTranscript(ctx.channel)

            em.title = "Transcript Generated"
            em.description = "Please find the transcript attached"
            await msg.edit(embed=em)
            await ctx.send(file=file)
            await ctx.message.delete()
        except HTTPException as err:
            em = discord.Embed(title="Command Error", description="This can only be used in a ticket!", color=discord.Colour.red())
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            msg = await ctx.send(embed=em)
            await asyncio.sleep(10)
            await ctx.message.delete()
            await msg.delete()
    
    @ticket.command(description="Closes a ticket")
    @commands.has_role(config["ticketAccessRole"])
    async def close(self, ctx):
        try:
            await ctx.guild.fetch_member(ctx.channel.topic)
            await self.closeTicket(ctx.channel, ctx.message.author)
        except HTTPException as err:
            em = discord.Embed(title="Command Error", description="This can only be used in a ticket!", color=discord.Colour.red())
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            msg = await ctx.send(embed=em)
            await asyncio.sleep(10)
            await ctx.message.delete()
            await msg.delete()
        
    @ticket.command(description="Ban a user from making tickets")
    @commands.has_role(config["ticketAccessRole"])
    async def ban(self, ctx, member: discord.Member):
        if not self.isBanned(member.id):
            config["ticketBanned"].append(member.id)
            json.dump(config, open("config.json", "w"), indent=4)
            em = discord.Embed(title="Ticket Ban", description="Succesfully banned %s!" % (member), color=discord.Colour.blurple())
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            msg = await ctx.send(embed=em)
            await asyncio.sleep(10)
            await ctx.message.delete()
            await msg.delete()
        else:
            em = discord.Embed(title="Command Error", description="This user is already banned!", color=discord.Colour.red())
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            msg = await ctx.send(embed=em)
            await asyncio.sleep(10)
            await ctx.message.delete()
            await msg.delete()
    
    @ticket.command(description="Unban a user from making tickets")
    @commands.has_role(config["ticketAccessRole"])
    async def unban(self, ctx, member: discord.Member):
        if self.isBanned(member.id):
            config["ticketBanned"].remove(member.id)
            json.dump(config, open("config.json", "w"), indent=4)
            em = discord.Embed(title="Ticket Ban", description="Succesfully unbanned %s!" % (member), color=discord.Colour.blurple())
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            msg = await ctx.send(embed=em)
            await asyncio.sleep(10)
            await ctx.message.delete()
            await msg.delete()
        else:
            em = discord.Embed(title="Command Error", description="This user is not banned!", color=discord.Colour.red())
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            msg = await ctx.send(embed=em)
            await asyncio.sleep(10)
            await ctx.message.delete()
            await msg.delete()

    @ticket.command(description="Change the title of a ticket")
    @commands.has_role(config["ticketAccessRole"])
    async def title(self, ctx, *, newTitle):
        try:
            await ctx.guild.fetch_member(ctx.channel.topic)
            
            await ctx.channel.edit(name=newTitle)
            em = discord.Embed(title="Ticket Title", description="Succesfully edited title to %s!" % (newTitle), color=discord.Colour.blurple())
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            msg = await ctx.send(embed=em)
            await asyncio.sleep(10)
            await ctx.message.delete()
            await msg.delete()

        except HTTPException as err:
            em = discord.Embed(title="Command Error", description="This can only be used in a ticket!", color=discord.Colour.red())
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            msg = await ctx.send(embed=em)
            await asyncio.sleep(10)
            await ctx.message.delete()
            await msg.delete()
    
    @ticket.command(description="Check for inactive tickets")
    @canBan()
    async def inactive(self, ctx):
        count = 0
        channels = []
        for channel in ctx.guild.channels:
            try:
                await ctx.guild.fetch_member(channel.topic)
                async for msg in channel.history(limit=1):
                    if msg.created_at.replace(tzinfo=None) < datetime.now()-timedelta(days=3):
                        count += 1
                        channels.append("<#%s>" % (channel.id))
                        #self.closeTicket(channel, "Inactivity")

            except BaseException as err:
                pass
        
        if len(channels) > 0:
            em = discord.Embed(title="Ticket Inactivity", description="Succesfully found %s inactive tickets!" % (count), color=discord.Colour.blurple())
            em.add_field(name="Inactive Tickets: ", value="\n".join(channels))
        else:
            em = discord.Embed(title="Ticket Inactivity", description="Found 0 inactive tickets!", color=discord.Colour.blurple())
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        await ctx.send(embed=em)


    @ticket.command(description="Add a member to a ticket")
    @commands.has_role(config["ticketAccessRole"])
    async def add(self, ctx, member: discord.Member):
        try:
            await ctx.guild.fetch_member(ctx.channel.topic)
            
            await ctx.channel.set_permissions(member, read_messages=True)
            em = discord.Embed(title="Ticket Members", description="Succesfully added %s to the ticket!" % (member), color=discord.Colour.blurple())
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            msg = await ctx.send(embed=em)
            await asyncio.sleep(10)
            await ctx.message.delete()
            await msg.delete()

        except HTTPException as err:
            em = discord.Embed(title="Command Error", description="This can only be used in a ticket!", color=discord.Colour.red())
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            msg = await ctx.send(embed=em)
            await asyncio.sleep(10)
            await ctx.message.delete()
            await msg.delete()

    @ticket.command(description="Remove a member from a ticket")
    @commands.has_role(config["ticketAccessRole"])
    async def remove(self, ctx, member: discord.Member):
        try:
            await ctx.guild.fetch_member(ctx.channel.topic)
            
            await ctx.channel.set_permissions(member, read_messages=False)
            em = discord.Embed(title="Ticket Members", description="Succesfully removed %s from the ticket!" % (member), color=discord.Colour.blurple())
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            msg = await ctx.send(embed=em)
            await asyncio.sleep(10)
            await ctx.message.delete()
            await msg.delete()

        except HTTPException as err:
            em = discord.Embed(title="Command Error", description="This can only be used in a ticket!", color=discord.Colour.red())
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            msg = await ctx.send(embed=em)
            await asyncio.sleep(10)
            await ctx.message.delete()
            await msg.delete()
    
    @ticket.command(description="Reloads config.json")
    @commands.has_role(config["ticketAccessRole"])
    async def reloadconfig(self, ctx):
        global config
        config = json.load(open("config.json", "r+"))

    @commands.group(invoke_without_command=True)
    async def report(self, ctx):
        channel = discord.utils.get(ctx.guild.channels, name=config["suggestionChannel"])
        em = discord.Embed(title="Incorrect usage", description="To make a report, simple send any message in <#%s>!" % (channel.id), color=discord.Colour.blurple())
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        msg = await ctx.send(embed=em)
        await asyncio.sleep(10)
        await ctx.message.delete()
        await msg.delete()
    
    
    @report.command(description="Sends the suggestion/bug explanation embed")
    @canBan()
    async def embed(self, ctx):
        await ctx.message.delete()
        em = discord.Embed(title="Suggestions / Bug reports", description="Would you like to suggest a new feature or report a found bug?", color=discord.Colour.blurple())
        em.add_field(name="How to report?", value="Just simply type any message here, and I will DM you with some more questions! \n Make sure your Dms are turned on")
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        msg = await ctx.send(embed=em)
        await asyncio.sleep(10)
        await ctx.message.delete()
        await msg.delete()

    @commands.Cog.listener()
    async def on_message(self, message):
        if not str(message.channel.type) == "private" and not message.author == self.bot.user and not message.content.startswith(bot.command_prefix):
            if message.channel.category.name == "Unreplied" or message.channel.category.name == "Replied":
                role = discord.utils.get(message.guild.roles, name=config["ticketAccessRole"])
                if role in message.author.roles:
                    category = discord.utils.get(message.guild.categories, name="Replied")
                    await message.channel.edit(category = category)
                else:
                    category = discord.utils.get(message.guild.categories, name="Unreplied")
                    await message.channel.edit(category = category)

            elif message.channel.name == config["suggestionChannel"]:
                await message.delete()
                em = discord.Embed(title="Suggestion / Bug report", description="I have sent you a DM (make sure they have been enabled)!", color=discord.Colour.blurple())
                em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                await message.channel.send(embed=em, delete_after=10)

                em.description = config["suggestionQuestions"]["message"]
                await message.author.send(embed=em)

                answers = {}
                for question in config["suggestionQuestions"]["questions"]:
                    answer = await askQuestion(message.author, question, answers, message.author)
                    if not answer == None:
                        answers[question["question"]] = answer
                
                id = int(len(suggestionJson)+1)
                em.title = "Bug / Suggestion Report"

                em.description = "Here are the given responses to the questions"
                channel = discord.utils.get(message.guild.channels, name=config["suggestionLogChannel"])
                for key in answers:
                    em.add_field(name=key, value=answers[key], inline=False)
                em.add_field(name="ID:", value=id)
                answers["userID"] = message.author.id
                answers["status"] = "Pending"
                suggestionJson[str(id)] = answers
                json.dump(suggestionJson, open("suggestions.json", "w"), indent=4)
                msg = await channel.send(embed=em)
                await msg.add_reaction("✅")
                await msg.add_reaction("❎")

                em.description = "Thank you for your report! A member of staff will take a look shortly!"
                await message.author.send(embed=em)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if not payload.user_id == self.bot.user.id:
            channel = await self.bot.fetch_channel(payload.channel_id)
            msg = await channel.fetch_message(payload.message_id)
            if msg.embeds:
                if msg.embeds[0].title == "Bug / Suggestion Report" and not discord.utils.get(msg.embeds[0].fields, name="Status:"):
                    id = 0
                    for field in msg.embeds[0].fields:
                        if field.name.startswith("ID"):
                            id = field.value
                    if str(payload.emoji) == "✅":
                        await self.reactToSuggest(id, "accepted", channel.guild, channel)
                        msg.embeds[0].add_field(name="Status: ", value="Accepted")
                        msg.embeds[0].color = discord.Color.green()
                        await msg.edit(embed=msg.embeds[0])
                        await msg.clear_reactions()
                    elif str(payload.emoji) == "❎":
                        await self.reactToSuggest(id, "denied", channel.guild, channel)
                        msg.embeds[0].add_field(name="Status: ", value="Denied")
                        msg.embeds[0].color = discord.Color.red()
                        await msg.edit(embed=msg.embeds[0])
                        await msg.clear_reactions()
                    
    
    async def reactToSuggest(self, ID: str, reaction: str, guild, channel):
        if suggestionJson[ID]:
            suggestionJson[ID]["status"] = reaction
            json.dump(suggestionJson, open("suggestions.json", "w"), indent=4) 
            em = discord.Embed(title="Report %s" % (reaction), description="Successfully %s report with ID: #%s!" % (reaction, ID), color=discord.Colour.blurple())
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            
            await channel.send(embed=em)

            member = await guild.fetch_member(suggestionJson[ID]["userID"])

            em = discord.Embed(title="Report %s" % (reaction), color=discord.Colour.blurple())
            em.description = "Your report with ID: #%s has been %s by a member of staff" % (ID, reaction)
            await member.send(embed=em)
    
        


def setup(bot):
    bot.add_cog(Tickets(bot))

class TicketButtons(discord.ui.View):
    
    def __init__(self, category):
        super().__init__()
        self.category = category


    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.green)
    async def btn(self, button: discord.ui.Button, interaction: discord.Interaction):
        for channel in interaction.guild.text_channels:
            if str(channel.topic) == str(interaction.user.id):
                await interaction.response.send_message("You already have a ticket opened!", ephemeral=True)
                return

        if not interaction.user.id in config["ticketBanned"]:
            em = discord.Embed(title="Ticket Created!")
            await interaction.response.send_message(embed=em, ephemeral=True)

            await Tickets.createTicket(self.category, interaction)
            
            
    
        
        else:
            await interaction.response.send_message("You have been banned from making tickets!", ephemeral=True)
        


async def askQuestion(channel, question, answers, member):
    em = discord.Embed(title="Ticket Question", color= discord.Colour.blurple())
    em.set_footer(text=bot.user.name, icon_url=bot.user.avatar.url)
    if "checkQuestion" in question:
        checkQuestion = question["checkQuestion"]
        checkAnswer = question["checkAnswer"]
        if answers[checkQuestion] == checkAnswer:
            check = True
        else:
            check = False
    else:
        check = True

    if question["type"] == "regular" and check:
        em.description = question["question"]
        await channel.send(embed=em)

        answer = await bot.wait_for('message', check=lambda message: message.author == member)
        return answer.content
    elif question["type"] == "yesno" and check:
        em.description = question["question"]
        msg = await channel.send(embed=em)

        await msg.add_reaction("✅")
        await msg.add_reaction("❎")

        def checkReact(reaction, user):
            return reaction.message == msg and str(reaction.emoji) == '✅' or str(reaction.emoji) == '❎' and user == member

        answer = await bot.wait_for('reaction_add', check=checkReact)
        if str(answer[0]) == "✅":
            answer = "Yes"
        elif str(answer[0]) == "❎":
            answer = "No"
        return answer

    elif question["type"] == "multiplechoice" and check:
        choicesList = []
        numbers = {1:"1️⃣", 2:"2️⃣",3:"3️⃣",4:"4️⃣",5:"5️⃣",6:"6️⃣",7:"7️⃣",8:"8️⃣",9:"9️⃣",10:"🔟"}
        indexes = {"1️⃣": 0, "2️⃣": 1, "3️⃣":2, "4️⃣":3, "5️⃣":4, "6️⃣":5, "7️⃣":6, "8️⃣":7, "9️⃣":8, "🔟":9}

        i = 1
        for choice in question["choices"]:
            choicesList.append(numbers[i] + ": "+ choice)
            i += 1
        

        em.description = question["question"] + "\n\n %s" % "\n".join(choicesList)
        msg = await channel.send(embed=em)

        for y in range(i-1):
            await msg.add_reaction(numbers[y+1])

        def checkReact(reaction, user):
            return reaction.message == msg  and user == member

        answer = await bot.wait_for('reaction_add', check=checkReact)
        answer = question["choices"][indexes[str(answer[0])]]
        return answer
    else:
        return None