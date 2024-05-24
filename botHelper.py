# botHelper.py
# Helper functions for discordBot.py.
import io
import aiohttp
from datetime import timedelta
from discord import File

# Helper function for downloading images from a given URL.
async def downloadImage(url, filename="default.jpg"):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return False
            data = io.BytesIO(await resp.read())
            filename = filename.replace(" ", "")
            image = File(data, filename)
            return image
        
# Anime info format helper function.
def formatAnimeInfo(response):
    # There must be a title.
    anime_title = response['title']

    # end_date without a start_date shouldn't be possible.
    if 'start_date' in response and 'end_date' in response:
        air_date = f"{response['start_date']} ～ {response['end_date']}"
    elif 'start_date' in response:
        air_date = f"{response['start_date']} ～ ???"
    else:
        air_date = "Unknown"

    # All season data should exist, or none of it.
    if 'start_season' in response:
        air_season = f"{response['start_season']['season'].capitalize()} {response['start_season']['year']}"
    else:
        air_season = "Unknown"

    # Default value check, just in case.
    num_episodes = response.get('num_episodes', 'Unknown')
    rating = response.get('mean', 'Unknown')

    anime_info = [f"Title: {anime_title}\n",
                  f"Episodes: {num_episodes}\n",
                  f"Rating: {rating}\n",
                  f"Season: {air_season}\n",
                  f"Aired: {air_date}"]
    anime_info = ''.join(anime_info)
    return anime_info

# Takes datetime and day of the week string and returns datetime that
# corresponds to next occurance of that day. If the day of the week
# given is the same as "today", then it returns "today".
def nextDay(today, day):
    day_str = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
               'friday': 4, 'saturday': 5, 'sunday': 6}
    days = (day_str[day] - today.weekday()) % 7
    return today + timedelta(days=days)