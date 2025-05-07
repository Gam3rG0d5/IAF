import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# Bot setup with intents
intents = discord.Intents.default()
intents.members = True  # For on_member_join event
intents.message_content = True  # For command processing
bot = commands.Bot(command_prefix='!', intents=intents)

# Remove default help command to avoid conflict
bot.remove_command('help')

# Path to the welcome video and clips directory
WELCOME_VIDEO_PATH = "Edit on Indian Air force.mp4"  # Ensure this file is in the repository
CLIPS_DIR = "clips"  # Directory to store user-uploaded clips

# Create clips directory if it doesn't exist
if not os.path.exists(CLIPS_DIR):
    os.makedirs(CLIPS_DIR)

# Check if user has admin role
def has_admin():
    async def predicate(ctx):
        admin_role = discord.utils.get(ctx.guild.roles, name="IAF Admin")
        return (ctx.author.guild_permissions.administrator or
                (admin_role and admin_role in ctx.author.roles))
    return commands.check(predicate)

# Check if user is the server owner
def is_owner():
    async def predicate(ctx):
        return ctx.author == ctx.guild.owner
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    # Ensure admin role exists in all guilds
    for guild in bot.guilds:
        if not discord.utils.get(guild.roles, name="IAF Admin"):
            await guild.create_role(name="IAF Admin", permissions=discord.Permissions(administrator=True))
    # Keep the bot running
    while True:
        await asyncio.sleep(3600)  # Sleep for an hour to keep the event loop alive

@bot.event
async def on_member_join(member):
    if os.path.exists(WELCOME_VIDEO_PATH):
        welcome_message = (
            f"Shyt Yeah! Welcome to the IAF - Indian Air Force server! "
            f"Get ready to soar with us! 🚀"
        )
        video_file = discord.File(WELCOME_VIDEO_PATH, filename="welcome_video.mp4")
        try:
            await member.send(content=welcome_message, file=video_file)
        except discord.Forbidden:
            # Handle case where user has DMs disabled
            channel = member.guild.system_channel
            if channel is not None:
                await channel.send(
                    f"Shyt Yeah! Welcome {member.mention} to the IAF - Indian Air Force server! "
                    f"Couldn't DM you the welcome video, check it out here! 🚀",
                    file=discord.File(WELCOME_VIDEO_PATH, filename="welcome_video.mp4")
                )
    else:
        try:
            await member.send(
                f"Shyt Yeah! Welcome to the IAF - Indian Air Force server! "
                f"Get ready to soar with us! 🚀 (Video file missing, contact admin!)"
            )
        except discord.Forbidden:
            channel = member.guild.system_channel
            if channel is not None:
                await channel.send(
                    f"Shyt Yeah! Welcome {member.mention} to the IAF - Indian Air Force server! "
                    f"Get ready to soar with us! 🚀 (Video file missing, contact admin!)"
                )

@bot.command(description="Send a clip based on a prompt (e.g., '!clip launch')")
async def clip(ctx, prompt: str):
    # Check for video (.mp4) or image (.png, .jpg) files
    for ext in [".mp4", ".png", ".jpg"]:
        clip_path = os.path.join(CLIPS_DIR, f"{prompt}{ext}")
        if os.path.exists(clip_path):
            clip_file = discord.File(clip_path, filename=f"{prompt}{ext}")
            await ctx.send(f"Shyt Yeah! Here's the {prompt} clip! 🚀", file=clip_file)
            return
    await ctx.send(f"No clip found for prompt '{prompt}'. Try another one! 😕")

@bot.command(description="Add a new clip (admin only)")
@has_admin()
async def addclip(ctx, prompt: str):
    if not ctx.message.attachments:
        await ctx.send("Please attach an image or video file to add as a clip! 📎")
        return
    attachment = ctx.message.attachments[0]
    if not attachment.filename.endswith((".mp4", ".png", ".jpg")):
        await ctx.send("Only .mp4, .png, or .jpg files are supported! 🚫")
        return
    # Check file size (8 MB limit for free bots)
    if attachment.size > 8 * 1024 * 1024:
        await ctx.send("File is too large! Must be under 8 MB for free bots. 📏")
        return
    # Save the file
    ext = os.path.splitext(attachment.filename)[1]
    clip_path = os.path.join(CLIPS_DIR, f"{prompt}{ext}")
    await attachment.save(clip_path)
    await ctx.send(f"Clip '{prompt}' added successfully! 🥳")

@bot.command(description="Test the welcome message (admin only)")
@has_admin()
async def testwelcome(ctx):
    if os.path.exists(WELCOME_VIDEO_PATH):
        welcome_message = (
            f"Shyt Yeah! Welcome to the IAF - Indian Air Force server! "
            f"Get ready to soar with us! 🚀"
        )
        video_file = discord.File(WELCOME_VIDEO_PATH, filename="welcome_video.mp4")
        try:
            await ctx.author.send(content=welcome_message, file=video_file)
            await ctx.send("Welcome message sent to your DMs! 🚀")
        except discord.Forbidden:
            await ctx.send("Couldn't send the welcome message to your DMs. Please enable DMs from server members! 😕")
    else:
        try:
            await ctx.author.send(
                f"Shyt Yeah! Welcome to the IAF - Indian Air Force server! "
                f"Get ready to soar with us! 🚀 (Video file missing, contact admin!)"
            )
            await ctx.send("Welcome message sent to your DMs! 🚀")
        except discord.Forbidden:
            await ctx.send("Couldn't send the welcome message to your DMs. Please enable DMs from server members! 😕")

@bot.command(description="Ban a user (admin only)")
@has_admin()
async def ban(ctx, user: discord.Member, *, reason: str = "No reason provided"):
    if user == ctx.author:
        await ctx.send("You can't ban yourself, silly! 😆")
        return
    await user.ban(reason=reason)
    await ctx.send(f"{user.mention} has been banned! Reason: {reason} 🚫")

@bot.command(description="Kick a user (admin only)")
@has_admin()
async def kick(ctx, user: discord.Member, *, reason: str = "No reason provided"):
    if user == ctx.author:
        await ctx.send("You can't kick yourself, silly! 😆")
        return
    await user.kick(reason=reason)
    await ctx.send(f"{user.mention} has been kicked! Reason: {reason} 👢")

@bot.command(description="Add an admin (owner only)")
@is_owner()
async def addadmin(ctx, user: discord.Member):
    admin_role = discord.utils.get(ctx.guild.roles, name="IAF Admin")
    if not admin_role:
        admin_role = await ctx.guild.create_role(name="IAF Admin", permissions=discord.Permissions(administrator=True))
    await user.add_roles(admin_role)
    await ctx.send(f"{user.mention} is now an IAF Admin! 🛡️")

@bot.command(description="Show this help message")
async def help(ctx):
    help_message = (
        "Shyt Yeah! Here are the available commands for IAF - Indian Air Force bot! 🚀\n"
        "!clip <prompt> - Send a clip based on a prompt (e.g., '!clip launch')\n"
        "!addclip <prompt> - Add a new clip (admin only)\n"
        "!testwelcome - Test the welcome message (admin only)\n"
        "!ban <user> [reason] - Ban a user (admin only)\n"
        "!kick <user> [reason] - Kick a user (admin only)\n"
        "!addadmin <user> - Add an admin (owner only)\n"
        "!help - Show this help message"
    )
    await ctx.send(help_message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("pakistani hain kya bhadwe")
    else:
        raise error

# Run the bot using the token from environment variable
bot.run(os.getenv('DISCORD_TOKEN'))
