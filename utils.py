import requests, html, pytz
from table2ascii import table2ascii, PresetStyle, Alignment
from datetime import datetime
import sqlite3

def get_question():
    # pull question and return various string values in dict form for bot parsing
    try:
        r = requests.get('https://opentdb.com/api.php?amount=1&type=multiple')
        json_response = r.json()['results'][0]
    except:
        print("--- question API request error ---")

    # q_type = json_response['type']
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
    conn = sqlite3.connect('triviaBot.db')
    c = conn.cursor()
    c.execute("UPDATE scoreboard set score=score+?, q_played=q_played+1, numCorr=numCorr+1 where name=?",(points, user))
    conn.commit()
    conn.close()

def add_game_data(user):
    conn = sqlite3.connect('triviaBot.db')
    c = conn.cursor()
    c.execute("UPDATE scoreboard set q_played=q_played+1 where name=?",(user,))
    conn.commit()
    conn.close()

def get_scores():
    conn = sqlite3.connect("triviaBot.db")
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

    conn.close()
    return output

def insert_trivia_log(difficulty, category, point_value):
    conn = sqlite3.connect("triviaBot.db")
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

def get_trivia_chart():
    #TODO Add in bar chart for some minor analytics or question distribution
    return "https://quickchart.io/chart?c={type:'line',data:{labels:['January','February','March','April','May'],datasets:[{label:'Dogs',data:[50,60,70,180,190],fill:false,borderColor:'blue'},{label:'Cats',data:[100,200,300,400,500],fill:false,borderColor:'green'}]}}"



#get_question()
# ----- testing --------
# print(get_scores())
