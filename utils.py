import requests

def get_question():
    #pull question
    try:
        r = requests.get('https://opentdb.com/api.php?amount=1')
        json_response = r.json()['results'][0]

        q_type = json_response['type']
        category = json_response['category']
        question = json_response['question']
        diff = json_response['difficulty']
        answer = json_response['correct_answer']

        if q_type == 'multiple':
            all_choices = json_response['incorrect_answers']
            all_choices.append(answer)
            all_choices = '\n'.join(all_choices)
        else:
            all_choices = '\n'.join(['True', 'False'])

        if diff == 'easy':
            point_val = 3
        elif diff == 'medium':
            point_val = 5
        elif diff == 'hard':
            point_val = 10

        return {
                "Category": str(category),  
                "Difficulty": str(diff),
                "point value": str(point_val),
                "q": str(question),
                "a": str(all_choices),
                "ans": str(answer)
                }
        
    except:
        return 'error-trivia api'
    
def add_points():
    pass


get_question()
