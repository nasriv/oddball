import requests
import html
import sqlite3

def get_question():
    # pull question and return various string values in dict form for bot parsing
    try:
        r = requests.get('https://opentdb.com/api.php?amount=1&type=multiple')
        json_response = r.json()['results'][0]

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

        return {
                "Category": str(category),  
                "Difficulty": str(diff),
                "point value": str(point_val),
                "q": str(question),
                "a": str(all_choices),
                "correctAns": str(answer)
                }
        
    except:
        return 'error-trivia api'
    
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
                cast(score as text) as "Score", 
                case when q_played = 0 then cast(0 as TEXT)
                    else cast(round(cast(numCorr as REAL)/q_played*100,0) as TEXT) 
                    end as "% Correct", 
                cast(q_played as TEXT) as "Qs Answered" 
                from scoreboard 
                order by score desc''')
        
        colHeaders = tuple(map(lambda x: x[0], c.description))
        response = result.fetchall()
        response.insert(0,colHeaders)

        scores = []

        # convert from tuple to string
        for item in response:
            scores.append('\t'.join(item))

        conn.close()

        return scores

def question_counter():
    pass

def db_init():
    pass

#get_question()
# ----- testing --------
get_scores()
