from multiprocessing import connection
from typing import List, Dict
import uuid
import mysql.connector
import simplejson as json
from flask import Flask, Response, request
from redis import Redis
from rq import Queue
from worker import send_simple_message

r = Redis(host='redis', port=6379)
queue = Queue(connection=r)

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
    resp = Response(js, status=200)
    return resp

@app.route('/v1/tasks/<string:key>', methods=['GET'])
def getByKey(key):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = f'SELECT * FROM tasks WHERE id = "{key}"'
    cursor.execute(query)
    result = cursor.fetchall()
    if result is None:
        cursor.close()
        connection.close()
        return {'error': 'Not Found', 'status': 404}, 404
    response = json.dumps(result)
    cursor.close()
    connection.close()
    return response, 200

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
        js = indexDb(task_id, title, is_completed, email)
        if is_completed == 1:
                job = queue.enqueue(send_simple_message, data['email'], title)
                return {'id':task_id, 'jobId': job.id}, 201
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
        if 'is_completed' in data:
            is_completed = data['is_completed']
            query = f'UPDATE tasks SET title = "{title}", is_completed = {is_completed} WHERE id = "{key}"'
            cursor.execute(query)
            connection.commit()
            if is_completed == 1:
                job = queue.enqueue(send_simple_message, data['email'], title)
                return {"jobId": job.id}, 200
        else:
            query = f'UPDATE tasks SET title = {title} WHERE id = "{key}"'
            cursor.execute(query)
            connection.commit()
        cursor.close()
        connection.close()
    except:
        cursor.close()
        connection.close()
        return {}, 200
    return {}, 200

@app.route('/v1/tasks/<string:key>/', methods=['DELETE'])
def DeleteByKey(key):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        query = f'DELETE FROM tasks WHERE id = "{key}"'
        cursor.execute(query)
        connection.commit()
        cursor.close()
        connection.close()
    except:
        return {}, 200
    return {}, 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
