import discord, smtplib
from discord.ext import commands
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

schoolEmail = "@student.hogent.be"
mainServerID = 771394209419624489

class EmailVerification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = discord.utils.get(member.guild, name="verify") 
        em = discord.Embed(title="Welkom %s", description="Om te verifiëren dat jij wel degelijk een HOGENT student bent, gelieve mij een berichtje te sturen met alleen jouw HOGENT email.")
        channel.send(embed=em)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None and not message.author.bot:
            if schoolEmail in message.content:
                await sendVerification(message.content, message.author.id)
                await message.author.send("Je hebt een E-mail ontvangen met een code, gelieve die code terug naar mij door te sturen! (Door de spam filters zal die waarschijnlijk daar staan)")
            elif len(message.content) == 6:
                discordID = message.author.id
                token = str(discordID)[0:3] + str(discordID)[-3:]
                if message.content == token:

                    guild = discord.utils.get(self.bot.guilds, id=mainServerID)
                    member = await guild.fetch_member(discordID)
                    

                    role = discord.utils.get(guild.roles, name="Verified")

                    await member.add_roles(role)
                    await message.author.send("Je bent correct geverifieërd, welkom! :tada:")
                else:
                    await message.author.send("Deze token klopte niet, controleer het even en stuur het opnieuw!")
            else:
                await message.author.send("Dit heb ik niet helemaal begrepen, als je probeert je email te sturen gelieve dan alleen je email te sturen \nProbeer je je code in te geven, gelieve dan alleen je code te sturen!")

async def sendVerification(mailTo, discordID):
    sender_address = 'informatica@verificatie.in-orde.be'
    #region
    sender_pass = '3lS8XabwKNnC9Lt9'
    #endregion
    receiver_address = mailTo
    
    
    token = str(discordID)[0:3] + str(discordID)[-3:]
    email_content = open("email.txt", "r", encoding="utf-8").read() % (token)

    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'HoGent Discord Verificatie'   #The subject line
    message.attach(MIMEText(email_content, 'html'))


    session = smtplib.SMTP('mail.verificatie.in-orde.be', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()

def setup(bot):
    bot.add_cog(EmailVerification(bot))