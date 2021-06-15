from flask import Flask, render_template, request, session, redirect, url_for
import cbkpbp
app = Flask(__name__)
app.debug = True
app.secret_key = 'supersecretkey'

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
        conference = session.get('global_con', None)
        print(conference)
        print(team)
        di = cbkpbp.getTeams(conference)
        for i in range(0, len(di)):
            if di[i]['team'] == team:
                id = di[i]['id']
        if id == None:
            return 'Not a proper team selection'
        df = cbkpbp.getSeason(id)
        four_di = cbkpbp.getFour(df, team)
        new_di = cbkpbp.getStats(df, team)
        roster = cbkpbp.getRoster(id)
        four_di_filter = None
        if request.form.get('player1', None) != None:
            players = request.form['player1']
            df_filter = cbkpbp.filterdf(df, players)
            four_di_filter = cbkpbp.getFour(df_filter, team)
    return render_template('data.html', team = team, conference = conference, new_di = new_di, four_di = four_di, roster = roster, four_di_filter = four_di_filter)


if __name__ == "__main__":
    app.run(debug=True)