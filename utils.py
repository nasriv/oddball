import requests, html, pytz, os
from table2ascii import table2ascii, PresetStyle, Alignment
from datetime import datetime
import sqlite3

global pi_DBpath 
pi_DBpath = "/home/raspi-001/Documents/oddball/triviaBot.db"

global home_path
home_path = '/home/raspi-001/Documents/oddball'

def get_question():
    # pull question and return various string values in dict form for bot parsing
    try:
        r = requests.get('https://opentdb.com/api.php?amount=1&type=multiple')
        json_response = r.json()['results'][0]
    except:
        print("--- question API request error ---")

    # q_type = json_response['type']
    try:
        category = json_response['category'].split(': ')[1]
    except:
        category = json_response['category']
    question = html.unescape(json_response['question'])
    diff = json_response['difficulty']
    answer = html.unescape(json_response['correct_answer'])

    # if q_type == 'multiple':
    all_choices = json_response['incorrect_answers']
    all_choices.append(answer)
    clean_choices = []
    for item in all_choices:
        # replace all html entitiy tags
        clean_choices.append(html.unescape(item))

    # merge all answers into single string for function return
    all_choices = '\n'.join(clean_choices)

    # set point value based on ques. difficulty
    if diff == 'easy':
        point_val = 1
    elif diff == 'medium':
        point_val = 2
    elif diff == 'hard':
        point_val = 4

    # write value to db to track questions created
    try:
        insert_trivia_log(diff,category,point_val)
    except:
        print('error inserting to trivia log db')
        return {}

    return {
            "Category": str(category),  
            "Difficulty": str(diff),
            "point value": str(point_val),
            "q": str(question),
            "a": str(all_choices),
            "correctAns": str(answer)
            }
    
def add_score(user, points):
    conn = sqlite3.connect(pi_DBpath)
    c = conn.cursor()
    c.execute("UPDATE scoreboard set score=score+?, q_played=q_played+1, numCorr=numCorr+1 where name=?",(points, user))
    conn.commit()
    conn.close()

def add_game_data(user):
    conn = sqlite3.connect(pi_DBpath)
    c = conn.cursor()
    c.execute("UPDATE scoreboard set q_played=q_played+1 where name=?",(user,))
    conn.commit()
    conn.close()

def get_scores():

    import matplotlib.pyplot as plt

    conn = sqlite3.connect(pi_DBpath)
    c = conn.cursor()
    result = c.execute(
        '''select name as "Player", 
            cast(score as text) as "Pts", 
            case when q_played = 0 then cast(0 as TEXT)
                else cast(round(cast(numCorr as REAL)/q_played*100,0) as TEXT) 
                end as "%Corr", 
            cast(q_played as TEXT) as "Qs" 
            from scoreboard 
            order by score desc''')
    
    colHeaders = list(map(lambda x: x[0], c.description))
    response = result.fetchall()

    output = table2ascii(
        header = colHeaders,
        body=[list(row) for row in response],
        column_widths=[17,13,13,12],
        alignments=[Alignment.LEFT, Alignment.CENTER, Alignment.DECIMAL, Alignment.LEFT],
        style=PresetStyle.plain
    )

    players, points, corrRate, qPlayed = [],[],[],[]
    for item in response:
        players.append(item[0])
        points.append(float(item[1]))
        corrRate.append(float(item[2]))
        qPlayed.append(float(item[3]))

    print(players,points,corrRate, qPlayed)

    conn.close()

    # create chart
    filename = "score_chart.jpg"

    plt.rcdefaults()
    fig, ax = plt.subplots()

    # Example data
    ax.scatter(corrRate, points, s=qPlayed, label=players)
    ax.grid(alpha=0.15)
    ax.set_xlabel('% Questions Answered Correctly')
    ax.set_ylabel('Total Points')
    ax.set_title('Leaderboard')

    fig.savefig(os.path.join(home_path,filename), bbox_inches='tight', dpi=100)
    
    print(str(datetime.now())+" --- scoreboard chart created") 

    return output

def insert_trivia_log(difficulty, category, point_value):
    conn = sqlite3.connect(pi_DBpath)
    c = conn.cursor()
    c.execute('''
    insert into triviaLog
    (datetime, difficulty, category, point_value)
    values
    (?,?,?,?)
    ''',(str(datetime.now(pytz.timezone('US/Eastern'))),str(difficulty),str(category), point_value)
    )
    conn.commit()
    conn.close()

    print(datetime.now()," ---- added q to trivia log")

def get_question_chart():
    import matplotlib.pyplot as plt
    import numpy as np

    # load question data from triviaLog
    conn = sqlite3.connect(pi_DBpath)
    c = conn.cursor()
    response = c.execute(
        '''select 
        category,
        count(category)
        from triviaLog
        group by category;
    ''')

    count = []
    labels = []
    for item in response.fetchall():
        count.append(item[1])
        labels.append(item[0])

    conn.close()

    # create chart
    filename = "chart_question.jpg"

    plt.rcdefaults()
    fig, ax = plt.subplots()

    # Example data
    y_pos = np.arange(len(labels))
    ax.barh(y_pos, count)
    ax.set_yticks(y_pos, labels=labels)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Question Count')
    ax.set_title('Current Trivia Question Distribution')

    fig.savefig(os.path.join(home_path,filename), bbox_inches='tight', dpi=100)
    
    print(str(datetime.now())+" --- question chart created")

    return filename




#get_question()
# ----- testing --------
# print(get_scores())
# print(get_trivia_chart())
