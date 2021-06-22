from flask import Flask, render_template, request, session, redirect, url_for
from sqlalchemy import create_engine
import psycopg2
from flask_sqlalchemy import SQLAlchemy
# from flask_session import Session
import random
import pandas as pd
import cbkpbp
app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://test:test@localhost:5432/cbkpbp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

engine = create_engine('postgresql+psycopg2://test:test@localhost:5432/cbkpbp')
engine.connect()

# conn = psycopg2.connect(database='cbkpbp', user='test', password='test', host='localhost')
# mycursor = conn.cursor()
# SESSION_TYPE = 'sqlalchemy'
# Session(app)
rand_num = random.randint(0, 1000)
app.secret_key = 'supersecretkey' + str(rand_num)

class BasketballPlays(db.Model):
    __tablename__ = 'plays'
    index = db.Column(db.Integer)
    team_focus = db.Column(db.Integer, primary_key = True)
    game_id = db.Column(db.Integer)
    prim_key = db.Column(db.String, primary_key = True)
    game_date = db.Column(db.String)
    team_away = db.Column(db.String)
    team_home = db.Column(db.String)
    players_away = db.Column(db.String)
    players_home = db.Column(db.String)
    score_away = db.Column(db.Integer)
    score_home = db.Column(db.Integer)
    clock = db.Column(db.String)
    period = db.Column(db.String)
    poss_team = db.Column(db.String)
    poss_team = db.Column(db.String)
    poss_for_real = db.Column(db.String)
    poss_id = db.Column(db.String)
    play_text = db.Column(db.String)
    o_reb_away = db.Column(db.Boolean)
    o_reb_home = db.Column(db.Boolean)
    d_reb_away = db.Column(db.Boolean)
    d_reb_home = db.Column(db.Boolean)
    two_fgm_away = db.Column('2fgm_away', db.Boolean)
    two_fga_away = db.Column('2fga_away', db.Boolean)
    two_fgm_home = db.Column('2fgm_home', db.Boolean)
    two_fga_home = db.Column('2fga_home', db.Boolean)
    three_fgm_away = db.Column('3fgm_away', db.Boolean)
    three_fga_away = db.Column('3fga_away', db.Boolean)
    three_fgm_home = db.Column('3fgm_home', db.Boolean)
    three_fga_home = db.Column('3fga_home', db.Boolean)
    ftm_away = db.Column(db.Boolean)
    fta_away = db.Column(db.Boolean)
    ftm_home = db.Column(db.Boolean)
    fta_home = db.Column(db.Boolean)
    assist_away = db.Column(db.Boolean)
    assist_home = db.Column(db.Boolean)
    to_away = db.Column(db.Boolean)
    to_home = db.Column(db.Boolean)
    foul_away = db.Column(db.Boolean)
    foul_home = db.Column(db.Boolean)

    def __repr__(self):
        return '<BasketballPlays %r>' % self.team_focus


@app.route("/")
def selectConference():
    con_list = []
    conferences = cbkpbp.getConferences()
    for i in range(0, len(conferences)):
        con_list.append(conferences[i]['conference'])
    conferences = con_list
    return render_template('index.html', conferences = conferences)

@app.route("/team", methods=['GET', 'POST'])
def selectTeam():
    if request.method == 'POST':
        conference = request.form['conferences']
        session['global_con'] = conference
        teams = cbkpbp.getTeams(conference)
        team_list = []
        for i in range(0, len(teams)):
            team_list.append(teams[i]['team'])
        teams = team_list
        return render_template('team.html', teams = teams, conference = conference)
    elif request.method == 'GET':
        return redirect(url_for('selectConference'))

@app.route("/data", methods=['GET', 'POST'])
def getData():
    if request.method == 'POST':
        id = None
        team = request.form['teams']
        session['team_global'] = team
        conference = session.get('global_con', None)
        print(conference)
        print(team)
        di = cbkpbp.getTeams(conference)
        for i in range(0, len(di)):
            if di[i]['team'] == team:
                id = di[i]['id']
        if id == None:
            return 'Not a proper team selection'
        # df = cbkpbp.getSeason(id)
        session['id_global'] = id
        df = pd.read_sql_query("""SELECT * FROM public.plays WHERE team_focus = %s""", engine, params=[id])
        df_maybe = pd.read_sql(session.query(BasketballPlays).filter(BasketballPlays.team_focus == id).statement, session.bind)
        print(df_maybe.head())
        print(type(df_maybe))
        four_di = cbkpbp.getFour(df, team)
        new_di = cbkpbp.getStats(df, team)
        roster = cbkpbp.getRoster(id)
        session['roster_global'] = roster
    return render_template('data.html', team = team, conference = conference, new_di = new_di, four_di = four_di, roster = roster)

@app.route("/final", methods = ["GET", "POST"])
def filter():
    if request.method == "POST":
        id = session.get('id_global', None)
        df = pd.read_sql_query("""SELECT * FROM public.plays WHERE team_focus = %s""", engine, params=[id])
        roster = session.get("roster_global", None)
        team = session.get("team_global", None)
        conference = session.get("global_con", None)
        four_di_complete = cbkpbp.getFour(df, team)
        stat_di_complete = cbkpbp.getStats(df, team)
        players = [request.form.get('player1', None), request.form.get('player2', None), request.form.get('player3', None), request.form.get('player4', None), request.form.get('player5', None)]
        players = [x for x in players if x != '']
        df_filter = cbkpbp.filterdf(df, players)
        four_di_filter = cbkpbp.getFour(df_filter, team)
        stat_di_filter = cbkpbp.getStats(df_filter, team)
        print(players)

    return render_template('final.html', team = team, conference = conference, roster = roster, four_di_complete = four_di_complete,
    four_di_filter = four_di_filter, stat_di_complete = stat_di_complete, stat_di_filter = stat_di_filter)


if __name__ == "__main__":
    app.run(debug=True)