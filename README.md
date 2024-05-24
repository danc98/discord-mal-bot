## Description
A basic Discord bot that allows users to poll the beta MAL API for anime information.  
Currently doesn't support OAuth requests that require authenticating your MAL account.

## Features
1. Search for anime by name.
2. Search for anime by ID.
3. Get a current anime rankings.
4. Get the current seasonal anime.
5. Get a random anime.
6. Get a given user's anime list.
7. Get the number of days before the next episode of a show (currently airing anime only).

## Setup
1. Written in Python 3.11.2, not tested in Python 2.0.
2. Run "python -m pip install -r requirements.txt" to install all modules.
3. Requires setting up a Discord bot and requesting a developer API key from MAL.  
 Discord Bot Setup: https://discordpy.readthedocs.io/en/stable/discord.html  
 MAL API Key Instructions: https://myanimelist.net/forum/?topicid=1973141  

## Using the Bot
1. Configure the .env file with the necessary keys.
 MAL: Client Secret, Client ID
 Discord: Discord Token, Guild ID
2. Run discordBot.py.

## Files
malApi.py - Interface program for MAL API.  
discordBot.py - Main Discord bot program.  
botHelper.py - Helper functions for the bot.  

## To-Do
Currently limited by the barebones information given by the MAL API.  
Primarily made for polling information, but a fork that allows you to update your anime list via the bot might be nice.
