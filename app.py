from botocore.exceptions import ClientError
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from flask_cors import CORS
import requests
import sqlite3
import boto3
import json
import uuid
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "https://course-explorer-electric-boogaloo.vercel.app"]}})

DATABASE_CATALOG = 'catalog_courses.db'
DATABASE_SECTIONS = 'sections.db'

def get_catalog_db_connection():
    conn = sqlite3.connect(DATABASE_CATALOG)
    return conn

def get_sections_db_connection():
    conn = sqlite3.connect(DATABASE_SECTIONS)
    return conn

def pull_from_table_catalog(course_title):
    conn = get_catalog_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM courses WHERE course_code = ?;"
    cursor.execute(query, (course_title,))
    results = cursor.fetchall()
    conn.close()
    if not results:
        return "Course not found"
    return results[0]

def pull_from_table_sections(course_title):
    conn = get_sections_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM courses WHERE course_name LIKE ?;"
    cursor.execute(query, ('%' + course_title + '%',))
    results = cursor.fetchall()
    conn.close()
    if not results:
        return "Course not found"
    return results[0]

@app.route('/search-catalog', methods=['GET'])
def search():
    query = request.args.get('query')
    words = query.split()
    
    class_name, course_number = words[0].upper(), words[1]
    course_title = class_name + " " + course_number
    
    return jsonify(pull_from_table_catalog(course_title))

# if __name__ == '__main__':
#     app.run(debug=True)

print(pull_from_table_sections("MATH 102"))