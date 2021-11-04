import discord, sqlite3, requests, json
from discord.ext import commands

conn = sqlite3.connect('Bot.db')
c = conn.cursor()
def read_key():
    with open('CoinbaseAPI.txt', 'r') as f:
            lines = f.readlines()
            return lines[0].strip()
        
API_KEY = read_key()

class Credits(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @commands.command()
    async def check(self, ctx, code):
        await ctx.message.delete()
        status = checkStatus(code)
        price = checkPrice(code)   
        em = discord.Embed(title="Checkout", colour=0x42ffff)
        if not 'error' in status:
            c.execute("SELECT * FROM creditcodes WHERE code=?", (code, ))
            used = c.fetchone()
            if used != None:
                used = used[1]
            if used != 'yes' or used == None:                
                if status == 'NEW':
                    em.add_field(name="Status: NEW", value="The checkout has been created, but not paid yet")
                if status == "EXPIRED":
                    em.add_field(name="Status: EXPIRED", value="The checkout was created, but was not paid in time")
                if status == 'PENDING' or status == 'COMPLETED':
                    em.add_field(name="Status: COMPLETE", value="Thanks for your purchase, your credits have been added!")
                    c.execute("SELECT * FROM credits WHERE userID=?", (ctx.message.author.id, ))
                    check = c.fetchone()       
                    creds = price
                    if check == None:
                        c.execute("INSERT INTO credits VALUES (?, ?, ?)", (ctx.message.author.name, ctx.message.author.id, creds))
                    else:
                        c.execute("UPDATE credits SET credits = credits + ? WHERE userID=?", (creds, ctx.message.author.id))
                    c.execute("INSERT INTO creditcodes VALUES (?, ?)", (code, 'yes', ))
                    conn.commit()
            else:
                em.add_field(name="Status: ALREADY USED", value="This code was already redeemed")
        if 'error' in status:
            em.add_field(name="Status: NOT FOUND", value="This checkout does not exist, please make sure you spelled it right")
        await ctx.send(embed=em)

    @commands.command()
    async def buy(self, ctx, creds):
        await ctx.message.delete()
        price = int(creds)/10
        checkout = createCheckout(price)
        em = discord.Embed(title="CLICK HERE TO PURCHASE", url="https://commerce.coinbase.com/checkout/%s" % (checkout), colour = 0x42ffff)
        em.add_field(name="You are purchasing:", value="%s credits!" % (creds))
        em.set_thumbnail(url=ctx.message.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command()
    async def balance(self, ctx, user: discord.Member = None): 
        await ctx.message.delete()
        if user == None:
            c.execute("SELECT * FROM credits WHERE userID=?", (ctx.message.author.id, ))
            balance = c.fetchone()
            if balance != None:
                balance = balance[2]
            else:
                balance = 0
            em = discord.Embed(title="Balance for %s" % (ctx.message.author.name), description="%s credits" % (balance), colour=0x42ffff)
            em.set_thumbnail(url=ctx.message.author.avatar_url)
        if user != None:
            c.execute("SELECT * FROM credits WHERE userID=?", (user.id, ))
            balance = c.fetchone()
            if balance != None:
                balance = balance[2]
            else:
                balance = 0
            em = discord.Embed(title="Balance for %s" % (user.name), description="%s credits" % (balance), colour=0x42ffff)
            em.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=em)


    @commands.command()
    @commands.has_role("Owner")
    async def changeBalance(self, ctx, user: discord.Member, creds):
        await ctx.message.delete()
        c.execute("SELECT * FROM credits WHERE userID=?", (user.id, ))
        check = c.fetchone()
        if check == None:
            c.execute("INSERT INTO credits VALUES (?, ?, ?)", (user.name, user.id, creds))
        else:
            c.execute("UPDATE credits SET credits = credits + ? WHERE userID=?", (creds, user.id))
        conn.commit()

        c.execute("SELECT * FROM credits WHERE userID=?", (user.id, ))
        balance = c.fetchone()    
        balance = balance[2]

        em = discord.Embed(title="Balance for %s" % (user.name), description="%s credits" % (balance), colour=0x42ffff)
        em.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=em)

    @commands.command()
    async def transfer(self, ctx, user: discord.Member, amount: int):
        if amount > 0:
            c.execute("SELECT * FROM credits WHERE userID=?", (ctx.message.author.id, ))
            balance = c.fetchone()
            if balance != None:
                balance = balance[2]
            else:
                balance = 0  
            if balance >= amount:
                c.execute("SELECT * FROM credits WHERE userID=?", (user.id, ))
                balance2 = c.fetchone()
                if balance2 != None:
                    balance2 = balance2[2]
                else:
                    balance2 = 0  
                newbalance = balance - amount
                newbalance2 = balance2 + amount

                c.execute("SELECT * FROM credits WHERE userID=?", (ctx.message.author.id, ))
                check = c.fetchone()
                if check == None:
                    c.execute("INSERT INTO credits VALUES (?, ?, ?)", (ctx.message.author.name, ctx.message.author.id, newbalance))
                else:
                    c.execute("UPDATE credits SET credits = ? WHERE userID=?", (newbalance, ctx.message.author.id))

                c.execute("SELECT * FROM credits WHERE userID=?", (user.id, ))
                check = c.fetchone()
                if check == None:
                    c.execute("INSERT INTO credits VALUES (?, ?, ?)", (user.name, user.id, newbalance2))
                else:
                    c.execute("UPDATE credits SET credits = ? WHERE userID=?", (newbalance2, user.id))
                conn.commit()
                em = discord.Embed(title="Transfer complete", colour=0x42ffff)
                em.add_field(name="New balance for %s" % (ctx.message.author.name), value="%s credits" % (newbalance), inline=False)
                em.add_field(name="New balance for %s" % (user.name), value="%s credits" % (newbalance2))
                await ctx.send(embed=em)
            else:
                await ctx.send("You don't have enough balance for this!", delete_after=10)
        else:
            await ctx.send("You can't transfer a negative balance!", delete_after=10)


def checkStatus(code):
    headers = {'X-CC-Api-Key': API_KEY, 'X-CC-Version': '2018-03-22'}
    r = requests.get('https://api.commerce.coinbase.com/charges/%s' % (code), headers=headers)
    data = r.json()
    if 'data' in data:
        data = data['data']['timeline']
        data = str(data)          
    if "'PENDING'" in data:
        data = 'PENDING'
    if "'CONFIRMED'" in data:
        data = 'CONFIRMED'    
    if "'EXPIRED'" in data:
        data = 'EXPIRED'
    if data != "EXPIRED" and data != "CONFIRMED" and data != "PENDING":
        data = "NEW" 
    return data

def checkPrice(code):
    headers = {'X-CC-Api-Key': API_KEY, 'X-CC-Version': '2018-03-22'}
    r = requests.get('https://api.commerce.coinbase.com/charges/%s' % (code), headers=headers)
    data = r.json()
    if 'data' in data:
        data = data['data']['pricing']['local']['amount']
        data = float(data) * 10
    return data

def createCheckout(price):
    headers = {'X-CC-Api-Key': API_KEY, 'X-CC-Version': '2018-03-22', 'Content-Type': 'application/json'}
    total = int(price) * 10
    data = '''{\n"name": "%s credits",\n
        "description": "Credits are a great way to spend on our site",\n
        "local_price": {\n"amount": "%s.00",\n
        "currency": "USD"\n},\n
        "pricing_type": "fixed_price",\n
        "requested_info": ["name"]\n}''' % (total, price)
    r = requests.post('https://api.commerce.coinbase.com/checkouts', headers=headers, data=data)
    data = r.json()
    data = data['data']['id']
    return data

def setup(bot): 
    bot.add_cog(Credits(bot))