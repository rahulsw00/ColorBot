import discord
from discord.ext import commands
import random
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Logging setup
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
logging.basicConfig(level=logging.DEBUG, handlers=[handler])

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Event handlers
@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready")

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

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")

@bot.command(name= 'assign', help="use !assign to give yourself random role")
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

@bot.command(name='editrole', help="Edit your assigned role `!editrole rolename #color`.")
async def edit_role(ctx, *, inputs: str):
    """
    Edits the user's assigned role's name or color.
    Parameters:
    - inputs: Multi-word inputs for new name and/or hex color (e.g., "!editrole new name #FF0000").
    """
    # Extract new name and color from the input
    parts = inputs.split("#")
    new_name = parts[0].strip() if parts[0] else None
    hex_color = f"#{parts[1].strip()}" if len(parts) > 1 else None

    # Find the user's assigned roles
    user_roles = ctx.author.roles[1:]  # Exclude the @everyone role
    if not user_roles:
        await ctx.send(f"{ctx.author.mention}, you don't have any custom roles to edit.")
        return

    # Use the first custom role found
    user_role = user_roles[0]

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
        # Apply the updates to the user's specific role
        await user_role.edit(**updates)
        embed = discord.Embed(
            title="Role Updated",
            description=f"Your role has been updated:\n"
                        f"**Name:** {updates.get('name', user_role.name)}\n"
                        f"**Color:** {hex_color or user_role.color}",
            color=user_role.color
        )
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("I don't have permissions to edit roles. Please check my role permissions.")
    except discord.HTTPException as e:
        await ctx.send(f"An error occurred: {e}")


bot.run(token, log_handler=handler, log_level=logging.DEBUG)
