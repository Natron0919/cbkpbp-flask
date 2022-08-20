#%%

from turtle import home, pos
from lxml import etree, html
from datetime import datetime
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


def getRoster(id):
    # Collect rosters of teams
    url = "https://stats.ncaa.org/team/" + str(id) + "/roster/15881"

    res = requests.get(url, headers = {'User-Agent': 'Mozilla/5.0'})
    res.raise_for_status()
    site = html.fromstring(res.content)

    # Placeholder for year
    year = 2021

    ## OLD
    # player_names = site.xpath("//*[@id='stat_grid']/tbody/tr/td[2]/a/text()")
    # player_names = [str(x) for x in player_names]

    player_names = site.xpath("//*[@id='stat_grid']/tbody/tr/td[2]/descendant-or-self::*/text()")
    player_names = [str(x) for x in player_names]

    print(player_names)

    # Get player id from ncaa stats site
    player_ids = site.xpath("//*[@id='stat_grid']/tbody/tr/td[2]")
    ## OLD
    # player_ids = site.xpath("//*[@id='stat_grid']/tbody/tr/td[2]/a/@href")
    # player_ids = [str(p) for p in player_ids]
    player_ids = [str(html.tostring(x)) for x in player_ids]
    # print(type(player_ids[0]))
    # print(player_ids[0])

    # Isolate id from href attribute
    ids = []
    for x in player_ids:
        try:
            ids.append(re.search("(?<=seq=)(\d+)", x).group(1))
        except:
            ids.append("0")
    ids = [str(x) for x in ids]

    # Get team id for the players
    team_id = []
    team_id = [id for x in player_names]

    ## NOT NEEDED
    # team_id.extend([re.search("(?<=org_id=)(\d+)", x).group(1) for x in player_ids])
    # team_id = [str(x) for x in team_id]
    # print(team_id)

    # Get Jersey numbers
    jersey_number = site.xpath("//*[@id='stat_grid']/tbody/tr/td[1]/text()")
    jersey_number = [int(x) for x in jersey_number]

    # Get Position
    position = [e.xpath('string()') for e in site.xpath("//*[@id='stat_grid']/tbody/tr/td[3]")]
    position = [str(x) for x in position]

    # [e.xpath('string()') for e in site.xpath('//html/body/div[2]/table[position() >= 6 and position() mod 2 = 0]/tr/td[1]')]

    # Get Class
    my_class = site.xpath("//*[@id='stat_grid']/tbody/tr/td[5]/text()")
    my_class = [str(x) for x in my_class]

    games_played = site.xpath("//*[@id='stat_grid']/tbody/tr/td[6]/text()")
    games_played = [str(x) for x in games_played]

    games_started = site.xpath("//*[@id='stat_grid']/tbody/tr/td[7]/text()")
    games_started = [str(x) for x in games_started]

    year = [year for x in ids]

    # # Get rid of entries where 
    # for x in range(len(jersey_number)):
    #     if games_played[x] == "0" and games_started[x] == "0":
    #         my_class.pop(x)
    #         position.pop(x)
    #         jersey_number.pop(x)

    # print(len(year))
    # print(len(ids))
    # print(len(player_names))
    # print(len(my_class))
    # print(len(position))
    # print(len(jersey_number))
    # print(len(team_id))
    # print(len(games_played))
    # print(len(games_started))

    di = {
        "year" : year,
        "player_id" : ids,
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
def getGame(id):

    # Need to fix routing later for automation
    url = "https://stats.ncaa.org/game/play_by_play/" + str(id)

    res = requests.get(url, headers = {'User-Agent': 'Mozilla/5.0'})
    res.raise_for_status()
    site = html.fromstring(res.content)

    # res = open_html("C:/Github Projects/cbkpbp-flask/testpages/game.html")
    # site = html.fromstring(res)

    # Bring in starters for each team with getStarters() function
    ## MAKE SURE TO CHANGE THE ARGUMENT ONCE FINISHED!!
    lineup_away, lineup_home, all_p_away, all_p_home = getStarters(str(id))

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

    team_away_track = []
    team_home_track = []

    game_id = []

    p_away = []
    p_home = []

    two_pt_m_away = []
    two_pt_a_away = []
    three_pt_m_away = []
    three_pt_a_away = []

    two_pt_m_home = []
    two_pt_a_home = []
    three_pt_m_home = []
    three_pt_a_home = []

    ft_m_home = []
    ft_a_home = []
    
    ft_m_away = []
    ft_a_away = []

    d_reb_away = []
    o_reb_away = []

    d_reb_home = []
    o_reb_home = []

    assist_away = []
    assist_home = []

    turnover_away = []
    turnover_home = []

    foul_away = []
    foul_home = []

    steal_away = []
    steal_home = []

    team_in_poss = []
    poss_id = []
    poss_counter = 0

    game_and_poss = []

    for x in play_text:

        # Away team lineups
        if any(player in x for player in lineup_away) and "substitution out" in x:
            p = x.split(",")[0].lower() # Isolate player being subbed
            lineup_away.remove(p)
        if any(player in x for player in all_p_away) and "substitution in" in x:
            p = x.split(",")[0].lower() # Isolate player being subbed
            lineup_away.append(p)     
        players_away = [x for x in lineup_away] # Stupid necessity because the .remove() and .append() methods were changing every entry of p_away

        # Home team lineups
        if any(player in x for player in lineup_home) and "substitution out" in x:
            p = x.split(",")[0].lower() # Isolate player being subbed
            lineup_home.remove(p)
        if any(player in x for player in all_p_home) and "substitution in" in x:
            p = x.split(",")[0].lower() # Isolate player being subbed
            lineup_home.append(p)     
        players_home = [x for x in lineup_home] # Stupid necessity because the .remove() and .append() methods were changing every entry of p_away

        p_away.append(players_away)
        p_home.append(players_home)

        team_away_track.append(team_away_name)
        team_home_track.append(team_home_name)
        game_id.append(id)

    for x in play_text:
        # 2pt Away Team
        if "2pt" in x and any(player in x for player in all_p_away) and "made" in x:
            two_pt_m_away.append(True)
            two_pt_a_away.append(True)
        elif "2pt" in x and any(player in x for player in all_p_away) and "missed" in x:
            two_pt_m_away.append(False)
            two_pt_a_away.append(True)
        else:
            two_pt_m_away.append(False)
            two_pt_a_away.append(False)

        # 2pt Home Team
        if "2pt" in x and any(player in x for player in all_p_home) and "made" in x:
            two_pt_m_home.append(True)
            two_pt_a_home.append(True)
        elif "2pt" in x and any(player in x for player in all_p_home) and "missed" in x:
            two_pt_m_home.append(False)
            two_pt_a_home.append(True)
        else:
            two_pt_m_home.append(False)
            two_pt_a_home.append(False)

        # 3pt Away Team
        if "3pt" in x and any(player in x for player in all_p_away) and "made" in x:
            three_pt_m_away.append(True)
            three_pt_a_away.append(True)
        elif "3pt" in x and any(player in x for player in all_p_away) and "missed" in x:
            three_pt_m_away.append(False)
            three_pt_a_away.append(True)
        else:
            three_pt_m_away.append(False)
            three_pt_a_away.append(False)

        # 3pt Home Team
        if "3pt" in x and any(player in x for player in all_p_home) and "made" in x:
            three_pt_m_home.append(True)
            three_pt_a_home.append(True)
        elif "3pt" in x and any(player in x for player in all_p_home) and "missed" in x:
            three_pt_m_home.append(False)
            three_pt_a_home.append(True)
        else:
            three_pt_m_home.append(False)
            three_pt_a_home.append(False)

        # Free Throws Away Team
        if "freethrow" in x and any(player in x for player in all_p_away) and "made" in x:
            ft_m_away.append(True)
            ft_a_away.append(True)
        elif "freethrow" in x and any(player in x for player in all_p_away) and "missed" in x:
            ft_m_away.append(False)
            ft_a_away.append(True)
        else:
            ft_m_away.append(False)
            ft_a_away.append(False)
        
        # Free Throws Home Team
        if "freethrow" in x and any(player in x for player in all_p_home) and "made" in x:
            ft_m_home.append(True)
            ft_a_home.append(True)
        elif "freethrow" in x and any(player in x for player in all_p_home) and "missed" in x:
            ft_m_home.append(False)
            ft_a_home.append(True)
        else:
            ft_m_home.append(False)
            ft_a_home.append(False)

        # Rebounds Away Team
        if "rebound defensive" in x and any(player in x for player in all_p_away):
            d_reb_away.append(True)
        else:
            d_reb_away.append(False)
        
        if "rebound offensive" in x and any(player in x for player in all_p_away):
            o_reb_away.append(True)
        else:
            o_reb_away.append(False)

        # Rebounds Home Team
        if "rebound defensive" in x and any(player in x for player in all_p_home):
            d_reb_home.append(True)
        else:
            d_reb_home.append(False)
        
        if "rebound offensive" in x and any(player in x for player in all_p_home):
            o_reb_home.append(True)
        else:
            o_reb_home.append(False)

        # Assists
        if "assist" in x and any(player in x for player in all_p_away):
            assist_away.append(True)
        else:
            assist_away.append(False)
        
        if "assist" in x and any(player in x for player in all_p_home):
            assist_home.append(True)
        else:
            assist_home.append(False)

        # Turnovers
        if " turnover" in x and any(player in x for player in all_p_away):
            turnover_away.append(True)
        else:
            turnover_away.append(False)

        if " turnover" in x and any(player in x for player in all_p_home):
            turnover_home.append(True)
        else:
            turnover_home.append(False)

        # Fouls
        if "foul " in x and any(player in x for player in all_p_away):
            foul_away.append(True)
        else:
            foul_away.append(False)

        if "foul " in x and any(player in x for player in all_p_home):
            foul_home.append(True)
        else:
            foul_home.append(False)

        # Steals
        if ", steal" in x and any(player in x for player in all_p_away):
            steal_away.append(True)
        else:
            steal_away.append(False)

        if ", steal" in x and any(player in x for player in all_p_home):
            steal_home.append(True)
        else:
            steal_home.append(False)

        # Who has possession of the ball
        if "jumpball" in x or "substitution" in x:
            team_in_poss.append("NULL") 
        elif (any(player in x for player in all_p_away) and " block" not in x and "foul personal" not in x and "steal" not in x) or ((" block" in x or "foul personal" in x or "steal" in x) and any(player in x for player in all_p_home)):
            team_in_poss.append(team_away_name)
        elif (any(player in x for player in all_p_home) and " block" not in x and "foul personal" not in x and "steal" not in x) or ((" block" in x or "foul personal" in x or "steal" in x) and any(player in x for player in all_p_away)):
            team_in_poss.append(team_home_name)
        else:
            team_in_poss.append("NULL")


    # Possession ID
    for x in range(len(team_in_poss)):
        if team_in_poss[x] == "NULL":
            poss_id.append(poss_counter)
        elif team_in_poss[x] != team_in_poss[x-1]:
            poss_counter += 1
            poss_id.append(poss_counter)
        else:
            poss_id.append(poss_counter)

    # game_id + poss_id
    for x in poss_id:
        game_and_poss.append(str(id) + str(x))

    
    print(len(poss_id))
    print(len(play_text))

    di = {
        "game_id" : game_id,
        "time" : time,
        "team_away" : team_away_track,
        "team_home" : team_home_track,
        "play_text" : play_text,
        "team_in_poss" : team_in_poss,
        "poss_id" : poss_id,
        "game_and_poss" : game_and_poss,
        "score_away" : score_away,
        "score_home" : score_home,
        "lineup_away" : p_away,
        "lineup_home" : p_home,
        "2pt_made_away" : two_pt_m_away,
        "2pt_attempt_away" : two_pt_a_away,
        "2pt_made_home" : two_pt_m_home,
        "2pt_attempt_home" : two_pt_a_home,
        "3pt_made_away" : three_pt_m_away,
        "3pt_attempt_away" : three_pt_a_away,
        "3pt_made_home" : three_pt_m_home,
        "3pt_attempt_home" : three_pt_a_home,
        "ft_made_away" : ft_m_away,
        "ft_attempt_away" : ft_a_away,
        "ft_made_home" : ft_m_home,
        "ft_attempt_home" : ft_a_home,
        "d_reb_away" : d_reb_away,
        "o_reb_away" : o_reb_away,
        "d_reb_home" : d_reb_home,
        "o_reb_home" : o_reb_home,
        "assist_away" : assist_away,
        "assist_home" : assist_home,
        "turnover_away" : turnover_away,
        "turnover_home" : turnover_home,
        "foul_away" : foul_away,
        "foul_home" : foul_home,
        "steal_away" : steal_away,
        "steal_home" : steal_home
    }

    df = pd.DataFrame(di)

    return df

def getFour(df, team):

    df_a = df[df['team_away'] == team]
    df_h = df[df['team_home'] == team]

    # Effective field goal percentage eFG% = (1.5*3fgm + 2fgm) / total_fga
    try:
        three_fgm_a = df_a[df_a['3pt_made_away'] == True].shape[0]
        three_fgm_h = df_h[df_h['3pt_made_home'] == True].shape[0]
        three_fgm = three_fgm_a + three_fgm_h

        fgm_a = df_a[df_a['2pt_made_away'] == True].shape[0]
        fgm_h = df_h[df_h['2pt_made_home'] == True].shape[0]
        fgm = fgm_a + fgm_h

        fga_a = df_a[df_a['2pt_attempt_away'] == True].shape[0] + df_a[df_a['3pt_attempt_away'] == True].shape[0]
        fga_h = df_h[df_h['2pt_attempt_home'] == True].shape[0] + df_h[df_h['3pt_attempt_home'] == True].shape[0]
        fga = fga_a + fga_h

        eFG = (1.5*three_fgm + fgm) / fga
        eFG = round(eFG*100, 2)
    except:
        eFG = 'N/A'

    # Turnover percentage TO% = TO / possessions 
    try:
        to_a = df_a[df_a['turnover_away'] == True].shape[0]
        to_h = df_h[df_h['turnover_home'] == True].shape[0]
        to = to_a + to_h

        p_o_a = len(df_a[df_a['team_in_poss'] == team]['game_and_poss'].unique())
        p_o_h = len(df_h[df_h['team_in_poss'] == team]['game_and_poss'].unique())
        p_o = p_o_a + p_o_h

        # p_d_a = len(df_a[(df_a['poss_for_real'] != team) & (df_a['poss_for_real'] != 'NULL')]['poss_id'].unique())
        # p_d_h = len(df_h[(df_h['poss_for_real'] != team) & (df_h['poss_for_real'] != 'NULL')]['poss_id'].unique())
        # p_d = p_d_a + p_d_h

        to_pct = to / p_o
        to_pct = round(to_pct*100, 2)
    except:
        to_pct = 'N/A'

    # Offensive rebounding percentage OR% = OR / (OR + DR_opp)
    try:
        o_reb_a = df_a[df_a['o_reb_away'] == True].shape[0]
        o_reb_h = df_h[df_h['o_reb_home'] == True].shape[0]
        o_reb = o_reb_a + o_reb_h

        d_reb_opp_a = df_a[df_a['d_reb_home'] == True].shape[0]
        d_reb_opp_h = df_h[df_h['d_reb_away'] == True].shape[0]
        d_reb_opp = d_reb_opp_a + d_reb_opp_h

        or_pct = o_reb / (o_reb + d_reb_opp)
        or_pct = round(or_pct*100, 2)
    except:
        or_pct = 'N/A'


    # Free throw rate FTRate = FTA/FGA
    try:
        fta_a = df_a[df_a['ft_attempt_away'] == True].shape[0]
        fta_h = df_h[df_h['ft_attempt_home'] == True].shape[0]
        fta = fta_a + fta_h

        fga_a = df_a[df_a['2pt_attempt_away'] == True].shape[0] + df_a[df_a['3pt_attempt_away'] == True].shape[0]
        fga_h = df_h[df_h['2pt_attempt_home'] == True].shape[0] + df_h[df_h['3pt_attempt_home'] == True].shape[0]
        fga = fga_a + fga_h

        ftrate = fta/fga
        ftrate = round(ftrate*100, 2)
    except:
        ftrate = 'N/A'

    four_di = {
        'eFG%' : eFG,
        'TO%' : to_pct,
        'OR%' : or_pct,
        'FTRate' : ftrate
    }

    return four_di


### GET ALL STATS FROM A GIVEN DF FOR A SPECIFIC TEAM
def getStats(df, team):
    df_a = df[df['team_away'] == team]
    df_h = df[df['team_home'] == team]

    # 3FGM & 3FGA
    three_fgm_a = df_a[df_a['3pt_made_away'] == True].shape[0]
    three_fgm_h = df_h[df_h['3pt_made_home'] == True].shape[0]
    three_fgm = three_fgm_a + three_fgm_h
    three_fga_a = df_a[df_a['3pt_attempt_away'] == True].shape[0]
    three_fga_h = df_h[df_h['3pt_attempt_home'] == True].shape[0]
    three_fga = three_fga_a + three_fga_h

    # 2FGM & 2FGA
    fgm_a = df_a[df_a['2pt_made_away'] == True].shape[0]
    fgm_h = df_h[df_h['2pt_made_home'] == True].shape[0]
    fgm = fgm_a + fgm_h

    two_fga_a = df_a[df_a['2pt_attempt_away'] == True].shape[0]
    two_fga_h = df_h[df_h['2pt_attempt_home'] == True].shape[0]
    two_fga = two_fga_a + two_fga_h

    # TOTAL FGA
    fga_a = df_a[df_a['2pt_attempt_away'] == True].shape[0] + df_a[df_a['3pt_attempt_away'] == True].shape[0]
    fga_h = df_h[df_h['2pt_attempt_home'] == True].shape[0] + df_h[df_h['3pt_attempt_home'] == True].shape[0]
    fga = fga_a + fga_h

    # eFG%
    try:
        eFG = (1.5*three_fgm + fgm) / fga
        eFG = round(eFG*100, 2)
    except:
        eFG = 'N/A'

    # Turnovers
    to_a = df_a[df_a['turnover_away'] == True].shape[0]
    to_h = df_h[df_h['turnover_home'] == True].shape[0]
    to = to_a + to_h

    # Possessions Off. & Def.
    p_o_a = len(df_a[df_a['team_in_poss'] == team]['game_and_poss'].unique())
    p_o_h = len(df_h[df_h['team_in_poss'] == team]['game_and_poss'].unique())
    p_o = p_o_a + p_o_h

    p_d_a = len(df_a[(df_a['team_in_poss'] != team) & (df_a['team_in_poss'] != 'NULL')]['game_and_poss'].unique())
    p_d_h = len(df_h[(df_h['team_in_poss'] != team) & (df_h['team_in_poss'] != 'NULL')]['game_and_poss'].unique())
    p_d = p_d_a + p_d_h

    # Assists
    assist_a = df_a[df_a['assist_away'] == True].shape[0]
    assist_h = df_h[df_h['assist_home'] == True].shape[0]
    assist = assist_a + assist_h

    # Turnover %
    try:
        to_pct = to / p_o
        to_pct = round(to_pct*100, 2)
    except:
        to_pct = 'N/A'

    # Offensive rebounding & Defensive rebounding
    o_reb_a = df_a[df_a['o_reb_away'] == True].shape[0]
    o_reb_h = df_h[df_h['o_reb_home'] == True].shape[0]
    o_reb = o_reb_a + o_reb_h
    d_reb_a = df_a[df_a['d_reb_away'] == True].shape[0]
    d_reb_h = df_h[df_h['d_reb_home'] == True].shape[0]
    d_reb = d_reb_a + d_reb_h

    # Opponent Off. rebounding & Def. rebounding
    o_reb_opp_a = df_a[df_a['o_reb_home'] == True].shape[0]
    o_reb_opp_h = df_h[df_h['o_reb_away'] == True].shape[0]
    o_reb_opp = o_reb_opp_a + o_reb_opp_h
    d_reb_opp_a = df_a[df_a['d_reb_home'] == True].shape[0]
    d_reb_opp_h = df_h[df_h['d_reb_away'] == True].shape[0]
    d_reb_opp = d_reb_opp_a + d_reb_opp_h

    # Offensive rebounding %
    try:
        or_pct = o_reb / (o_reb + d_reb_opp)
        or_pct = round(or_pct*100, 2)
    except:
        or_pct = 'N/A'

    # FTM & FTA

    ftm_a = df_a[df_a['ft_made_away'] == True].shape[0]
    ftm_h = df_h[df_h['ft_made_home'] == True].shape[0]
    ftm = ftm_a + ftm_h
    fta_a = df_a[df_a['ft_attempt_away'] == True].shape[0]
    fta_h = df_h[df_h['ft_attempt_home'] == True].shape[0]
    fta = fta_a + fta_h

    # Steals

    steal_a = df_a[df_a['steal_away'] == True].shape[0]
    steal_h = df_h[df_h['steal_home'] == True].shape[0]
    steal = steal_a + steal_h


    try:
        ftrate = fta/fga
        ftrate = round(ftrate*100, 2)
    except:
        ftrate = 'N/A'

    new_di = {
        '2FGM' : fgm,
        '2FGA' : two_fga,
        '3FGM' : three_fgm,
        '3FGA' : three_fga,
        'FGA' : fga,
        'eFG%' : eFG,
        'TO' : to,
        'TO%' : to_pct,
        'Steals' : steal,
        'Assists' : assist,
        'OFF REB' : o_reb,
        'DEF REB' : d_reb,
        'OPP OFF REB' : o_reb_opp,
        'OPP DEF REB' : d_reb_opp,
        'OR%' : or_pct,
        'FTM' : ftm,
        'FTA' : fta,
        'FTRate' : ftrate,
        'Poss_O' : p_o,
        'Poss_D' : p_d
    }

    print('')

    print('2FGM: ' + str(fgm))
    print('2FGA: ' + str(two_fga))
    print('3FGM: ' + str(three_fgm))
    print('3FGA: ' + str(three_fga))
    print('FGA: ' + str(fga))
    print('eFG% = ' + str(eFG) + '% \n')

    print('TO: ' + str(to))
    print('TO% = ' + str(to_pct) + '% \n')
    print('Assists: ' + str(assist))
    print('Steals:' + str(steal))

    print('Off. Rebounds: ' + str(o_reb))
    print('Def. Rebounds: ' + str(d_reb))
    print('Opponent Off. Rebounds: ' + str(o_reb_opp))
    print('Opponent Def. Rebounds: ' + str(d_reb_opp))
    print('OR% = ' + str(or_pct) + '% \n')

    print('FTM: ' + str(ftm))
    print('FTA: ' + str(fta))
    print('FGA: ' + str(fga))
    print('FTRate = ' + str(ftrate) + '%')
    print('\n')
    print('Possessions_Off: ' + str(p_o))
    print('Possessions_Def: ' + str(p_d))

    return new_di


# game_links gives URL to get to game
## For whatever reason the game_id is different here vs what's actually on the page
### This means we need to grab the correct link with actual_links
def getGameLinks(team_id):

    ### CHANGE THIS PROCESS WHEN FINALIZING
    # res = open_html("C:/Users/nreeb/Documents/test/page2.html")
    # site = html.fromstring(res)

    res = requests.get("https://stats.ncaa.org/teams/" + str(team_id), headers = {'User-Agent': 'Mozilla/5.0'})
    site = html.fromstring(res.content)

    game_links = site.xpath('/html/body/div[2]/table/tr/td[1]/fieldset/table/tbody/tr/td[3]/a/@href')
    game_links = [str(x) for x in game_links]
    link_base = "https://stats.ncaa.org"
    actual_links = []

    ### EXPAND THIS WHEN FINALIZING SO IT DOESN'T JUST GET FIRST GAMES
    for x in game_links:
        res = requests.get(link_base + str(x), headers = {'User-Agent': 'Mozilla/5.0'})
        link = html.fromstring(res.content)
        id = link.xpath('/html/body/div[2]/div[3]/div/div/ul/li[3]/a/@href')
        if 'play_by_play' in str(id[0]):
            actual_links.append(id[0])
            print(id[0])
            time.sleep(1)
        else:
            print("Play by play data not available for game " + x)

    actual_links = [str(x) for x in actual_links]
    actual_links = [re.search("(?<=by_play\/)(\d*)", x).group(1) for x in actual_links]


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

def getGameInfo(game_id):

    url  = "https://stats.ncaa.org/game/play_by_play/" + str(game_id)
    res = requests.get(url, headers = {'User-Agent': 'Mozilla/5.0'})
    site = html.fromstring(res.content)


    game = []
    game.append(game_id)
    date = site.xpath('/html/body/div[2]/table[3]/tr[1]/td[2]/text()')
    team_away = site.xpath('/html/body/div[2]/table[6]/tr[1]/td[2]/text()')
    team_home = site.xpath('/html/body/div[2]/table[6]/tr[1]/td[4]/text()')
    score_away = site.xpath('/html/body/div[2]/table[1]/tr[2]/td[4]/text()')
    score_home = site.xpath('/html/body/div[2]/table[1]/tr[3]/td[4]/text()')

    date = [str(x) for x in date]
    date = [re.search("(\d{2}\/\d{2}\/\d{4})", x).group(1) for x in date]
    date = [datetime.strptime(x, r"%m/%d/%Y").strftime(r"%Y-%m-%d") for x in date]

    di = {
        "game_id" : game,
        "date" : date,
        "team_away" : team_away,
        "team_home" : team_home,
        "score_away" : score_away,
        "score_home" : score_home
    }

    df = pd.DataFrame(di)

    return df


def getYearlyTeamIds(id):

    url  = "https://stats.ncaa.org/teams/history/MBB/" + str(id)
    res = requests.get(url, headers = {'User-Agent': 'Mozilla/5.0'})
    site = html.fromstring(res.content)

    yearly_id = site.xpath('//*[@id="team_history_data_table"]/tbody/tr[2]/td[1]/a/@href')
    yearly_id = [str(x) for x in yearly_id]
    yearly_id = [re.search("(?<=teams/)(\d*)", x).group(1) for x in yearly_id]


    return yearly_id[0]

def filterdf(df, selection):
    if type(selection) != list:
        selection = [selection]

    mask = df.lineup_away.apply(lambda x: all(l in x for l in selection))
    df1 = df[mask]
    mask2 = df.lineup_home.apply(lambda x: all(l in x for l in selection))
    df2 = df[mask2]
    new_df = pd.concat([df1, df2])

    return new_df




# %%
### df.to_csv("C:/Github Projects/cbkpbp-flask/data/vtgame.csv", index=False)