import database
import random
import discord
from discord.commands import Option
from discord.ui import Select, View

database = database.database()
bot = discord.Bot()
print("Initiated Database")

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

def ErrorEmbed(user, message, footer=False):
    embed = discord.Embed(
        title="Error",
        description=message,
        color=discord.Colour.red(), # Pycord provides a class with default colors you can choose from
    )
    embed.set_author(name=user.name, icon_url=user.display_avatar)
    embed.set_thumbnail(url=user.display_avatar)
    if footer:
        embed.set_footer(text=footer)

    return embed # Send the embed with some text

def GreenEmbed(user, title, description, footer=False):
    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Colour.green(), # Pycord provides a class with default colors you can choose from
    )
    embed.set_author(name=user.name, icon_url=user.display_avatar)
    embed.set_thumbnail(url=user.display_avatar)
    if footer:
        embed.set_footer(text=footer)

    return embed

@bot.event
async def on_message(message):
    if database.DoesUserExist(message.author.id):
        database.CheckBalance(message.author.id)
        if database.ReadyForPromotion(message.author.id):
            await message.channel.send(embed=GreenEmbed(message.author, "Promoted!", 
            f"Congratulations! You have been promoted to `{database.CheckOccupation(message.author.id)}`!", f"You will now be making ${database.CheckWage(message.author.id)}/hr!"))

@bot.slash_command(name = "fight", description = "Fight someone!", guild_ids=[975128340744794243, 971590721142398996])
async def fight(ctx,
    user:Option(discord.Member, "Who would you like to fight?")):
    await on_message(ctx)
    if database.DoesUserExist(ctx.author.id):
        if user != ctx.author:
            if database.DoesUserExist(user.id):
                if database.CheckCooldown(ctx.author.id) == True:
                    if random.random() < 0.25:
                        await ctx.respond(embed=GreenEmbed(ctx.author, f"{ctx.author.name} punched {user.name}!", f"{user.mention}"))
                    else:
                        await ctx.respond(embed=ErrorEmbed(ctx.author, f"You lunged towards {user.mention} but you missed :skull:"))
                else:
                    await ctx.respond(embed=ErrorEmbed(ctx.author, f"You are on cooldown! Please wait {database.CheckCooldown(ctx.author.id)} more seconds.", 
                    "You can buy items that reduce the time of the cooldown in the shop."), ephemeral=True)
            else:
                await ctx.respond(embed=ErrorEmbed(user, "The person you tried to fight has not made an account yet. Tell them to do /balance to create one!"), 
                ephemeral=True) # Send the embed with some text
        else:
            await ctx.respond(embed=ErrorEmbed(user, "take it out on Jason instead!!!!"))
    else:
        await ctx.respond(embed=ErrorEmbed(ctx.author, "You have not made an account yet. Type /balance to make one!"), ephemeral=True) # Send the embed with some text

@bot.slash_command(name = "inventory", description = "Look at your inventory!", guild_ids=[975128340744794243, 971590721142398996])
async def inventory(ctx):
    await on_message(ctx)
    if database.DoesUserExist(ctx.author.id):
        desc = ""
        options = []

        for i in database.CheckInventoryNames(ctx.author.id):
            options.append(discord.SelectOption(label=f"{i} (x{database.GetIndexOfItem(f'{database.CheckStoreAliasByName(i)}Quantity', ctx.author.id)})", value=i, emoji=f"{database.CheckStoreEmojiByName(i)}"))
            desc+=f"{database.CheckStoreEmojiByName(i)} **{i}** — `(x{database.GetIndexOfItem(f'{database.CheckStoreAliasByName(i)}Quantity', ctx.author.id)})`\n{database.CheckStoreDescriptionByName(i)}\n\n"

        if desc:
            select = Select(placeholder="Choose an item to equip!", options=options)
            view = View(select)

            async def SelectCallback(interaction):
                select.disabled = True
                if not database.EquipItem(select.values[0], ctx.author.id):
                    await interaction.response.send_message(embed=GreenEmbed(ctx.author, "Equiped!", 
                    f"You have successfully equiped `{select.values[0]}`!",
                    f"You now have {database.GetIndexOfItem(f'{database.CheckStoreAliasByName(select.values[0])}Quantity', ctx.author.id)} left. You can buy more at the shop!"), ephemeral=True)
                else:
                    await interaction.response.send_message(embed=ErrorEmbed(ctx.author, 
                    f"You already have `{select.values[0]}` equipped! Please wait {'{:.2f}'.format(database.EquipItem(select.values[0], ctx.author.id))} more seconds!"), ephemeral=True)
            select.callback = SelectCallback

            embed = discord.Embed(
                title="Inventory",
                description=desc,
                color=discord.Colour.blurple(), # Pycord provides a class with default colors you can choose from
            )

            embed.set_footer(text="Use the dropdown menu below to use an item!", icon_url=ctx.author.display_avatar) # footers can have icons too
            #embed.set_thumbnail(url=user.display_avatar)
            await ctx.respond(embed=embed, view=view, ephemeral=True) # Send the embed with some text
        else:
            await ctx.respond(embed=ErrorEmbed(ctx.author, "Your inventory is empty. You can purchase items with /shop!"), ephemeral=True) # Send the embed with some text
    else:
        await ctx.respond(embed=ErrorEmbed(ctx.author, "You have not made an account yet. Type /balance to make one!"), ephemeral=True) # Send the embed with some text

@bot.slash_command(name = "shop", description = "Look at the shop!", guild_ids=[975128340744794243, 971590721142398996])
async def shop(ctx):
    await on_message(ctx)
    if database.DoesUserExist(ctx.author.id):
        options = []
        quantity = []
        desc = ""
        index = 0
        for i in database.CheckStoreNames():
            if i == "Bank Tier Upgrade":
                if not database.CheckBankIndex(ctx.author.id)+1 >= database.CheckBankTiersCurrently():
                    options.append(discord.SelectOption(label=f"{i}", emoji=f"{database.CheckStoreEmojiByName(i)}", description=f"${'{:.2f}'.format(database.CheckBankPrice(ctx.author.id, True))}"))
                    desc+=f"`{index+1}` {database.CheckStoreEmojiByName(i)} **{i}** — ${'{:.2f}'.format(database.CheckBankPrice(ctx.author.id, True))}\nUpgrade your banking to {database.CheckBankTierName(ctx.author.id, True)}, and increase your bank limit from ${database.CheckBankLimit(ctx.author.id)} to ${database.CheckBankLimit(ctx.author.id, True)}!\n\n"
            else:
                options.append(discord.SelectOption(label=f"{i}", emoji=f"{database.CheckStoreEmojiByName(i)}", description=f"${'{:.2f}'.format(database.CheckStorePrices(index))}"))
                desc+=f"`{index+1}` {database.CheckStoreEmojiByName(i)} **{i}** — ${'{:.2f}'.format(database.CheckStorePrices(index))}\n{database.CheckStoreDescription(index)}\n\n"
            index +=1
        
        for i in range(25):
            quantity.append(discord.SelectOption(label=f"{i+1}"))

        select = Select(placeholder="Choose an item to purchase!", options=options)
        view = View(select)
        selectQuantity = Select(placeholder="Choose how many of this item you would like!", options=quantity)
        selectQuantity.disabled=True

        async def SelectCallback(interaction):
            if select.values[0] != "Bank Tier Upgrade":
                view.add_item(selectQuantity)    
                select.disabled=True
                selectQuantity.disabled=False
                await interaction.response.edit_message(view=view)
            else:
                await interaction.response.send_message(embed=GreenEmbed(ctx.author, "Purchased!", 
                f"You have successfully purchased `{select.values[0]}` for ${'{:.2f}'.format(database.CheckBankPrice(ctx.author.id, True))}!",
                "This is an upgrade, not a consumable item. This upgrade will be automatically applied."), ephemeral=True)
                database.UpgradeBank(ctx.author.id)
            SelectCallback.firstChoice = select.values[0]

        async def SelectQuantityCallback(interaction):
            selectQuantity.disabled=True
            await interaction.response.edit_message(view=view)
            if database.CheckBalance(ctx.user.id) >= int(selectQuantity.values[0]) * database.CheckStorePriceByName(SelectCallback.firstChoice):
                await interaction.followup.send(embed=GreenEmbed(ctx.author, "Purchased!", 
                f"You have successfully purchased `{selectQuantity.values[0]}x {SelectCallback.firstChoice}` for ${'{:.2f}'.format(int(selectQuantity.values[0]) * database.CheckStorePriceByName(SelectCallback.firstChoice))}!",
                "Type /inventory to see how many items you have."), ephemeral=True)
                database.BuyItem(ctx.author.id, SelectCallback.firstChoice, int(selectQuantity.values[0]), int(selectQuantity.values[0]) * database.CheckStorePriceByName(SelectCallback.firstChoice))
            else:
                await ctx.respond(embed=ErrorEmbed(ctx.author, "You have insufficient funds."), ephemeral=True) # Send the embed with some text
                
        select.callback = SelectCallback
        selectQuantity.callback = SelectQuantityCallback

        embed = discord.Embed(
            title="Shop",
            description=desc,
            color=discord.Colour.blurple(), # Pycord provides a class with default colors you can choose from
        )

        embed.set_footer(text="Use the dropdown menus below to purchase something from the shop.", icon_url=ctx.author.display_avatar) # footers can have icons too
        #embed.set_thumbnail(url=user.display_avatar)
        await ctx.respond(embed=embed, view=view, ephemeral=True) # Send the embed with some text
    else:
        await ctx.respond(embed=ErrorEmbed(ctx.author, "You have not made an account yet. Type /balance to make one!"), ephemeral=True) # Send the embed with some text


@bot.slash_command(name = "balance", description = "Check how much money you or someone else have!", guild_ids=[975128340744794243, 971590721142398996, 1043393156315623455])
async def balance(ctx,
    user:Option(discord.Member, "Optional: Find how much money someone else has!", default = "")):
    await on_message(ctx)
    if not user:
        user = ctx.author
    while True:
        if database.DoesUserExist(user.id):
            embed = discord.Embed(
                title="Balance",
                color=discord.Colour.blurple(), # Pycord provides a class with default colors you can choose from
            )
            embed.add_field(name="JasonBucks", value=f"**${'{:.2f}'.format(database.CheckBalance(user.id))}** [${database.CheckWage(user.id)}/hr]")
            embed.add_field(name="Bank", value=f"**${'{:.2f}'.format(database.CheckBank(user.id))}** [{database.CheckBankTier(user.id)}]")
            embed.add_field(name="Occupation", value=database.CheckOccupation(user.id))

        
            embed.set_footer(text="You got this!", icon_url=user.display_avatar) # footers can have icons too
            embed.set_author(name=user.name, icon_url=user.display_avatar)
            #embed.set_thumbnail(url=user.display_avatar)
            embed.set_image(url=user.display_avatar)
        
            await ctx.respond(embed=embed, ephemeral=True) # Send the embed with some text
            break
        else:
            if user == ctx.author:
                await ctx.respond(embed=GreenEmbed(ctx.author, "Welcome to JasonBot!", """Welcome! This is JasonBot, an 
                economy discord bot that you can do many things, such as purchase items, and fight many other things!""".replace('\n', '')), ephemeral=True)
                await ctx.respond(embed=GreenEmbed(ctx.author, "How do I get started?", """You get new jobs just by playing,
                and your job influences how much money you make per hour. Your ability to get a promotion is based off of your 
                total networth (All the money you've ever made).""".replace('\n', '')), ephemeral=True) 
                database.CreateAccount(user.id, user)
            else:
                await ctx.respond(embed=ErrorEmbed(user, "This person has not made an account yet. Tell them to do /balance to create one!"), ephemeral=True) # Send the embed with some text
                break

@bot.slash_command(name = "pay", description = "Give someone money!", guild_ids=[975128340744794243, 971590721142398996])
async def pay(ctx,
    user:Option(discord.Member, "Enter the person you would like to pay!"),
    amount:Option(int, "Enter how much you would like to pay!",min_value=1,)):
    await on_message(ctx)
    while True:
        if database.DoesUserExist(user.id):
            if database.DoesUserExist(ctx.user.id):
                if amount <= database.CheckBalance(ctx.user.id):
                    database.TransferMoney(ctx.user.id, user.id, amount)
                    await ctx.respond(f"You gave {user} ${amount}!")
                    break
                else:
                    await ctx.respond("You have insufficent funds!", ephemeral=True)
                    break
            else:
                database.CreateAccount(ctx.user.id, ctx.user)
        else:
            await ctx.respond(embed=ErrorEmbed(user, "This person has not made an account yet. Tell them to do /balance to create one!"), ephemeral=True) # Send the embed with some text
            break

@bot.slash_command(name = "deposit", description = "Put money into your bank account.", guild_ids=[975128340744794243, 971590721142398996])
async def deposit(ctx,
    amount:Option(int, "Enter how much you would like to deposit.")):
    await on_message(ctx)
    if database.DoesUserExist(ctx.author.id):
        if amount <= database.CheckBalance(ctx.author.id):
            if amount <= database.CheckBankLimit(ctx.author.id) and (amount+database.CheckBank(ctx.author.id))<=database.CheckBankLimit(ctx.author.id):
                database.DepositBank(ctx.author.id, amount)
                embed = discord.Embed(
                    title="Deposted!",
                    description=f"You have successfully deposited ${amount}!",
                    color=discord.Colour.green(), # Pycord provides a class with default colors you can choose from
                )
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
                embed.set_thumbnail(url=ctx.author.display_avatar)

                await ctx.respond(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(
                    title="Bank tier exceeded",
                    description=f"""You tried to deposit ${amount}.00 (total balance of ${'{:.2f}'.format(database.CheckBank(ctx.author.id))}), which is more than what the 
                    **[{database.CheckBankTier(ctx.author.id)}]** tier can handle. (${'{:.2f}'.format(database.CheckBankLimit(ctx.author.id))}) Type /bank to upgrade your bank.""".replace('\n',''),
                    color=discord.Colour.red(), # Pycord provides a class with default colors you can choose from
                )
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
                embed.set_thumbnail(url=ctx.author.display_avatar)
            
                await ctx.respond(embed=embed, ephemeral=True) # Send the embed with some text
        else:
            await ctx.respond(embed=ErrorEmbed(ctx.author, "You have insufficient funds."), ephemeral=True) # Send the embed with some text
    else:
        await ctx.respond(embed=ErrorEmbed(ctx.author, "You have not made an account yet. Type /balance to make one!"), ephemeral=True) # Send the embed with some text

@bot.slash_command(name = "bank", description = "Check your banking information!", guild_ids=[975128340744794243, 971590721142398996])
async def bank(ctx,
    user:Option(discord.Member, "Optional: Check the banking information of someone else!", default = "")):
    if not user:
        user = ctx.author
    if database.DoesUserExist(user.id):
        embed = discord.Embed(
            title=database.CheckBankTierName(user.id),
            color=discord.Colour.green(), # Pycord provides a class with default colors you can choose from
        )
        embed.add_field(name="Bank Balance", value=f"${'{:.2f}'.format(database.CheckBank(user.id))}")
        embed.add_field(name="Limit", value=f"${'{:.2f}'.format(database.CheckBankLimit(user.id))}")
        embed.add_field(name="Daily Fees", value=f"${'{:.2f}'.format(database.CheckBankFees(user.id))}")

        embed.set_author(name=ctx.author.name, icon_url=user.display_avatar)
        embed.set_thumbnail(url=user.display_avatar)

        await ctx.respond(embed=embed, ephemeral=True)
    else:
        await ctx.respond(embed=ErrorEmbed(user, "This person has not made an account yet. Tell them to do /balance to create one!"), ephemeral=True)

@bot.slash_command(name = "reset", description = "Wipe the database", guild_ids=[975128340744794243, 971590721142398996])
async def reset(ctx):
    database.ResetDatabase()
    await ctx.respond("ok")

@bot.slash_command(name = "anonymous", description = "Send an anonymous message to #quotations!", guild_ids=[975128340744794243, 971590721142398996])
async def anonymous(ctx,
    message:Option(str, "Say an anonymous message.")):
    await on_message(ctx)
    database.LogMessage(ctx.author.id, message, ctx.author)
    await bot.get_channel(int("971618873440890880")).send(f'{message}')
    await ctx.respond(f"You said '{message}' anonymously! XD", ephemeral=True)

bot.run("OTc1MTI3NDAxMDEwOTU0MzEy.GB0wQN.iqaoGWUAYn8_Vj8yxwqq0Cxa6J6gjGbV57ggms")
