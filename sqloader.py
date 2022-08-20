#%%

### UPLOADER FOR player TABLE
from numpy import append
import pandas as pd
import ncaastats
import mysql.connector
from sqlalchemy import alias, create_engine

# Credentials to database connection
hostname="localhost"
dbname="cbkpbp"
uname="root"
pwd="profootballjokeswillmakeusmoney"


engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(host=hostname, db=dbname, user=uname, pw=pwd))
connection = engine.connect()

myresult = pd.read_sql('SELECT * FROM team WHERE conference = "WCC"', con=connection)

team_ids = myresult['team_id']

for x in team_ids:
    try:
        df = ncaastats.getRoster(x)
        df.to_sql("player", con=connection, if_exists="append", index=False)
        print("Roster loaded successfully")
    except Exception as e:
        print(e)
#%%

### UPLOADER FOR game TABLE

from numpy import append
import pandas as pd
import ncaastats
import mysql.connector
from sqlalchemy import create_engine

# Credentials to database connection
hostname="localhost"
dbname="cbkpbp"
uname="root"
pwd="profootballjokeswillmakeusmoney"


engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(host=hostname, db=dbname, user=uname, pw=pwd))
connection = engine.connect()

team_aliases_table = pd.read_sql('SELECT * FROM team_alias WHERE year = "2021" AND team_alias_id > 252', con=connection)

aliases = team_aliases_table['team_alias']


for y in aliases:
    links = ncaastats.getGameLinks(y)

    myresult = pd.read_sql('SELECT * FROM game', con=connection)
    existing_links = myresult['game_id']
    existing_links = [str(x) for x in existing_links]
    for x in links:
        if x not in existing_links:
            try:
                df = ncaastats.getGameInfo(x)
                df.to_sql("game", con=connection, if_exists="append", index=False)
                print("Successfully added game " + str(x) + " to game table")
            except Exception as e:
                print(e)
        else:
            print("Game " + str(x) + " already in database")



#%%

### UPLOADER FOR pbp TABLE

from numpy import append
import pandas as pd
import ncaastats
import mysql.connector
import time
from sqlalchemy import create_engine

# Credentials to database connection
hostname="localhost"
dbname="cbkpbp"
uname="root"
pwd="profootballjokeswillmakeusmoney"

year = 2021
year_col = []

engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(host=hostname, db=dbname, user=uname, pw=pwd))
connection = engine.connect()

myresult = pd.read_sql('SELECT * FROM game', con=connection)
games = [str(x) for x in myresult["game_id"]]

existing_games = pd.read_sql('SELECT DISTINCT game_id FROM pbp', con=connection)
e_games = [str(x) for x in existing_games['game_id']]

for x in games:
    if x not in e_games:
        try:
            df = ncaastats.getGame(x)
            df['lineup_away'] = [':'.join(x) for x in df['lineup_away']]
            df['lineup_home'] = [':'.join(x) for x in df['lineup_home']]
            df.to_sql("pbp", con=connection, if_exists="append", index=False)
            print("Game " + x + " was successfully loaded into database")
        except:
            print("Game " + x + " did not load into database")
    else:
        print("Game " + x + " already in database")




# %%

### UPLOADER FOR team_alias TABLE

from numpy import append
import pandas as pd
import ncaastats
import mysql.connector
import time
from sqlalchemy import create_engine

# Credentials to database connection
hostname="localhost"
dbname="cbkpbp"
uname="root"
pwd="profootballjokeswillmakeusmoney"

year = 2021
year_col = []

engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(host=hostname, db=dbname, user=uname, pw=pwd))
connection = engine.connect()

myresult = pd.read_sql('SELECT * FROM team', con=connection)

team_ids = myresult['team_id']

alias_id = []

for x in team_ids:
    thing = ncaastats.getYearlyTeamIds(x)
    alias_id.append(thing)
    year_col.append(year)
    print("Added " + str(x) + "to list")
    time.sleep(1)



# %%

### Testing

from numpy import append
import pandas as pd
import ncaastats
import mysql.connector
import time
from sqlalchemy import create_engine

# Credentials to database connection
hostname="localhost"
dbname="cbkpbp"
uname="root"
pwd="profootballjokeswillmakeusmoney"

year = 2021
year_col = []

engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(host=hostname, db=dbname, user=uname, pw=pwd))
connection = engine.connect()

team = 'Virginia Tech'
myresult = pd.read_sql_query("""SELECT * FROM pbp WHERE team_home = %s OR team_away = %s""", engine, params=[team, team])

# %%
