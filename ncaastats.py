#%%

from turtle import home
from lxml import etree, html
import pandas as pd
import numpy as np
import requests
import re
import os.path
import time
import random
import json
import math

def open_html(path):
    with open(path, 'rb') as f:
        return f.read()
def save_html(html, path):
    with open(path, 'wb') as f:
        f.write(html)

# url = "https://stats.ncaa.org/game/play_by_play/5155038"

# res = requests.get(url, headers = {'User-Agent': 'Mozilla/5.0'})
# res.raise_for_status()
# site = html.fromstring(res.content)

#save_html(res.content, "C:/Github Projects/cbkpbp-flask/testpages/game.html")


def getRoster():
    # Collect rosters of teams
    url = "https://stats.ncaa.org/team/742/roster/15881"

    res = requests.get(url, headers = {'User-Agent': 'Mozilla/5.0'})
    res.raise_for_status()
    site = html.fromstring(res.content)

    # Placeholder for year
    year = 2021

    player_names = site.xpath("//*[@id='stat_grid']/tbody/tr/td[2]/a/text()")

    #Get player id from ncaa stats site
    player_ids = site.xpath("//*[@id='stat_grid']/tbody/tr/td[2]/a/@href")
    player_ids = [str(p) for p in player_ids]
    print(type(player_ids[0]))
    print(player_ids[0])

    # Isolate id from href attribute
    ids = []
    ids.extend([re.search("(?<=seq=)(\d+)", x).group(1) for x in player_ids])
    ids = [str(x) for x in ids]
    print(ids[0])

    # Get team id for the players
    team_id = []
    team_id.extend([re.search("(?<=org_id=)(\d+)", x).group(1) for x in player_ids])
    team_id = [str(x) for x in team_id]
    print(team_id)

    # Get Jersey numbers
    jersey_number = site.xpath("//*[@id='stat_grid']/tbody/tr/td[1]/text()")
    jersey_number = [int(x) for x in jersey_number]

    # Get Position
    position = site.xpath("//*[@id='stat_grid']/tbody/tr/td[3]/text()")
    position = [str(x) for x in position]

    # Get Class
    my_class = site.xpath("//*[@id='stat_grid']/tbody/tr/td[5]/text()")
    my_class = [str(x) for x in my_class]

    year = [year for x in player_ids]

    print(len(year))
    print(len(ids))
    print(len(player_names))
    print(len(my_class))
    print(len(position))
    print(len(jersey_number))
    print(len(team_id))

    di = {
        "year" : year,
        "player_id" : player_ids,
        "name" : player_names,
        "class" : my_class,
        "position" : position,
        "jersey_number" : jersey_number,
        "team_id" : team_id
    }

    df = pd.DataFrame(di)

    return df

def getTeams():
    url = "https://stats.ncaa.org/rankings?academic_year=2022&division=1&sport_code=MBB"

    res = requests.get(url, headers = {'User-Agent': 'Mozilla/5.0'})
    res.raise_for_status()
    site = html.fromstring(res.content)

    # TBD for later

# Get starters for a specific game (to use in final df)
def getStarters(game_id):

    url = "https://stats.ncaa.org/game/box_score/" + str(game_id)
    res = requests.get(url, headers = {'User-Agent': 'Mozilla/5.0'})
    res.raise_for_status()
    site = html.fromstring(res.content)


     #   3 and 7
    starters_away = site.xpath('//*[@id="contentarea"]/table[5]/tr[position() >= 3 and position() <= 7]/td[1]/a/text()')
    starters_home = site.xpath('//*[@id="contentarea"]/table[6]/tr[position() >= 3 and position() <= 7]/td[1]/a/text()')

    all_p_away = site.xpath('//*[@id="contentarea"]/table[5]/tr/td[1]/a/text()')
    all_p_home = site.xpath('//*[@id="contentarea"]/table[6]/tr/td[1]/a/text()')

    starters_away = [str(x).lower() for x in starters_away]
    starters_home = [str(x).lower() for x in starters_home]

    all_p_away = [str(x).lower() for x in all_p_away]
    all_p_home = [str(x).lower() for x in all_p_home]

    starters_away = [x.split(", ")[1] + " " + x.split(", ")[0] for x in starters_away]
    starters_home = [x.split(", ")[1] + " " + x.split(", ")[0] for x in starters_home]

    all_p_away = [x.split(", ")[1] + " " + x.split(", ")[0] for x in all_p_away]
    all_p_home = [x.split(", ")[1] + " " + x.split(", ")[0] for x in all_p_home]


    return starters_away, starters_home, all_p_away, all_p_home


# Get df of game data
def getGame():

    # Need to fix routing later for automation
    # url = "https://stats.ncaa.org/game/play_by_play/5155038"

    # res = requests.get(url, headers = {'User-Agent': 'Mozilla/5.0'})
    # res.raise_for_status()
    # site = html.fromstring(res.content)

    res = open_html("C:/Github Projects/cbkpbp-flask/testpages/game.html")
    site = html.fromstring(res)

    # Bring in starters for each team with getStarters() function
    ## MAKE SURE TO CHANGE THE ARGUMENT ONCE FINISHED!!
    lineup_away, lineup_home, all_p_away, all_p_home = getStarters("5155038")

    # Collect play-by-play data with direct XPATHS
    # Use this syntax to collect empty boxes as well
    time = [e.xpath('string()') for e in site.xpath('//html/body/div[2]/table[position() >= 6 and position() mod 2 = 0]/tr/td[1]')]
    team_away = [e.xpath('string()') for e in site.xpath('//html/body/div[2]/table[position() >= 6 and position() mod 2 = 0]/tr/td[2]')]
    score = [e.xpath('string()') for e in site.xpath('//html/body/div[2]/table[position() >= 6 and position() mod 2 = 0]/tr/td[3]')]
    team_home = [e.xpath('string()') for e in site.xpath('//html/body/div[2]/table[position() >= 6 and position() mod 2 = 0]/tr/td[4]')]

    # Remove extra time entries
    for x in range(len(team_away)):
        if "game start" in team_away[x] or "jumpball startperiod" in team_away[x] or "period start" in team_away[x] or "commercial" in team_away[x] or "end confirmed" in team_away[x]:
            time[x] = ""
    time = [x for x in time if x != ""]
    time = [x for x in time if x != "Time"]


    # Change team_away to strings and remove extra entries
    team_away = [str(x) for x in team_away]
    team_away = [x for x in team_away if "game start" not in x and "jumpball startperiod" not in x and "period start" not in x and "commercial" not in x and "end confirmed" not in x]
    team_away_name = team_away[0]
    team_away = [x for x in team_away if x != team_away_name]

    # Separate score to away and home
    score = [str(x) for x in score]
    score = [x for x in score if "Score" not in x]
    score_away = []
    score_home = []
    for x in score:
        score_away.append(x.split("-")[0])
        score_home.append(x.split("-")[1])

    # Change team_home to string and remove extra entries
    team_home = [str(x) for x in team_home]
    team_home_name = team_home[0]
    team_home = [x for x in team_home if x != team_home_name]

    # Combine play texts to one list
    play_text = [team_away[x] + team_home[x] for x in range(len(team_away))]
    play_text = [x.lower() for x in play_text]

    ##### MASSIVE RUN THRU OF play_text TO GET WHAT EACH PLAY ACTUALLY SYMBOLIZES


    p_away = []
    p_home = []

    for x in play_text:

        if any(player in x for player in lineup_away) and "substitution out" in x:
            p = x.split(",")[0].lower() # Isolate player being subbed
            print(p + " Subbed out")
            lineup_away.remove(p)
        if any(player in x for player in all_p_away) and "substitution in" in x:
            p = x.split(",")[0].lower() # Isolate player being subbed
            print(p + " Subbed in")
            lineup_away.append(p)     
        
        p_away.append(lineup_away)

    
   # for x in play_text:


    di = {
        "time" : time,
        "play_text" : play_text,
        "score_away" : score_away,
        "score_home" : score_home,
        "lineup_away" : p_away
    }

    df = pd.DataFrame(di)

    return p_away


# game_links gives URL to get to game
## For whatever reason the game_id is different here vs what's actually on the page
### This means we need to grab the correct link with actual_links
def getGameLinks(team_id):

    ### CHANGE THIS PROCESS WHEN FINALIZING
    res = open_html("C:/Users/nreeb/Documents/test/page2.html")
    site = html.fromstring(res)

    res = requests.get("https://stats.ncaa.org/teams/" + str(team_id))


    game_links = site.xpath('/html/body/div[2]/table/tr/td[1]/fieldset/table/tbody/tr/td[3]/a/@href')
    game_links = [str(x) for x in game_links]
    link_base = "https://stats.ncaa.org"
    actual_links = []
    ### EXPAND THIS WHEN FINALIZING SO IT DOESN'T JUST GET FIRST GAMES
    for x in game_links:
        res = requests.get(link_base + str(x), headers = {'User-Agent': 'Mozilla/5.0'})
        link = html.fromstring(res.content)
        id = link.xpath('/html/body/div[2]/div[3]/div/div/ul/li[3]/a/@href')
        actual_links.append(id[0])
        time.sleep(2)

    actual_links = [str(x) for x in actual_links]

    return actual_links

# Get team schedule for each year
## Site URL is structured in a way where a team has a different id for each year
### EX. Virginia Tech has a base id of 742 but for the 2021-2022 season their id is 527441
def getSchedulePages(team_id):

    ### CHANGE TO TAKE FUNCTION ARGUMENT team_id
    url = "https://stats.ncaa.org/teams/history/MBB/" + str(team_id)
    res = requests.get(url, headers = {'User-Agent': 'Mozilla/5.0'})
    site = html.fromstring(res.content)

    # Change position to however many years you'd like to grab
    year_link = site.xpath('//*[@id="team_history_data_table"]/tbody/tr[position() >= 2 and position() <= 4]/td[1]/a/@href')
    year_link = [str(x) for x in year_link]
    year_link = [re.search("(?<=teams/)(\d*)", x).group(1) for x in year_link]

    return year_link



# %%
### df.to_csv("C:/Github Projects/cbkpbp-flask/data/vtgame.csv", index=False)