#%%

from flask import Flask, render_template, request, session, redirect, url_for
from flask.helpers import make_response
from sqlalchemy import alias, create_engine
# from flask_session import Session
import random
import pandas as pd
import ncaastats
app = Flask(__name__)

# Config stuff
app.config.from_pyfile('config.py')

# Credentials to database connection
hostname="localhost"
dbname="cbkpbp"
uname="test"
pwd="test"

engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(host=hostname, db=dbname, user=uname, pw=pwd))
connection = engine.connect()


@app.route("/")
def selectConference():
    con_list = pd.read_sql_query("""SELECT DISTINCT conference FROM team""", engine)
    conferences = [str(x) for x in con_list['conference']]
    conferences.sort()
    return render_template('index.html', conferences = conferences)

@app.route("/team", methods=['GET', 'POST'])
def selectTeam():
    if request.method == 'POST':
        conference = request.form['conferences']
        session['global_con'] = conference
        team_list = pd.read_sql_query("""SELECT team_name FROM team WHERE conference = %s""", engine, params=[conference])
        team_list = [str(x) for x in team_list['team_name']]
        team_list.sort()
        return render_template('team.html', teams = team_list, conference = conference)
    elif request.method == 'GET':
        return redirect(url_for('selectConference'))

@app.route("/data", methods=['GET', 'POST'])
def getData():
    if request.method == 'POST':
        team = request.form['teams']
        session['team_global'] = team
        conference = session.get('global_con', None)
        print(conference)
        print(team)
        pbp = pd.read_sql_query("""SELECT * FROM pbp WHERE team_away = %s OR team_home = %s""", engine, params=[team.strip(), team.strip()])
        team_id = pd.read_sql_query("""SELECT team_id FROM team WHERE team_name = %s""", engine, params=[team])
        team_id = team_id['team_id']
        team_id = str(team_id[0])
        print(team_id)
        four_di = ncaastats.getFour(pbp, team.strip())
        new_di = ncaastats.getStats(pbp, team.strip())
        roster = pd.read_sql_query("""SELECT name_mneumonic FROM player WHERE team_id = %s""", engine, params=[team_id])
        roster = [str(x) for x in roster['name_mneumonic']]
        session['roster_global'] = roster
    return render_template('data.html', team = team, conference = conference, new_di = new_di, four_di = four_di, roster = roster)


@app.route("/final", methods = ["GET", "POST"])
def filter():
    if request.method == "POST":
        team = session.get('team_global', None)
        pbp = pd.read_sql_query("""SELECT * FROM pbp WHERE team_away = %s OR team_home = %s""", engine, params=[team.strip(), team.strip()])
        roster = session.get("roster_global", None)
        conference = session.get("global_con", None)
        four_di_complete = ncaastats.getFour(pbp, team.strip())
        stat_di_complete = ncaastats.getStats(pbp, team.strip())
        players = [request.form.get('player1', None), request.form.get('player2', None), request.form.get('player3', None), request.form.get('player4', None), request.form.get('player5', None)]
        players = [x for x in players if x != '']
        session['players_latest'] = players
        df_filter = ncaastats.filterdf(pbp, players)



        four_di_filter = ncaastats.getFour(df_filter, team.strip())
        stat_di_filter = ncaastats.getStats(df_filter, team.strip())
        print(players)

    return render_template('final.html', team = team, conference = conference, roster = roster, four_di_complete = four_di_complete,
    four_di_filter = four_di_filter, stat_di_complete = stat_di_complete, stat_di_filter = stat_di_filter, 
    players = players)

@app.route("/downloadcsv")
def download_csv():
    team = session.get('team_global', None)
    pbp = pd.read_sql_query("""SELECT * FROM pbp WHERE team_away = %s OR team_home = %s""", engine, params=[team.strip(), team.strip()])
    df_filter = ncaastats.filterdf(pbp, session.get("players_latest", None))
    resp = make_response(df_filter.to_csv())
    resp.headers["Content-Disposition"] = "attachment; filename=filtered_data.csv"
    resp.mimetype='text/csv'

    return resp

@app.route("/downloadtotalcsv")
def download_totalcsv():
    team = session.get('team_global', None)
    pbp = pd.read_sql_query("""SELECT * FROM pbp WHERE team_away = %s OR team_home = %s""", engine, params=[team.strip(), team.strip()])
    resp = make_response(pbp.to_csv())
    resp.headers["Content-Disposition"] = "attachment; filename=complete_data.csv"
    resp.mimetype='text/csv'

    return resp




if __name__ == "__main__":
    app.run(debug=True)