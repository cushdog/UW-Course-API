from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "https://course-explorer-electric-boogaloo.vercel.app"]}})

DATABASE = 'courses.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    return conn

def course_pull_from_table(course_title):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM courses WHERE course_code = ?;"
    cursor.execute(query, (course_title,))
    results = cursor.fetchall()
    conn.close()
    if not results:
        return "Course not found"
    return results[0]

def subject_pull_from_table(subject):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM courses WHERE subject = ?;"
    cursor.execute(query, (subject,))
    results = cursor.fetchall()
    conn.close()
    if not results:
        return "Course not found"
    return results[0]

@app.route('/search', methods=['GET'])
def search():

    query = request.args.get('query')
    words = query.split()
    
    class_name, course_number = words[0].upper(), words[1]
    course_title = class_name + " " + course_number

    results = course_pull_from_table(course_title)

    return jsonify(results)

@app.route('/subject-search', methods=['GET'])
def search():

    query = request.args.get('query')
    words = query.split()
    
    subject = words[0].upper()

    results = subject_pull_from_table(subject)

    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)