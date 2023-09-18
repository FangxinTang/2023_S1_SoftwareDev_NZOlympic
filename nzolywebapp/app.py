from flask import Flask, flash
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect

app = Flask(__name__)

dbconn = None
connection = None

##################################### Utility Functions ###################################
def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn

def getMembers():
    cur=getCursor()
    cur.execute("select * from members")
    results=cur.fetchall()
    return results

def getTeams():
    cur=getCursor()
    cur.execute("select * from teams")
    results=cur.fetchall()
    return results

def getEvents():
    cur=getCursor()
    cur.execute("select * from events")
    results=cur.fetchall()
    return results

def getEventStages():
    cur=getCursor()
    cur.execute("select * from event_stage")
    results=cur.fetchall()
    return results

def getEventStageResults():
    cur=getCursor()
    cur.execute("select * from event_stage_results")
    results=cur.fetchall()
    return results

def getResults():
    cur=getCursor()
    cur.execute("select * from results")
    results=cur.fetchall()
    return results

########################################################################################
#### Alter the event stage table to make the StageID auto-increment
# cursor = getCursor()
# alter_query = "ALTER TABLE event_stage MODIFY StageID INT AUTO_INCREMENT"
# cursor.execute(alter_query)


### Create a new table results showing member details + stage info and results
# create_cur = getCursor()
# create_query = """
# CREATE TABLE results AS
# SELECT DISTINCT subquery.StageID, es.StageName, es.Qualifying, subquery.MemberID, subquery.FirstName, subquery.LastName, subquery.PointsScored, subquery.Position
# FROM (
#     SELECT m.MemberID, m.FirstName, m.LastName, t.TeamName, e.EventName, esr.PointsScored, esr.Position, esr.StageID
#     FROM members m
#     LEFT JOIN teams t ON m.TeamID = t.TeamID
#     LEFT JOIN events e ON m.TeamID = e.NZTeam
#     LEFT JOIN event_stage_results esr ON m.MemberID = esr.MemberID
# ) AS subquery
# LEFT JOIN event_stage es ON subquery.StageID = es.StageID; 
# """
# create_cur.execute(create_query)



########################################### public  #####################################
@app.route("/")
def home():
    return render_template("base.html")


@app.route("/listmembers")
def listmembers():
    connection = getCursor()
    sql ="""
    SELECT m.MemberID, t.TeamName, CONCAT(m.FirstName, ' ', m.LastName) AS FullName,m.City, m.Birthdate 
    FROM members AS m 
    JOIN teams AS t ON m.TeamID = t.TeamID
    """
    connection.execute(sql)
    memberList = connection.fetchall()
    # print(memberList)
    return render_template("memberlist.html", memberlist = memberList) 


@app.route("/listevents")
def listevents():
    eventList = getEvents()
    return render_template("eventlist.html", eventlist = eventList)


@app.route("/athlete/<member_name>")   
# developing
def athlete_interface(member_name):
    return render_template("athlete.html", member_name = member_name)

################################### admin ###############################

@app.route("/admin/")
def admin():
    return render_template("admin.html")

#### search member function
@app.route("/admin/search")
def search():
    return render_template("admin/search.html")

@app.route("/admin/searchresults", methods=["GET","POST"])
def get_search_result():
    search_term = request.form.get('adminsearch')
    like_search_term = f'%{search_term}%'
    #seach members table
    member_cursor = getCursor()
    m_sql = "SELECT * FROM members WHERE members.FirstName LIKE %s OR members.LastName LIKE %s"
    member_cursor.execute(m_sql, (like_search_term, like_search_term,))
    member_search_results = member_cursor.fetchall()
    #search events table
    event_cursor =getCursor()
    e_sql = "SELECT * FROM events WHERE events.EventName LIKE %s"
    event_cursor.execute(e_sql,(like_search_term,))
    event_search_results = event_cursor.fetchall()
    return render_template("admin/searchresults.html", member_search_results=member_search_results, event_search_results=event_search_results)


### edit member function
@app.route("/admin/edit/", methods=["GET", "POST"])
def click_edit():
    return redirect(url_for('search'))

@app.route("/admin/edit/<member_id>", methods=["GET", "POST"])
def edit(member_id):
    all_member_details = getMembers()
    for member_details in all_member_details:
        # print(type(member_details[0]))
        # print(type(member_id))
        if str(member_details[0]) == member_id:
            member_to_be_edited = member_details[2] + " " + member_details[3]
    return render_template("/admin/edit.html", member_id=member_id, name=member_to_be_edited)

@app.route("/admin/editmemberresult/<member_id>", methods=["GET", "POST"])
def get_edit_result(member_id):
#get data from a Form, this form should lives in admin_edit.html, where a value member_id is passed into this page from search_result.html
    #data include TeamName(associate with value, first_name, last_name, city, birthdate)
    team_id = request.form.get("team_id")
    first_name_i = request.form.get("first_name")
    first_name=first_name_i.capitalize()
    last_name_i = request.form.get("last_name")
    last_name=last_name_i.capitalize()
    city_i = request.form.get("city")
    city=city_i.capitalize()
        #change the date format
    birthdate_str = request.form.get("birthdate")
    birthdate = None

    if birthdate_str is not None:
        birthdate_dt = datetime.strptime(birthdate_str, "%Y-%m-%d")
        birthdate = birthdate_dt.strftime("%Y-%m-%d")
    #update the data into members table
    mycursor = getCursor()
    sql = """
    update members 
    set TeamID =%s, FirstName=%s, LastName=%s, City=%s, Birthdate=%s 
    where MemberID = %s;
    """
    if team_id is not None and team_id != '':
        mycursor.execute(sql,(team_id, first_name, last_name, city, birthdate, member_id))
    return redirect(f"/listmembers")

### add member function
@app.route("/admin/add")
def add():
    teams=getTeams()
    return render_template("admin/add.html", teams=teams)

@app.route("/admin/showaddmember", methods=["GET", "POST"])
def get_add_result():
    member_id =request.form.get("member_id")
    team_id = request.form.get("team_id")
    first_name_input = request.form.get("first_name")
    first_name=first_name_input.capitalize()
    last_name_input = request.form.get("last_name")
    last_name=last_name_input.capitalize()
    city = request.form.get("city")
    birthdate_str = request.form.get("birthdate")
    if birthdate_str is not None:
        birthdate_dt = datetime.strptime(birthdate_str, "%Y-%m-%d")
        birthdate = birthdate_dt.strftime("%Y-%m-%d")  # Convert to date format
    mycursor = getCursor()
    sql = """
    INSERT INTO members (MemberID, TeamID, FirstName, LastName, City, Birthdate) 
    VALUES(%s,%s,%s,%s,%s,%s);
    """
    if team_id is not None and team_id != '':
        mycursor.execute(sql,(member_id, team_id, first_name, last_name, city, birthdate))
    return redirect("/listmembers")


### add event function
@app.route("/admin/add_event")
def add_event():
    #pass events,teams table to add_event template
    events=getEvents()
    teams=getTeams()
    return render_template("/admin/add_event.html", events=events, teams=teams)

@app.route("/admin/addeventresult", methods=["GET","POST"])
def get_addevent_result():
    event_name = request.form.get("event_name")
    sport = request.form.get("sport")
    nz_team = int(request.form.get("nz_team"))
    cursor = getCursor()
    sql = """
    INSERT INTO events (EventName, Sport, NZTeam) 
    VALUES (%s, %s, %s)
    """
    cursor.execute(sql, (event_name, sport, nz_team))
    return redirect("/listevents")


# add event stages function
@app.route("/admin/add_stage")
def add_stage():
    events=getEvents()
    return render_template("admin/add_stage.html",events=events)

@app.route("/admin/addeventstagesresults", methods=["GET","POST"])
def get_addstage_result():
    #get user input from "/add_eventstages"
    stage_name = request.form.get("stage_name")
    event_id = int(request.form.get("event_id"))
    location_input = request.form.get("location")
    location=location_input.capitalize()
    stage_date_str = request.form.get("stage_date")
    if stage_date_str is not None:
        stage_date_dt = datetime.strptime(stage_date_str, "%Y-%m-%d")
        stage_date = stage_date_dt.strftime("%Y-%m-%d")  # Convert to date format
    qualifying = request.form.get("qualifying")
    points_to_qualify = float(request.form.get("points_to_qualify"))
    #insert new row to event_stage table
    cur=getCursor()
    sql = """
    INSERT INTO event_stage (StageName, EventID, Location, StageDate, Qualifying, PointsToQualify) 
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cur.execute(sql, (stage_name, event_id, location, stage_date, qualifying, points_to_qualify))
    #fetch the updated event_stage table from mysql
    event_stages = getEventStages()
    return render_template("admin/addeventstagesresults.html", event_stages=event_stages)


#add scores and positions
@app.route("/admin/add_scores")
def add_scores():
    # pass event_stage to add_score form to get stage id     
    event_stages=getEventStages()
    return render_template("admin/add_scores.html", event_stages=event_stages)

@app.route("/admin/scores", methods=['POST'])
def scores():
    stage_id = int(request.form.get("stage_id"))
    points_scored = float(request.form.get("points_scored"))
    position = int(request.form.get("position"))
    event_stages = getEventStages()

    cur = getCursor()
    for row in event_stages:
        if row[5] == 1:
        # update scores and positions
            sql_update_scores_positions = """
            UPDATE event_stage_results
            SET PointsScored = %s, Position = %s
            WHERE StageID = %s
            """
            cur.execute(sql_update_scores_positions, (points_scored, position, stage_id))

        elif row[5] == 0:
            # Update scores only
            sql_update_scores_only = """
            UPDATE event_stage_results
            SET PointsScored = %s, Position = NULL
            WHERE StageID = %s
            """
            cur.execute(sql_update_scores_only, (points_scored, stage_id))
        break  # Exit the loop once the stage_id is found

    scores = getResults()   
    return render_template("admin/scores.html", scores=scores)



# Team Members Report
@app.route("/admin/team_members_report")
def get_team_members_report():
    cur = getCursor()
    sql = """
    select m.FirstName, m.LastName, t.TeamName
    from members m
    inner join teams t
    on m.TeamID = t.TeamID
    """
    cur.execute(sql)
    team_members_list = cur.fetchall()
    # Sort team members by last name, then first name, using lambda sort
    sorted_members = sorted(team_members_list, key=lambda x: (x[1], x[0]))
    return render_template("admin/team_members_report.html", team_members=sorted_members)


# Medal_Report
@app.route('/admin/medal_report')
def get_medal_report():
    cur = getCursor()
    sql = """
    SELECT esr.MemberID, m.FirstName, m.LastName, esr.Position as MedalClass
    FROM event_stage_results esr
    INNER JOIN members m
    ON esr.MemberID = m.MemberID
    """
    cur.execute(sql)
    medal_report_data = cur.fetchall()

    report_data = []
    medal_class = ""
    for event_result in medal_report_data:
        if event_result[3] == 1:
            medal_class = "Gold"
        elif event_result[3] == 2:
            medal_class  = "Silver"
        elif event_result[3] == 3:
            medal_class = "Bronze"
        else:
            medal_class = str(event_result[3])
        report_data.append((event_result[0], event_result[1], event_result[2], medal_class)) 

    gold_cur = getCursor()
    num_gold_sql = """
    SELECT COUNT(*) as Gold
    FROM event_stage_results
    WHERE Position = 1 
    """
    gold_cur.execute(num_gold_sql)
    result = gold_cur.fetchone()
    num_gold = result[0]


    silver_cur = getCursor()
    num_silver_sql = """
    SELECT COUNT(*) as Silver
    FROM event_stage_results
    WHERE Position = 2 
    """
    silver_cur.execute(num_silver_sql)
    result_s = silver_cur.fetchone()
    num_silver = result_s[0]


    bronze_cur = getCursor()
    num_bronze_sql = """
    SELECT COUNT(*) as Bronze
    FROM event_stage_results
    WHERE Position = 3 
    """
    bronze_cur.execute(num_bronze_sql)
    result_b = bronze_cur.fetchone()
    num_bronze = result_b[0]

    return render_template('admin/medal_report.html', data = report_data, num_gold=num_gold, num_silver=num_silver, num_bronze=num_bronze)
    

if __name__ == "__main__":
    app.run(debug=True)