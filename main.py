import discord
from discord.ext import commands
import random
import logging
from dotenv import load_dotenv
import os
import random
import re
from discord.ext import commands
import webserver

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Logging setup
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
logging.basicConfig(level=logging.DEBUG, handlers=[handler])

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Event handlers
@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready")

#message triggers
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    msg = message.content
    if len(msg) >=300:
        await message.channel.send('Holy yapp')
    
    pattern = r"^i(?:'|'|\s+a)?m\s+([a-zA-Z0-9][^<]*?)(?:\s*<.*)?$"
    if re.match(pattern, msg.lower()):
        response = re.match(pattern, msg, flags=re.IGNORECASE)
        if response:
            await message.channel.send(f"Hi {response[1]}, I'm Bot")
            return
    
    targets = ["ganyu","Ganyu"]
    if any(t in msg.lower() for t in targets):
        if message.author.name == 'syrgarde' or message.author.name == 'key_2':
            await message.channel.send('g*nyu')
        elif random.choice(range(5)) == 1:
            await message.channel.send('g*nyu')
    
    if 'phainon' in msg.lower() and random.choice(range(100)) == 1:
        await message.channel.send("paimon")
    
    if re.search(r'^ban$', msg.lower()):
        file = discord.File("media/banhana.png", filename='banhana.gif')
        await message.channel.send(file=file)

    if re.search(r'^(who|who\?)$', msg.lower()):
        await message.channel.send('tao')
    
    if re.search(r'\bwhere\b', msg.lower()) and random.choice(range(10)) == 1:
        await message.channel.send('over der 👉')
    
    if re.search(r'^(bad bot)$', msg.lower()):
        await message.channel.send('<:hamsterStare:1386426294870212771>')
    
    await bot.process_commands(message)

# memeber join
@bot.event
async def on_member_join(member):
    """
    Assigns a default role to a new member when they join the server.
    """
    role_name = "banned"  
    role = discord.utils.get(member.guild.roles, name=role_name)

    if role:
        try:
            await member.add_roles(role)
        except discord.Forbidden:
            print(f"Bot does not have permission to assign the role '{role.name}'.")
        except discord.HTTPException as e:
            print(f"An error occurred while assigning the role: {e}")
    else:
        print(f"The role '{role_name}' does not exist. Please create it in the server.")

# help
@bot.command(name='help')
async def help(ctx):
    embed = discord.Embed(
        title='Commands:',
        description="""
    **!help** - Diplays this help message.
    **!hello** - Says hello back.
    **!assign** - Assign the user a random role.
    **!editrole** - Edit your assigned role `!editrole rolename #color`.
    **!8ball** - Ask the magic 8 ball a question.
"""
    )
    await ctx.send(embed = embed)
# hello
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")

# magic 8 ball
@bot.command(name='8ball')
async def magicBall(ctx,*,inputs: str):
    responses = [
       "Yes, definitely.",
       "As I see it, yes.",
       "Reply hazy, try again.",
       "Cannot predict now.",
       "Do not count on it.",
       "My sources say no.",
       "Outlook not so good.",
       "Very doubtful."
   ]
    await ctx.reply(f"{random.choice(responses)}", mention_author = True)

# role assign command
@bot.command()
async def assign(ctx):
    # Exclude @everyone role and check user's current roles
    user_roles = [role for role in ctx.author.roles if role != ctx.guild.default_role]
    
    if len(user_roles) >= 2:
        await ctx.send(f"{ctx.author.mention}, you cannot have more than 2 roles.")
        return
    # Generate a random role name
    random_role_name = f"Role-{random.randint(1000, 9999)}"
    try:
        # Create the new role
        new_role = await ctx.guild.create_role(name=random_role_name)
        await ctx.author.add_roles(new_role)
        embed = discord.Embed(
            title="Role Assigned",
            description=f"You've been assigned the role **{new_role.name}**. Use `!editrole` to customize it!",
            color=new_role.color
        )
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("I don't have permissions to create roles. Please check my role permissions.")
    except discord.HTTPException as e:
        await ctx.send(f"An error occurred: {e}")

# role edit command
@bot.command(name='editrole')
async def edit_role(ctx, *, inputs: str):
    """
    Allows a user to edit the name or color of their assigned role.
    If the user only has the 'banned' role, they are instructed to use '!assign' to get a new role.
    Parameters:
    - inputs: Multi-word inputs for new name and/or hex color (e.g., "!editrole new name #FF0000").
    """
    # Extract new name and color from the input
    parts = inputs.split("#")
    new_name = parts[0].strip() if parts[0] else None
    hex_color = f"#{parts[1].strip()}" if len(parts) > 1 else None

    # Find the user's roles (excluding @everyone)
    user_roles = ctx.author.roles[1:]
    if not user_roles:
        await ctx.send(f"{ctx.author.mention}, you don't have any custom roles to edit.")
        return

    # Check for the 'banned' role
    banned_role = discord.utils.get(ctx.guild.roles, name="banned")
    if banned_role in user_roles and len(user_roles) == 1:
        await ctx.send(
            f"{ctx.author.mention}, you cannot edit the role 'banned'. "
            f"Please use `!assign` to get a random role to edit."
        )
        return

    # Select the first editable role (not 'banned')
    user_role = next((role for role in user_roles if role != banned_role), None)
    if not user_role:
        await ctx.send(f"{ctx.author.mention}, no editable roles were found.")
        return

    # Prepare updates
    updates = {}
    if new_name:
        updates['name'] = new_name
    if hex_color:
        try:
            if hex_color.startswith('#'):
                hex_color = hex_color[1:]
            updates['colour'] = discord.Colour(int(hex_color, 16))
        except ValueError:
            await ctx.send("Invalid hexadecimal color code. Please use a format like `#FF0000`.")
            return

    try:
        # Apply the updates to the user's role
        await user_role.edit(**updates)
        embed = discord.Embed(
            title="Role Updated",
            description=f"Your role has been updated:\n"
                        f"**Name:** {updates.get('name', user_role.name)}\n"
                        f"**Color:** {hex_color or user_role.color}",
            color=updates.get('colour', user_role.color)
        )
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("I don't have permissions to edit roles. Please check my role permissions.")
    except discord.HTTPException as e:
        await ctx.send(f"An error occurred: {e}")


webserver.keep_alive()
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
