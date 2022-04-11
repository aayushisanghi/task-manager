from typing import List, Dict
import uuid
import mysql.connector
import simplejson as json
from flask import Flask, Response, request

app = Flask(__name__)

def get_db_connection():
    config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        'database': 'tasksdb'
    }
    connection = mysql.connector.connect(**config)
    return connection

def indexDb(task_id, title, is_completed, email) -> List[Dict]:
    connection = get_db_connection()
    cursor = connection.cursor()
    query = f'INSERT INTO tasks (id, title, is_completed, notify) VALUES ("{task_id}", "{title}", {is_completed}, "{email}")'
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()

def getTasksDb():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute('SELECT * FROM tasks')
    result = cursor.fetchall()
    
    cursor.close()
    connection.close()
    return result


@app.route('/v1/tasks', methods=['GET'])
def getTasks() -> str:
    js = json.dumps(getTasksDb())
    # TODO: make js in required format
    resp = Response(js, status=200, mimetype='application/json')
    return resp

@app.route('/v1/tasks', methods=['POST'])
def postTasks() -> str:
    data = request.get_json()
    task_id = str(uuid.uuid4())
    email = data['email']
    try:
        title = data['title']
        if 'is_completed' in data.keys():
            is_completed = data['is_completed']
        else:
            is_completed = 0
        print(title)
        print(is_completed)
        js = indexDb(task_id, title, is_completed, email)
        # resp = Response({'id':task_id}, status=201, mimetype='application/json')
        return {'id':task_id}, 201
    except:
        return {'error': 'Invalid JSON Body', 'status': 400}, 400
    
@app.route('/v1/tasks/<string:key>/', methods=['PUT'])
def UpdateByKey(key):
    data = request.get_json()
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    title = data['title']
    try:
        if 'is_completed' in data.keys():
            is_completed = data['is_completed']
            query = f'UPDATE tasks SET title = {title}, is_completed = {is_completed} WHERE id = {key}'
            cursor.execute(query)
        else:
            query = f'UPDATE tasks SET title = {title} WHERE id = {key}'
            cursor.execute(query)
        connection.commit()
        cursor.close()
        connection.close()
    except:
        cursor.close()
        connection.close()
        return {}, 200
    return {}, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
