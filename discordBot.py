# discordBot.py
import discord
import os
import random
import botHelper # Helper functions.
from dotenv import load_dotenv
from enum import Enum
from datetime import date
from discord import app_commands
from malApi import malAPI

# Load tokens.
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = os.getenv('GUILD_ID')
MY_GUILD = discord.Object(id=GUILD_ID)

# Client wrapper to bind commands and guild_id.
class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)

        # Bind tree to client.
        self.tree = app_commands.CommandTree(self)

        # API connection.
        self.api = malAPI()
    
    # Sync commands to one guild.
    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

    # Shutdown command.
    async def close(self):
        print("Shutting down.")
        await super().close()

# Client definition and setup.
intents = discord.Intents.default()
client = MyClient(intents=intents)

# Log-in message.
@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

# Search for an anime.
@client.tree.command(name="animebyname", description="Returns a list of anime that match the search query. Use /animebyid for details.")
@app_commands.describe(query="Name of anime.", limit="Number of results to return. Default: 10, Limit: 20")
async def animeByName(interaction: discord.Interaction, query: str, limit: int=10):
    response = client.api.getAnime(query.strip(), limit)
    if response == False:
        await interaction.response.send_message(f"Request send error.")
        return

    # Format response.
    results = ""
    i = 1
    for item in response:
        results += f"#{i} {item['title']} (ID: {item['id']})\n"
        i += 1
    await interaction.response.send_message(results)

# Retrieve anime by ID.
@client.tree.command(name="animebyid", description="Retrieves the MAL entry for the anime id given.")
@app_commands.describe(anime_id="MAL anime id.")
async def animeById(interaction: discord.Interaction, anime_id: str):
    # Prevent timeout.
    await interaction.response.defer()

    # Call API.
    response = client.api.getAnimeByID(anime_id.strip())
    if response == False:
        await interaction.followup.send(f"The requested anime could not be found.")
        return
    
    # Format response, retrieve cover, send.
    anime_info = botHelper.formatAnimeInfo(response)
    picture_url = response['main_picture']['medium']
    anime_pic = await botHelper.downloadImage(picture_url, f"{response['title']}.jpg")
    if anime_pic == False:
        await interaction.followup.send(f"Error: Failed to retrieve image for {response['title']}.")
    else:
        await interaction.followup.send(file=anime_pic, content=anime_info)

# Enum to enable slash command choices.
class Rankings(Enum):
    all = "all"
    airing = "airing"
    upcoming = "upcoming"
    tv = "tv"
    ova = "ova"
    movie = "movie"
    special = "special"
    bypopularity = "bypopularity"
    favorite = "favorite"

rank_explanations = { "all" : "Top Anime Series:",
                      "airing" : "Top Airing Anime:",
                      "upcoming" : "Top Upcoming Anime:",
                      "tv" : "Top Anime TV Series",
                      "ova" : "Top Anime OVA Series",
                      "movie" : "Top Anme Movies",
                      "special" : "Top Anime Specials",
                      "bypopularity" : "Top Anime by Popularity",
                      "favorite" : "Top Favorited Anime", }

# Retrieve anime by ranking.
@client.tree.command(name="animeranking", description="Retrieves anime ranking by given type.")
@app_commands.describe(rank_type="Ranking type.", limit="Number of results to return. Default: 10, Limit: 20")
async def animeRanking(interaction: discord.Interaction, rank_type: Rankings, limit: int=10):
    response = client.api.getAnimeRanking(rank_type.value, limit)
    if response == False:
        await interaction.response.send_message(f"Request send error.")
        return
    
    # Format response.
    results = rank_explanations[rank_type.value] + "\n" # Header.
    for item in response:
        results += f"#{item['rank']} {item['title']} (ID: {item['id']})\n"
    await interaction.response.send_message(results)

# Enum to enable slash command choices.
class SeasonSort(Enum):
    anime_score = "anime_score"
    num_users = "anime_num_list_users"

class Seasons(Enum):
    winter = "winter"
    spring = "spring"
    summer = "summer"
    fall = "fall"

# Retrieve seasonal anime.
@client.tree.command(name="animebyseason", description="Retrieves all anime from a given season.")
@app_commands.describe(season="Airing season.", year="Airing year.", sort="Sort order.", limit="Number of results to return. Default: 10, Limit: 20")
async def animeBySeason(interaction: discord.Interaction, season: Seasons, year: int, sort: SeasonSort, limit: int=10):
    response = client.api.getSeasonalAnime(year, season.value, sort.value, limit)
    if response == False:
        await interaction.response.send_message(f"Request send error.")
        return
    
    # Format response.
    results = f"{season.value.capitalize()} {str(year)}:\n" # Header
    i = 1
    for item in response:
        results += f"#{i} {item['title']} (ID: {item['id']})\n"
        i += 1
    await interaction.response.send_message(results)

# Get random anime.
@client.tree.command(name="randomanime", description="Get a random anime.")
async def randomAnime(interaction: discord.Interaction):
    # Prevent timeout.
    await interaction.response.defer()

    # Generate random id.
    response = False
    anime_id = 0
    tries = 0  # Max attempts.
    while response == False and tries <= 10:
        anime_id = random.randint(0, 60000)
        response = client.api.getAnimeByID(str(anime_id))
        tries += 1

    # Timeout error.
    if response == False:
        await interaction.followup.send(f"Request timed out.")
        return
    
    # Format response, retrieve cover, send.
    anime_info = botHelper.formatAnimeInfo(response)
    picture_url = response['main_picture']['medium']
    anime_pic = await botHelper.downloadImage(picture_url, f"{response['title']}.jpg")
    if anime_pic == False:
        await interaction.followup.send(f"Error: Failed to retrieve image for {response['title']}.")
    else:
        await interaction.followup.send(file=anime_pic, content=anime_info)

# Get days until next episode releases.
@client.tree.command(name="nextepisode", description="Calculates days until next episode of given anime. (JST only.)")
@app_commands.describe(anime_id="MAL anime id.")
async def nextEpisode(interaction: discord.Interaction, anime_id: str):
    fields="id,title,start_date,status,broadcast"
    response = client.api.getAnimeByID(anime_id.strip(), fields)
    if response == False:
        await interaction.response.send_message(f"The requested anime could not be found.")
        return
    
    # Time variables.
    time_until = 0
    today = date.today()

    # Show ended.
    if response['status'] == "finished_airing":
        await interaction.response.send_message(f"{response['title']} has already finished airing.")
    
    # Not aired.
    elif response['status'] == "not_yet_aired":
        if "start_date" in response:
            await interaction.response.send_message(f"{response['title']} has an air date of {response['start_date']}.\n")
        else:
            await interaction.response.send_message(f"{response['title']} hasn't begun airing yet.")
    
    # Airing.
    elif response['status'] == "currently_airing":
        broadcast = response['broadcast']
        reply = f"{response['title']} airs at {broadcast['start_time']} on {broadcast['day_of_the_week'].capitalize()}s!\n"

        # Calculate next day of next episode.
        next_ep_date = botHelper.nextDay(today, broadcast['day_of_the_week'])
        time_until = (next_ep_date - today).days
        if time_until == 0:
            reply += f"The next episode airs today at {broadcast['start_time']}! (Or at least it should.)"
        else:
            reply += f"The next episode (should) air in {time_until} day(s)."
        
        await interaction.response.send_message(reply)

    # Fall-through.
    else:
        await interaction.response.send_message(f"{response['title']} has an unknown status.")

# Enums to enable slash command choices.
class ListSort(Enum):
    list_score = "list_score"
    list_updated_at = "list_updated_at"
    anime_title = "anime_title"
    anime_start_date = "anime_start_date"
    # anime_id = "anime_id"  # Not yet implemented, apparently.
 
class Status(Enum):
    all = ""
    watching = "watching"
    completed = "completed"
    on_hold = "on_hold"
    dropped = "dropped"
    plan_to_watch = "plan_to_watch"

# Retrieve a user's anime list.
@client.tree.command(name="getuseranimelist", description="Retrieves a given user's anime list.")
@app_commands.describe(user_name="MAL username.", status="Watch status.", sort="Sort by.", limit="Number of results to return. Default: 10, Limit: 20")
async def getUserAnimelist(interaction: discord.Interaction, user_name: str, status: Status, sort: ListSort, limit: int=10):
    if user_name == "":
        await interaction.response.send_message(f"Please specify a user.")
        return
    
    # Call API.
    response = client.api.getUserAnimeList(user_name, status.value, sort.value, limit)
    if response == False:
        await interaction.response.send_message(f"User not found.")
        return
    
    # Format response.
    results = f"User: {user_name}\n" # Header.
    i = 1
    for item in response:
        results += f"#{i} {item['title']} (ID: {item['id']})\n   Status: {item['status'].capitalize()}   Score: {item['score']}\n"
        i += 1
    await interaction.response.send_message(results)

# Start the bot.
def start():
    client.run(DISCORD_TOKEN)

# Begin.
if __name__ == "__main__":
    start()