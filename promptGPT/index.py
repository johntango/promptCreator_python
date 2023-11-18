# -----------------------
# you to install flask
#   pip install Flask
# -----------------------

# imports
from flask import Flask, render_template, request, redirect,jsonify
import openai
import sqlite3
import json
from openai import OpenAI

# connect to db and get cursor
connection = sqlite3.connect("data/prompts.db", check_same_thread=False)
cursor = connection.cursor()


# web application
app = Flask(__name__)
# add data to database
# this is where we read from the database
@app.route('/')
def index():
    list = cursor.execute("SELECT * FROM prompts").fetchall()
    return render_template('read.html', list=list)

# this is where we read from the database
@app.route('/createPrompt',methods=['GET'])
def create():
    msg = {"gptResponse":"Waiting for input"}
    return render_template('create.html', msg = msg)

@app.route('/sendGPT', methods=['GET'])
def ask_openai():
    # read api key from file openai_key.json
    with open('openai_key.json') as f:
        data = json.load(f)
    client = OpenAI(api_key=data['OPENAI_API_KEY']) # checked Nov 16 2023

    # get parameters from request
    style = request.args.get('style')
    tone = request.args.get('tone')
    language = request.args.get('language')
    topic = request.args.get('topic')
    prompt = "I am a " + style + " writer. I write in " + language + " and my tone is " + tone + ". I want to write a paragraph about " + topic + "."
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    print(completion.choices[0].message.content)
    answer = completion.choices[0].message.content
    msg = {"gptResponse":answer}
    write_to_db(topic, style, tone, language, prompt, answer)
    return render_template('create.html', msg = msg)


# this is where we write to the database
def write_to_db(topic, style, tone, language, prompt, response):
    connection = sqlite3.connect("data/prompts.db")
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO prompts VALUES
            (?, ?, ?, ?, ?, ?)
    ''', (topic, style, tone, language, prompt, response))
    
    connection.commit()
    # verify data
    rows = cursor.execute('SELECT * FROM prompts').fetchall()
    print(rows)
    
    
if __name__ == '__main__':
    app.run(debug=True, port=3000)