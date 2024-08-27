from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
import os
import re

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "https://course-explorer-electric-boogaloo.vercel.app", "https://course-explorer-electric-boogaloo1234567890098765434567890.vercel.app"]}})

DATABASE = 'courses.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    return conn

def clean_quarters_field(quarters):
    # Trim any leading/trailing whitespace
    quarters = quarters.strip()

    # Handle cases where "Not currently offered" is followed by some text
    not_offered_match = re.search(r'(Not currently offered)(.*)', quarters, re.IGNORECASE)
    if not_offered_match:
        # Extract the "Not currently offered" part and what comes after it
        not_offered_part = not_offered_match.group(1)
        following_text = not_offered_match.group(2).strip()
        if following_text:
            # Insert a comma between the two parts
            return f"{not_offered_part}, {following_text}"
        else:
            return not_offered_part

    # Define patterns for the common quarter terms
    quarter_patterns = {
        'Autumn': r'Autumn',
        'Winter': r'Winter',
        'Spring': r'Spring',
        'Summer': r'Summer',
        'Even Years': r'Even Years',
    }

    # Find all matching quarters
    found_quarters = []
    for name, pattern in quarter_patterns.items():
        if re.search(pattern, quarters, re.IGNORECASE):
            found_quarters.append(name)

    # Remove redundant or unnecessary text
    if found_quarters:
        quarters = ", ".join(found_quarters)
    else:
        quarters = "Not currently offered"  # Default if no quarters found

    return quarters

def clean_db_row(row):
    # Assuming the "sections" field is always the last index in the row
    row = list(row)

    quarters_index = 6  # Adjust based on your data's column index
    row[quarters_index] = clean_quarters_field(row[quarters_index])

    sections_data = row[-1]
    
    try:
        sections = json.loads(sections_data)  # Parse the string into a Python list
        for section in sections:
            if 'Enrollment Status' in section:
                enrollment_status = section['Enrollment Status']
                match = re.search(r'(\d+)\s+seats\s+available.*?(\d+)', enrollment_status)
                if match:
                    section['Enrollment Status'] = f"{match.group(1)}/{match.group(2)}"

            if 'Meeting Time & Location' in section:
                meeting_info = section['Meeting Time & Location']
                learning_format = re.search(r'(In-person|Online)', meeting_info)
                days_times = re.search(r'((M|T|W|Th|F)+)?(\d{1,2}:\d{2}\s*[APM]{2})\s*-\s*to\s*(\d{1,2}:\d{2}\s*[APM]{2})', meeting_info)
                location = re.search(r'(\w+)\s+building\s+room\s+(\w+)', meeting_info)
                if learning_format and days_times and location:
                    section['Learning Format'] = learning_format.group(1)
                    section['Meeting Times'] = f"{days_times.group(1)}, {days_times.group(3)}-{days_times.group(4)}"
                    section['Location'] = f"{location.group(1)} building, Room {location.group(2)}"
                    del section['Meeting Time & Location']

            if 'SLN' in section:
                sln = section['SLN']
                sln_number = re.search(r'\d+', sln)
                if sln_number:
                    section['SLN'] = sln_number.group(0)  # Just the number

        row[-1] = json.dumps(sections)  # Convert the cleaned list back to a JSON string

    except json.JSONDecodeError:
        print("Error decoding JSON for sections field")
    
    return tuple(row)

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
    return results

@app.route('/search', methods=['GET'])
def search():

    query = request.args.get('query')
    words = query.split()
    
    class_name, course_number = words[0].upper(), words[1]
    course_title = class_name + " " + course_number

    results = clean_db_row(course_pull_from_table(course_title))

    return jsonify(results)

@app.route('/subject-search', methods=['GET'])
def subjectSearch():

    query = request.args.get('query')
    words = query.split()
    
    subject = words[0].upper()

    results = subject_pull_from_table(subject)

    for result in results:
        temp = clean_db_row(result)
        result = temp

    return jsonify(results)

@app.route('/prof-search', methods=['GET'])
def profSearch():

    query = request.args.get('query')
    words = query.split()
    
    prof_name = words[0] + " " + words[1]

    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM courses WHERE sections LIKE ?;"
    cursor.execute(query, ('%' + prof_name + '%',))
    results = cursor.fetchall()
    conn.close()

    for result in results:
        temp = clean_db_row(result)
        result = temp

    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
