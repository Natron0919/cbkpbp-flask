#%%
import cbkpbp
import pandas as pd
import psycopg2
from sqlalchemy import create_engine

engine = create_engine('postgresql+psycopg2://test:test@localhost:5432/cbkpbp')
engine.connect()
print(engine)

conferences = cbkpbp.getConferences()
# conferences

teams = cbkpbp.getTeams('southeastern')
id = None
# for i in range(0, len(teams)):
#     if teams[i]['team'] == team:
#         id = teams[i]['id']

for i in range(0, len(teams)):
    id = teams[i]['id']
    df = cbkpbp.getSeason(id)
    df.to_sql('plays', engine, if_exists= 'append')
# %%
# import cbkpbp
# di = cbkpbp.getPage(222745)
# df = cbkpbp.getpbp(di)
# df.head()
# %%
