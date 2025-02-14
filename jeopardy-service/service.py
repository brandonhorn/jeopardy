# middle_layer_service.py
import random
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import pyodbc
from azure.identity import DefaultAzureCredential
from index_settings import IndexSettings
from uploader import upload_next, upload_prev
from sql import sql_client

app = Flask(__name__)
CORS(app)
sql_client = sql_client()

# Database connection settings

settings = IndexSettings()

# API endpoint to add more recent episodes, GET request with takes optional url parameter 'count'
@app.route('/api/add_recent', methods=['GET'])
def add_recent():
    count = request.args.get('count')
    if count is None:
        count = 1
    else:
        count = int(count)
    upload_next(sql_client, settings, count)
    return jsonify({'message': 'Episodes uploaded successfully'})

@app.route('/api/add_past', methods=['GET'])
def add_past():
    count = request.args.get('count')
    if count is None:
        count = 1
    else:
        count = int(count)
    upload_prev(sql_client, settings, count)
    return jsonify({'message': 'Episodes uploaded successfully'})

@app.route('/api/question', methods=['GET'])
def get_question():
    id = random.randint(0, settings.get_question_count() - 1)
    question = sql_client.get_question(id)
    return jsonify(question)

@app.route('/api/player/0/clue', methods=['POST'])
def set_player_question():
    data = request.get_json()
    sql_client.update_player(0, data['clue_id'], data['value'], data['correct'])
    return jsonify({'message': 'Player question set successfully'})

@app.route('/api/player/create', methods=['POST'])
def create_player():
    data = request.get_json()
    sql_client.create_player(data['user_id'])
    return jsonify({'message': 'Player created successfully'})

@app.route('/api/player/init', methods=['GET'])
def init_player():
    sql_client.create_player_misses()
    return jsonify({'message': 'Player table initialized successfully'})

@app.route('/api/player/{id}/score', methods=['GET'])
def get_score(id):
    score = sql_client.get_player_coryat_score(id)
    return jsonify({'score': score})

@app.route('/api/questions', methods=['GET'])
def get_questions():
    user_id = request.args.get('user_id')
    
    # Get the Azure AD token
    credential = DefaultAzureCredential()
    token = credential.get_token("https://database.windows.net/").token

    # Create the connection string
    connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Authentication=ActiveDirectoryMsi;"

    # Connect to the database
    conn = pyodbc.connect(connection_string, attrs_before={pyodbc.SQL_COPT_SS_ACCESS_TOKEN: token})
    cursor = conn.cursor()

    # Fetch rows based on the user ID
    cursor.execute(f"SELECT * FROM {table_name} WHERE user_id = ?", user_id)
    rows = cursor.fetchall()

    # Convert rows to a list of dictionaries
    questions = []
    for row in rows:
        questions.append({
            'Category': row.Category,
            'Question': row.Question,
            'Value': row.Value,
            'Answer': row.Answer
        })

    # Close the connection
    cursor.close()
    conn.close()

    return jsonify(questions)




if __name__ == '__main__':
    app.run(debug=True)