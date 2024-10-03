import discord, os, json
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True      # Ensure the bot can read message content
intents.guilds = True               # Ensure the bot can access guilds (servers)
intents.members = True              # Ensure the bot can access member information

bot = commands.Bot(command_prefix="!", intents=intents)

# Triggered when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

# Function to load data from the JSON file
def load_data(DATA_FILE):
    # Check if the file exists
    if os.path.exists(DATA_FILE):
        # Check if the file is empty
        if os.stat(DATA_FILE).st_size == 0:
            return {}
        # Try to load the JSON data
        try:
            with open(DATA_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            # If the file is corrupted or empty, return an empty dictionary
            return {}
    else:
        # If the file doesn't exist, return an empty dictionary
        return {}

# Function to save data to the JSON file
def save_data(data, DATA_FILE):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

@bot.event
async def on_message(message):

    if message.author == bot.user:
        return

    DATA_FILE = 'SavedData.json'
    STATS_FILE = 'SavedStats.json'
    # Load data from JSON files
    data = load_data(DATA_FILE)
    stats = load_data(STATS_FILE)

    # Get the guild ID where the message was sent
    guild_id = str(message.guild.id)
    author_id = str(message.author.id)

    # Check if the guild has a saved role ID in the JSON file
    if guild_id in data:
        saved_role_id = data[guild_id].get("role_id")  # Get the saved role ID

        # Ensure the message author is a member and has the required role
        if isinstance(message.author, discord.Member):
            if any(role.id == int(saved_role_id) for role in message.author.roles):
                emoji_list = [
                    "🐡",  # blowfish
                    "🐠",  # tropical_fish
                    "🐟",  # fish
                    "🐬",  # dolphin
                    "🐋",  # whale2
                    "🐳",  # whale
                    "🦈",  # shark
                    "🧜‍♂️",  # merman
                    "🪼",  # jellyfish
                    "🌊",  # ocean
                    "🍣",  # sushi
                    "🎣",  # fishing_pole_and_fish
                    "🎏",  # carp_streamer
                    "🇫",  # regional_indicator_f
                    "🇮",  # regional_indicator_i
                    "🇸",  # regional_indicator_s
                    "🇭",  # regional_indicator_h
                    "🦑",  # squid
                    "🐙",  # octopus
                    "🐢"  # turtle
                ]

                # Add to the counter that counts how many times the person has been fish reacted to
                if author_id in stats:
                    saved_reactions = stats[author_id].get("reactions")
                    new_saved_reactions = saved_reactions + 1
                    stats[author_id]["reactions"] = new_saved_reactions
                    save_data(stats, STATS_FILE)
                    if new_saved_reactions % 50 == 0:
                        await message.channel.send(f"<@{author_id}> has been fish reacted {new_saved_reactions} times!")
                else:
                    stats[author_id] = {"reactions": 1}
                    save_data(stats, STATS_FILE)
                    await message.channel.send(f"Its <@{author_id}> first time getting fish reacted!")

                # React to the message with each emoji
                for emoji in emoji_list:
                    try:
                        await message.add_reaction(emoji)
                    except discord.HTTPException as e:
                        # Handle specific Discord API exceptions (e.g., message not found)
                        print(f"Failed to add reaction {emoji} to message {message.id}: {e}")
                        # Optionally, send a message in the channel notifying about the error
                        await message.channel.send("Someone deleted the message I was reacting to!")

@bot.tree.command(name="selectfishrole", description="Select a role that should get fish reacted to!")
@app_commands.describe(role='The role that should get fish reacted to')
async def selectfishrole_command(interaction: discord.Interaction, role: discord.Role):
    DATA_FILE = 'SavedData.json'
    # Load the current data from the JSON file
    data = load_data(DATA_FILE)
    guild_id = str(interaction.guild.id)  # Get the guild ID as a string
    new_role_id = str(role.id)  # Get the role ID as a string

    # Check if there's already a saved role for this guild
    if guild_id in data:
        saved_role_id = data[guild_id].get("role_id")
        if saved_role_id == new_role_id:
            # If the role is already set, notify the user
            await interaction.response.send_message(
                f"The role <@&{new_role_id}> is already set as the fish role!"
            )
            return
        else:
            # Overwrite the old role with the new one
            data[guild_id]["role_id"] = new_role_id
            save_data(data, DATA_FILE)
            # Notify the user that the role has been overwritten
            await interaction.response.send_message(
                f"Overwritten the previous role <@&{saved_role_id}> with the new role <@&{new_role_id}>!"
            )
    else:
        # If no role is set yet, save the new role
        data[guild_id] = {"role_id": new_role_id}
        save_data(data, DATA_FILE)
        # Notify the user that the role has been saved
        await interaction.response.send_message(f"Saved role <@&{new_role_id}> for this guild.")

@bot.tree.command(name="getstats", description="Get the fish reactions stats for a specific user!")
@app_commands.describe(member='The member you want to get stats for!')
async def getstats_command(interaction: discord.Interaction, member: discord.Member):
    STATS_FILE = 'SavedStats.json'
    stats = load_data(STATS_FILE)
    member_id = str(member.id)

    print(member.id)

    if member_id in stats:
        saved_reactions = stats[member_id].get("reactions")
        await interaction.response.send_message(f"<@{member_id}> has gotten fish reacted {saved_reactions} times!")
    else:
        await interaction.response.send_message(f"<@{member_id}> has not yet been fish reacted!")

from typing import Final
from dotenv import load_dotenv
load_dotenv()
TOKEN : Final[str] = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)
