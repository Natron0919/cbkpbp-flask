#%%

from lxml import html
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

#res = requests.get('https://api.foxsports.com/bifrost/v1/cbk/event/223863/data?apikey=jE7yBJVRNAwdDesMgTzTXUUSx1It41Fq', headers = {'User-Agent': 'Mozilla/5.0','Content-Type' : 'application/json',})
#save_html(res.content, 'C:/Projects/playbyplay/tests/testcbkpage')


# sample_id = '223863'
# api_key = 'jE7yBJVRNAwdDesMgTzTXUUSx1It41Fq'
# url = 'https://api.foxsports.com/bifrost/v1/cbk/event/223863/data?apikey=jE7yBJVRNAwdDesMgTzTXUUSx1It41Fq'

# Returns list of conferences to select from
def getConferences():
    api_key = 'jE7yBJVRNAwdDesMgTzTXUUSx1It41Fq'
    base_url = 'https://api.foxsports.com/bifrost/v1/explore/browse/sports/cbk?apikey='
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Content-Type' : 'application/json',
    }
    res = requests.get(str(base_url) + str(api_key), headers = headers)
    res.raise_for_status()

    di = json.loads(res.content)


    conferences = []
    groups = []
    count = 0
    dic = {}
    for x in di['groups'][1]['items']:
        conferences.append(x['imageAltText'].lower())
        groups.append(x['uri'].split('group/')[1])

        con = x['imageAltText'].lower()
        gro = x['uri'].split('group/')[1]
        dic[count] = {'conference' : con, 'group' : gro}
        count += 1
    return dic

def getTeams(conference):
    di = getConferences()
    group = None
    for i in range(0, len(di)):
        if di[i]['conference'] == conference:
            group = di[i]['group']
    if group == None:
        return 'Not a proper conference selection'
    
    api_key = 'jE7yBJVRNAwdDesMgTzTXUUSx1It41Fq'
    url = 'https://api.foxsports.com/bifrost/v1/explore/browse/sports/cbk/group/' + str(group) + '?apikey='
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Content-Type' : 'application/json',
    }

    res = requests.get(str(url) + str(api_key), headers = headers)
    res.raise_for_status()

    di = json.loads(res.content)

    dic = {}
    count = 0
    for x in di['groups'][1]['items']:
        team = x['imageAltText'].lower()
        id = x['entityLink']['layout']['tokens']['id']
        dic[count] = {'team' : team, 'id' : id}
        count += 1

    return dic

def getIDS(team_id):
    # di = getConferences()
    # print('Conferences: \n')
    # for i in range(0, len(di)):
    #     print(di[i]['conference'])
    # con = input('Select a conference from the above list: ')
    # di = getTeams(con)
    # print('\n')
    # print('Teams: \n')
    # for i in range(0, len(di)):
    #     print(di[i]['team'])
    # team = input('Select a team from the above list: ')

    # id = None
    # for i in range(0, len(di)):
    #     if di[i]['team'] == team:
    #         id = di[i]['id']
    # if id == None:
    #     return 'Not a proper team selection'
    
    id = team_id
    api_key = 'jE7yBJVRNAwdDesMgTzTXUUSx1It41Fq'
    url = 'https://api.foxsports.com/bifrost/v1/cbk/team/' + str(id) + '/scores-segment/all?apikey='
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Content-Type' : 'application/json',
    }


    res = requests.get(str(url) + str(api_key), headers = headers)
    di = json.loads(res.content)

    games = []
    for x in di['sectionList']:
        for y in x['events']:
            if 'final' in y['statusLine'].lower():
                games.append(y['entityLink']['layout']['tokens']['id'])
    return games

def getSeason(id):
    games = getIDS(id)
    final_di = {}
    print('Team: ' + str(id))
    for i in range(0, len(games)):
        print('Loading game: ' + str(games[i]))
        try:
            if i == 0:
                di = getPage(game_id = games[i])
                df = getpbp(di)
                dic = df.to_dict(orient = 'list')
                final_di = dic
                time.sleep(random.randint(1, 10))
            else:
                di = getPage(game_id = games[i])
                df = getpbp(di)
                dic = df.to_dict(orient = 'list')
                for x in final_di.keys():
                    final_di[x].extend(dic[x])
                time.sleep(random.randint(1, 8))
        except:
            print('Game ' + str(games[i]) + ' failed to load')
    print('All games loaded')
    df = pd.DataFrame(final_di)
    df.insert(0, 'team_focus', str(id))

    
    return df






# Returns JSON of foxsports API which is used to gather all pbp data
def getPage(game_id = 'test', api_key = 'test'):

    # Test case which pulls local copy of a sample page
    if game_id == 'test' and api_key == 'test':
        res_content = open_html('C:/Projects/playbyplay/tests/testcbkpage')
        return json.loads(res_content)
    else:
        api_key = 'jE7yBJVRNAwdDesMgTzTXUUSx1It41Fq'
        base_url = 'https://api.foxsports.com/bifrost/v1/cbk/event/' + str(game_id) + '/data?apikey=' + str(api_key)
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type' : 'application/json',
        }
        res = requests.get(base_url, headers = headers)
        res.raise_for_status()
        if res.status_code == 200:
            return json.loads(res.content)
        else:
            return None

# Returns starters for each team to be used in lineup columns
def getStarters(di):
    s_away = []
    s_home = []
    away_starter_table = di['boxscore']['boxscoreSections'][0]['boxscoreItems'][0]['boxscoreTable']['rows']
    home_starter_table = di['boxscore']['boxscoreSections'][1]['boxscoreItems'][0]['boxscoreTable']['rows']

    # Cycle through box score table to get each teams starters
    for i in range(0, len(away_starter_table) - 1):
        s_away.append(away_starter_table[i]['entityLink']['title'].lower())
    for i in range(0, len(home_starter_table) - 1):
        s_home.append(home_starter_table[i]['entityLink']['title'].lower())

    return s_away, s_home

def getRoster(team_id):

    api_key = 'jE7yBJVRNAwdDesMgTzTXUUSx1It41Fq'
    url = 'https://api.foxsports.com/bifrost/v1/cbk/team/' + str(team_id) + '/roster?apikey='
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Content-Type' : 'application/json',
    }

    res = requests.get(url + api_key, headers = headers)
    di = json.loads(res.content)

    # return di
    players = []
    groups = di['groups']

    for x in range(0, len(groups) - 1):
        for y in di['groups'][x]['rows']:
            players.append(y['columns'][0]['text'].lower())

    return players



# def getAllPlayers(di):
#     p_away = []
#     p_home = []

#     away_player_table = di['boxscore']['boxscoreSections'][0]['boxscoreItems']
#     home_player_table = di['boxscore']['boxscoreSections'][1]['boxscoreItems']

#     for i in range(0, 2):
#         for j in range(0, len(away_player_table[i]['boxscoreTable']['rows']) - 1):
#             p_away.append(away_player_table[i]['boxscoreTable']['rows'][j]['entityLink']['title'].lower())
#         for j in range(0, len(home_player_table[i]['boxscoreTable']['rows']) - 1):
#             p_home.append(home_player_table[i]['boxscoreTable']['rows'][j]['entityLink']['title'].lower())

#     return p_away, p_home



# Returns df of pbp data
def getpbp(di):

    # Get starting lineups for each team
    lineup_away, lineup_home = getStarters(di)
    g_id = di['header']['id']
    g_date = di['header']['eventTime']
    g_date = g_date.split('T')[0]

    # Get mascot name (For rebounding stats)
    mascot_away = di['boxscore']['boxscoreSections'][0]['boxscoreItems'][2]['boxscoreTable']['rows'][0]['columns'][0]['text'].lower()

    mascot_home = di['boxscore']['boxscoreSections'][1]['boxscoreItems'][2]['boxscoreTable']['rows'][0]['columns'][0]['text'].lower()
    # Empty lists to fill later
    game_id = []
    game_date = []
    players_away = []
    players_home = []
    clock = []
    away_score = []
    home_score = []
    half = []
    plays = []
    poss_kindof = []
    prim_key = []
    cnt = 0

    # Pattern to be used on lineup change plays and get new players for each team
    lineup_pattern = r"\((.*?)\)"

    # Narrow page down to pbp data and not all the extra crap
    pbp = di['pbp']

    # Get meta data for game
    # away_team = pbp['sections'][0]['groups'][0]['leftTeamAbbr']
    at_list = []
    # home_team = pbp['sections'][0]['groups'][0]['rightTeamAbbr']
    ht_list = []

    # Used in lineup changes to match what team is subbing
    long_away_team = di['header']['leftTeam']['imageAltText'].lower()
    long_home_team = di['header']['rightTeam']['imageAltText'].lower()

    # Seperates games into sections (1st half, 2nd half, OT, etc.)
    periods = pbp['sections'][0]['groups']
    for i in range(0, len(periods)):

        # Get what period the game is in
        period_of_play = periods[i]['title']

        # Cycle through each play
        for x in periods[i]['plays']:

            # Get what team is in possession (NOT EXACTLY RIGHT ALL THE TIME)
            try:
                poss_kindof.append(x['imageAltText'].lower())
            except KeyError:
                poss_kindof.append('NULL')

            # General scraping for data and adding each entry to the appropriate list
            game_id.append(g_id)
            prim_key.append(str(g_id) + '_' + str(cnt))
            cnt += 1
            game_date.append(g_date)
            plays.append(x['playDescription'].lower())
            clock.append(x['timeOfPlay'])
            at_list.append(long_away_team)
            ht_list.append(long_home_team)
            half.append(period_of_play)

            # Update score for each team if necessary
            if x['leftTeamScoreChange'] == True:
                away_score.append(x['leftTeamScore'])
            else:
                away_score.append(np.nan)
            
            if x['rightTeamScoreChange'] == True:
                home_score.append(x['rightTeamScore'])
            else:
                home_score.append(np.nan)

            # Change lineups if substitution happens
            if 'lineup' in x['playDescription'].lower() and x['imageAltText'].lower() == long_away_team:
                players_a = re.search(lineup_pattern, x['playDescription'].lower()).group(1)
                lineup_away = players_a.split(', ')
            
            if 'lineup' in x['playDescription'].lower() and x['imageAltText'].lower() == long_home_team:
                players_h = re.search(lineup_pattern, x['playDescription'].lower()).group(1)
                lineup_home = players_h.split(', ')
            
            # Add updated lineups to the appropriate list
            players_away.append(lineup_away)
            players_home.append(lineup_home)

    # Get possession for real
    poss_for_real = []

    # Cycle through each play and fix possession where necessary
    for i in range(0, len(plays)):

        # EX. John Ojiako shooting foul (Jalen Johnson draws the foul)
        if 'foul' in plays[i] and 'offensive' not in plays[i]:
            if poss_kindof[i] == long_away_team:
                poss_for_real.append(long_home_team)
            elif poss_kindof[i] == long_home_team:
                poss_for_real.append(long_away_team)
            else:
                poss_for_real.append('NULL')
        elif 'blocks' in plays[i]:
            if poss_kindof[i] == long_away_team:
                poss_for_real.append(long_home_team)
            elif poss_kindof[i] == long_home_team:
                poss_for_real.append(long_away_team)
            else:
                poss_for_real.append('NULL')
        elif 'lineup' in plays[i]:
            poss_for_real.append('NULL')
        else:
            poss_for_real.append(poss_kindof[i])
    
    # Get poss in terms of home or away
    poss_team = []

    for i in range(0, len(poss_for_real)):
        if poss_for_real[i] == long_home_team:
            poss_team.append('home')
        elif poss_for_real[i] == long_away_team:
            poss_team.append('away')
        else:
            poss_team.append('NULL')

    # Get possession ID
    poss_id = []
    poss_id.append('0_' + str(g_id))
    poss_count = 1
    tip_off_winner = poss_for_real[1]
    for i in range(1, len(plays)):
        if poss_for_real[i] == tip_off_winner or poss_for_real[i] == 'NULL':
            poss_id.append(str(poss_count) + '_' + str(g_id))
        elif poss_for_real[i] != tip_off_winner and poss_for_real[i] != 'NULL':
            tip_off_winner = poss_for_real[i]
            poss_count += 1
            poss_id.append(str(poss_count) + '_' + str(g_id))

    # Fill out stat columns for each play

    #OFFENSIVE REBOUNDING

    o_reb_away = []
    o_reb_home = []


    for i in range(0, len(plays)):
        if 'offensive rebound' in plays[i] and mascot_away not in plays[i] and mascot_home not in plays[i]:
            if poss_for_real[i] == long_away_team:
                o_reb_away.append(True)
                o_reb_home.append(False)
            elif poss_for_real[i] == long_home_team:
                o_reb_away.append(False)
                o_reb_home.append(True)
        else:
            o_reb_away.append(False)
            o_reb_home.append(False)

    #DEFENSIVE REBOUNDING
    d_reb_away = []
    d_reb_home = []

    for i in range(0, len(plays)):
        if 'defensive rebound' in plays[i] and mascot_away not in plays[i] and mascot_home not in plays[i]:
            if poss_for_real[i] == long_away_team:
                d_reb_away.append(True)
                d_reb_home.append(False)
            elif poss_for_real[i] == long_home_team:
                d_reb_away.append(False)
                d_reb_home.append(True)
        else:
            d_reb_away.append(False)
            d_reb_home.append(False)

    # BLOCK
    block_away = []
    block_home = []

    for i in range(0, len(plays)):
        if 'blocks' in plays[i]:
            if poss_for_real[i] == long_away_team:
                block_away.append(True)
                block_home.append(False)
            elif poss_for_real[i] == long_home_team:
                block_away.append(False)
                block_home.append(True)

        else:
            block_away.append(False)
            block_home.append(False)

    # 2FG's
    two_fga_away = []
    two_fga_home = []
    two_fgm_away = []
    two_fgm_home = []

    for i in range(0, len(plays)):
        if 'misses two' in plays[i] or ('blocks' in plays[i] and 'two' in plays[i]):
            if poss_for_real[i] == long_away_team:
                two_fga_away.append(True)
                two_fga_home.append(False)

                two_fgm_away.append(False)
                two_fgm_home.append(False)
            elif poss_for_real[i] == long_home_team:
                two_fga_away.append(False)
                two_fga_home.append(True)


                two_fgm_away.append(False)
                two_fgm_home.append(False)
        elif 'makes two' in plays[i]:
            if poss_for_real[i] == long_away_team:
                two_fga_away.append(True)
                two_fga_home.append(False)

                two_fgm_away.append(True)
                two_fgm_home.append(False)
            elif poss_for_real[i] == long_home_team:
                two_fga_away.append(False)
                two_fga_home.append(True)

                two_fgm_away.append(False)
                two_fgm_home.append(True)
        else:
            two_fga_away.append(False)
            two_fga_home.append(False)
            two_fgm_away.append(False)
            two_fgm_home.append(False)


    # 3FG'S
    three_fga_away = []
    three_fga_home = []
    three_fgm_away = []
    three_fgm_home = []

    for i in range(0, len(plays)):
        if 'misses three' in plays[i] or ('blocks' in plays[i] and 'three' in plays[i]):
            if poss_for_real[i] == long_away_team:
                three_fga_away.append(True)
                three_fga_home.append(False)

                three_fgm_away.append(False)
                three_fgm_home.append(False)
            elif poss_for_real[i] == long_home_team:
                three_fga_away.append(False)
                three_fga_home.append(True)


                three_fgm_away.append(False)
                three_fgm_home.append(False)
        elif 'makes three' in plays[i]:
            if poss_for_real[i] == long_away_team:
                three_fga_away.append(True)
                three_fga_home.append(False)

                three_fgm_away.append(True)
                three_fgm_home.append(False)
            elif poss_for_real[i] == long_home_team:
                three_fga_away.append(False)
                three_fga_home.append(True)


                three_fgm_away.append(False)
                three_fgm_home.append(True)
        else:
            three_fga_away.append(False)
            three_fga_home.append(False)
            three_fgm_away.append(False)
            three_fgm_home.append(False)

    # FREE THROWS
    fta_away = []
    fta_home = []
    ftm_away = []
    ftm_home = []

    for i in range(0, len(plays)):
        if 'misses' in plays[i] and 'free throw' in plays[i] and 'violation' not in plays[i]:
            if poss_for_real[i] == long_away_team:
                fta_away.append(True)
                fta_home.append(False)
                ftm_away.append(False)
                ftm_home.append(False)
            elif poss_for_real[i] == long_home_team:
                fta_away.append(False)
                fta_home.append(True)
                ftm_away.append(False)
                ftm_home.append(False)
        elif 'makes' in plays[i] and 'free throw' in plays[i]:
            if poss_for_real[i] == long_away_team:
                fta_away.append(True)
                fta_home.append(False)
                ftm_away.append(True)
                ftm_home.append(False)
            elif poss_for_real[i] == long_home_team:
                fta_away.append(False)
                fta_home.append(True)
                ftm_away.append(False)
                ftm_home.append(True)
        else:
            fta_away.append(False)
            fta_home.append(False)
            ftm_away.append(False)
            ftm_home.append(False)



    # ASSISTS
    assist_away = []
    assist_home = []

    for i in range(0, len(plays)):
        if 'assists' in plays[i]:
            if poss_for_real[i] == long_away_team:
                assist_away.append(True)
                assist_home.append(False)
            elif poss_for_real[i] == long_home_team:
                assist_away.append(False)
                assist_home.append(True)
        else:
            assist_away.append(False)
            assist_home.append(False)

    # TO's
    to_away = []
    to_home = []

    for i in range(0, len(plays)):
        if 'turnover' in plays[i]:
            if poss_for_real[i] == long_away_team:
                to_away.append(True)
                to_home.append(False)
            elif poss_for_real[i] == long_home_team:
                to_away.append(False)
                to_home.append(True)
        else:
            to_away.append(False)
            to_home.append(False)


    # FOULS
    foul_away = []
    foul_home = []

    for i in range(0, len(plays)):
        if 'foul' in plays[i]:
            if poss_kindof[i] == long_away_team:
                foul_away.append(True)
                foul_home.append(False)
            elif poss_kindof[i] == long_home_team:
                foul_away.append(False)
                foul_home.append(True)
            else:
                foul_away.append(False)
                foul_home.append(False)
        else:
            foul_away.append(False)
            foul_home.append(False)





    # Combine all lists into dictionary format
    new_di = {
    'game_id' : game_id,
    'prim_key' : prim_key,
    'game_date' : game_date,
    'team_away' : at_list,
    'team_home' : ht_list,
    'players_away' : players_away,
    'players_home' : players_home,
    'score_away' : away_score,
    'score_home' : home_score,
    'clock' : clock,
    'period' : half,
    'poss_team' : poss_team,
    'poss_for_real' : poss_for_real,
    'poss_id' : poss_id,
    'play_text' : plays,
    'o_reb_away' : o_reb_away,
    'o_reb_home' : o_reb_home,
    'd_reb_away' : d_reb_away,
    'd_reb_home' : d_reb_home,
    '2fgm_away' : two_fgm_away,
    '2fga_away' : two_fga_away,
    '2fgm_home' : two_fgm_home,
    '2fga_home' : two_fga_home,
    '3fgm_away' : three_fgm_away,
    '3fga_away' : three_fga_away,
    '3fgm_home' : three_fgm_home,
    '3fga_home' : three_fga_home,
    'ftm_away' : ftm_away,
    'fta_away' : fta_away,
    'ftm_home' : ftm_home,
    'fta_home' : fta_home,
    'assist_away' : assist_away,
    'assist_home' : assist_home,
    'to_away' : to_away,
    'to_home' : to_home,
    'foul_away' : foul_away,
    'foul_home' : foul_home
    }

    # Set beginning score to 0-0
    away_score[0] = 0
    home_score[0] = 0

    # return new_di

    # Turn dictionary into DataFrame
    df = pd.DataFrame(new_di)

    # Front fill score columns since majority of entries are np.nan
    df['score_away'] = df['score_away'].fillna(method='ffill', axis=0)
    df['score_home'] = df['score_home'].fillna(method='ffill', axis=0)

    return df

def getStats(df, team):
    df_a = df[df['team_away'] == team]
    df_h = df[df['team_home'] == team]

    # 3FGM & 3FGA
    three_fgm_a = df_a[df_a['3fgm_away'] == True].shape[0]
    three_fgm_h = df_h[df_h['3fgm_home'] == True].shape[0]
    three_fgm = three_fgm_a + three_fgm_h
    three_fga_a = df_a[df_a['3fga_away'] == True].shape[0]
    three_fga_h = df_h[df_h['3fga_home'] == True].shape[0]
    three_fga = three_fga_a + three_fga_h

    # 2FGM & 2FGA
    fgm_a = df_a[df_a['2fgm_away'] == True].shape[0]
    fgm_h = df_h[df_h['2fgm_home'] == True].shape[0]
    fgm = fgm_a + fgm_h

    two_fga_a = df_a[df_a['2fga_away'] == True].shape[0]
    two_fga_h = df_h[df_h['2fga_home'] == True].shape[0]
    two_fga = two_fga_a + two_fga_h

    # TOTAL FGA
    fga_a = df_a[df_a['2fga_away'] == True].shape[0] + df_a[df_a['3fga_away'] == True].shape[0]
    fga_h = df_h[df_h['2fga_home'] == True].shape[0] + df_h[df_h['3fga_home'] == True].shape[0]
    fga = fga_a + fga_h

    # eFG%
    try:
        eFG = (1.5*three_fgm + fgm) / fga
        eFG = round(eFG*100, 2)
    except:
        eFG = 'N/A'

    # Turnovers
    to_a = df_a[df_a['to_away'] == True].shape[0]
    to_h = df_h[df_h['to_home'] == True].shape[0]
    to = to_a + to_h

    # Possessions Off. & Def.
    p_o_a = len(df_a[df_a['poss_for_real'] == team]['poss_id'].unique())
    p_o_h = len(df_h[df_h['poss_for_real'] == team]['poss_id'].unique())
    p_o = p_o_a + p_o_h

    p_d_a = len(df_a[(df_a['poss_for_real'] != team) & (df_a['poss_for_real'] != 'NULL')]['poss_id'].unique())
    p_d_h = len(df_h[(df_h['poss_for_real'] != team) & (df_h['poss_for_real'] != 'NULL')]['poss_id'].unique())
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

    ftm_a = df_a[df_a['ftm_away'] == True].shape[0]
    ftm_h = df_h[df_h['ftm_home'] == True].shape[0]
    ftm = ftm_a + ftm_h
    fta_a = df_a[df_a['fta_away'] == True].shape[0]
    fta_h = df_h[df_h['fta_home'] == True].shape[0]
    fta = fta_a + fta_h


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

    # print('')

    # print('2FGM: ' + str(fgm))
    # print('2FGA: ' + str(two_fga))
    # print('3FGM: ' + str(three_fgm))
    # print('3FGA: ' + str(three_fga))
    # print('FGA: ' + str(fga))
    # print('eFG% = ' + str(eFG * 100) + '% \n')

    # print('TO: ' + str(to))
    # print('TO% = ' + str(to_pct * 100) + '% \n')
    # print('Assists: ' + str(assist))

    # print('Off. Rebounds: ' + str(o_reb))
    # print('Def. Rebounds: ' + str(d_reb))
    # print('Opponent Off. Rebounds: ' + str(o_reb_opp))
    # print('Opponent Def. Rebounds: ' + str(d_reb_opp))
    # print('OR% = ' + str(or_pct * 100) + '% \n')

    # print('FTM: ' + str(ftm))
    # print('FTA: ' + str(fta))
    # print('FGA: ' + str(fga))
    # print('FTRate = ' + str(ftrate * 100) + '%')
    # print('\n')
    # print('Possessions_Off: ' + str(p_o))
    # print('Possessions_Def: ' + str(p_d))

    return new_di

def getFour(df, team):

    df_a = df[df['team_away'] == team]
    df_h = df[df['team_home'] == team]

    # Effective field goal percentage eFG% = (1.5*3fgm + 2fgm) / total_fga
    try:
        three_fgm_a = df_a[df_a['3fgm_away'] == True].shape[0]
        three_fgm_h = df_h[df_h['3fgm_home'] == True].shape[0]
        three_fgm = three_fgm_a + three_fgm_h

        fgm_a = df_a[df_a['2fgm_away'] == True].shape[0]
        fgm_h = df_h[df_h['2fgm_home'] == True].shape[0]
        fgm = fgm_a + fgm_h

        fga_a = df_a[df_a['2fga_away'] == True].shape[0] + df_a[df_a['3fga_away'] == True].shape[0]
        fga_h = df_h[df_h['2fga_home'] == True].shape[0] + df_h[df_h['3fga_home'] == True].shape[0]
        fga = fga_a + fga_h

        eFG = (1.5*three_fgm + fgm) / fga
        eFG = round(eFG*100, 2)
    except:
        eFG = 'N/A'

    # Turnover percentage TO% = TO / possessions 
    try:
        to_a = df_a[df_a['to_away'] == True].shape[0]
        to_h = df_h[df_h['to_home'] == True].shape[0]
        to = to_a + to_h

        p_o_a = len(df_a[df_a['poss_for_real'] == team]['poss_id'].unique())
        p_o_h = len(df_h[df_h['poss_for_real'] == team]['poss_id'].unique())
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
        fta_a = df_a[df_a['fta_away'] == True].shape[0]
        fta_h = df_h[df_h['fta_home'] == True].shape[0]
        fta = fta_a + fta_h

        fga_a = df_a[df_a['2fga_away'] == True].shape[0] + df_a[df_a['3fga_away'] == True].shape[0]
        fga_h = df_h[df_h['2fga_home'] == True].shape[0] + df_h[df_h['3fga_home'] == True].shape[0]
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

    # print('2FGM: ' + str(fgm))
    # print('3FGM: ' + str(three_fgm))
    # print('FGA: ' + str(fga))
    # print('eFG% = ' + str(eFG) + '% \n')

    # print('TO: ' + str(to))
    # print('TO% = ' + str(to_pct) + '% \n')

    # print('Off. Rebounds: ' + str(o_reb))
    # print('Opponent Def. Rebounds: ' + str(d_reb_opp))
    # print('OR% = ' + str(or_pct) + '% \n')

    # print('FTA: ' + str(fta))
    # print('FGA: ' + str(fga))
    # print('FTRate = ' + str(ftrate) + '%')
    # print('\n')
    # print('Possessions_Off: ' + str(p_o))
    # print('Possessions_Def: ' + str(p_d))

    return four_di

def filterdf(df, selection):
    if type(selection) != list:
        selection = [selection]

    mask = df.players_away.apply(lambda x: all(l in x for l in selection))
    df1 = df[mask]
    mask2 = df.players_home.apply(lambda x: all(l in x for l in selection))
    df2 = df[mask2]
    new_df = df1.append(df2)

    return new_df

# %%

# %%
