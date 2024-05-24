# malApi.py
import requests
import os
from datetime import date, datetime
from dotenv import load_dotenv
load_dotenv()  # Load necessary keys.

class malAPI:

    def __init__(self):
        # Keys.
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.client_auth = {'X-MAL-CLIENT-ID': os.getenv("CLIENT_ID")}
        
        # Log file.
        today = date.today()
        log_date = today.strftime("%Y%m%d")
        self.log_file = f"{log_date}_api_log.txt"

        self.limit_cap = 20  # Limit param cap.

    # Returns id, name, and cover pictures of shows found in the query.
    def getAnime(self, search_query="", limit="100", offset="0"):
        # Numeric argument check.
        if self._checkNumericArgs(limit, offset) == False:
            return False
        
        # Limit cap.
        if int(limit) >= self.limit_cap:
            limit = self.limit_cap
        
        # Prepare request parts and send.
        url = "https://api.myanimelist.net/v2/anime"
        parameters = {}
        parameters["q"]      = str(search_query)
        parameters["limit"]  = str(limit)
        parameters["offset"] = str(offset)
        response = self._sendRequest(url, parameters)

        # Request failed.
        if response == False:
            return False

        # Extract each show found.
        response = response.json()
        formatted_response = []
        for anime in response["data"]:
            formatted_response.append(anime["node"])
        return formatted_response
    
    # Returns specific anime by ID given.
    # Pass fields to narrow results.
    def getAnimeByID(self, anime_id, fields=""):
        # Numeric argument check.
        if self._checkNumericArgs(anime_id) == False:
            return False
        
        # Default fields to return. Modify as needed.
        if fields == "":
            fields="id,title,main_picture,start_date,end_date,mean,num_episodes,start_season"
        
        # Prepare request parts and send.
        url = "https://api.myanimelist.net/v2/anime/" + str(anime_id)
        parameters = {}
        parameters["fields"] = str(fields)
        response = self._sendRequest(url, parameters)

        # Request failed.
        if response == False:
            return False
        
        response = response.json()
        return response
    
    # Get a list of the current anime rankings by ranking_type.
    def getAnimeRanking(self, ranking_type, limit="100", offset="0"):
        # Numeric argument check.
        if self._checkNumericArgs(limit, offset) == False:
            return False
        
        # Check ranking type.
        valid_ranking_types = ["all", "airing", "upcoming", "tv", "ova",
                               "movie", "special", "bypopularity", "favorite"]
        if ranking_type not in valid_ranking_types:
            self._writeToLog("Invalid ranking type.")
            return False
        
        # Limit cap.
        if int(limit) >= self.limit_cap:
            limit = self.limit_cap
        
        # Prepare request parts and send.
        url = "https://api.myanimelist.net/v2/anime/ranking"
        parameters = {}
        parameters["ranking_type"] = str(ranking_type)
        parameters["limit"]        = str(limit)
        parameters["offset"]       = str(offset)
        response = self._sendRequest(url, parameters)

        # Request failed.
        if response == False:
            return False

        # Extract each show found.
        response = response.json()
        formatted_response = []
        for anime in response["data"]:
            # Put the rank in with the anime data then append.
            anime["node"]["rank"] = anime["ranking"]["rank"]
            formatted_response.append(anime["node"])
        return formatted_response
    
    # Get a list of the seasonal anime specified.
    def getSeasonalAnime(self, year, season, sort="anime_score", limit="100", offset="0"):
        # Numeric argument check.
        if self._checkNumericArgs(year, limit, offset) == False:
            return False
        
        # Check season.
        season_types = ["winter", "spring", "summer", "fall"]
        if season not in season_types:
            self._writeToLog("Invalid season type.")
            return False
        
        # Check sort.
        if sort != "anime_score" and sort != "anime_num_list_users":
            self._writeToLog("Invalid sort type.")
            return False
        
        # Limit cap.
        if int(limit) >= self.limit_cap:
            limit = self.limit_cap
        
        # Prepare request parts and send.
        url = "https://api.myanimelist.net/v2/anime/season/" + str(year) + "/" + str(season).lower()
        parameters = {}
        parameters["sort"]   = str(sort)
        parameters["limit"]  = str(limit)
        parameters["offset"] = str(offset)
        response = self._sendRequest(url, parameters)

        # Request failed.
        if response == False:
            return False

        # Extract each show found.
        response = response.json()
        formatted_response = []
        for anime in response["data"]:
            formatted_response.append(anime["node"])
        return formatted_response
    
    # Get a specified user's anime list.
    def getUserAnimeList(self, user_name, status="", sort="anime_title", limit="100", offset="0"):
        # Numeric argument check.
        if self._checkNumericArgs(limit, offset) == False:
            return False
        
        # Limit cap.
        if int(limit) >= self.limit_cap:
            limit = self.limit_cap
        
        # Check status.
        if status != "":
            status_types = ["watching", "completed", "on_hold", "dropped", "plan_to_watch"]
            if status not in status_types:
                self._writeToLog("Invalid status type.")
                return False
            
        # Check sort.
        sort_types = ["list_score", "list_updated_at", "anime_title", "anime_start_date", "anime_id"]
        if sort not in sort_types:
            self._writeToLog("Invalid sort type.")
            return False
        
        # Prepare request parts and send.
        url = "https://api.myanimelist.net/v2/users/" + str(user_name) + "/animelist"
        parameters = {}
        parameters["fields"] = "list_status"
        parameters["status"] = str(status)
        parameters["sort"]   = str(sort)
        parameters["limit"]  = str(limit)
        parameters["offset"] = str(offset)
        response = self._sendRequest(url, parameters)

        # Request failed.
        if response == False:
            return False
        
        # Extract each show found.
        response = response.json()
        formatted_response = []
        for anime in response["data"]:
            # Merge anime info with list info.
            anime_info = anime["node"]
            anime_info["score"]      = anime["list_status"]["score"]
            anime_info["status"]     = anime["list_status"]["status"]
            anime_info["updated_at"] = anime["list_status"]["updated_at"]
            formatted_response.append(anime_info)      
        return formatted_response
    
    # Returns response on success, False on fail.
    def _sendRequest(self, url, parameters):
        r = requests.get(url, parameters, headers=self.client_auth)
        # Error handling.
        response_json = r.json()
        if r.status_code != 200:
            error_msg = f"{r.status_code}: {response_json['error']}\n"
            error_msg += f"URL: {url}\n"
            error_msg += f"Parameters: {parameters}\n"
            self._writeToLog(error_msg)
            return False
        return r
    
    # Writes error message to log file.
    def _writeToLog(self, *msgs):
        now = datetime.now()
        now = now.strftime("%Y/%m/%d %H:%M:%S")
        with open(self.log_file, "a") as log:
            for msg in msgs:
                log.write(f"[{now}] {msg}\n")

    # Checks that numeric arguments are numbers.
    def _checkNumericArgs(self, *args):
        for arg in args:
            # Floats/signed ints are never valid, so this is okay.
            arg = str(arg)
            if arg.isnumeric() == False and arg != "":
                error_msg = f"({arg}) must be a number."
                self._writeToLog(error_msg)
                return False
        return True