import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime
import os
import json
from openai import OpenAI
import warnings
import sys
import re
import requests
warnings.filterwarnings('ignore')

# db connection
def dbConnection():
    sys.path.append("../../model")
    from dbConnectivity import dbConnectivity
    connection  = dbConnectivity()
    return connection

# Getting unique colleges names
def unique_colleges():
    connection = dbConnection()
    cursor = connection.cursor()
    cursor.execute("SELECT location FROM empdata")
    rows = cursor.fetchall()
    coll_df = pd.DataFrame(rows, columns = ["Colleges"])
    col_unique = coll_df["Colleges"].unique()
    return col_unique

# getting unique subjects
def unique_subjects():
    connection = dbConnection()
    cursor = connection.cursor()
    cursor.execute("SELECT subject FROM feedback")
    rows = cursor.fetchall()
    sub_df = pd.DataFrame(rows, columns = ["subject"])
    sub_unique = sub_df["subject"].unique()
    return sub_unique

# getting the chatgpt api key
def get_apikey():
    sys.path.append("../")
    from config import conf
    conf = conf()
    return conf

# prediction pipeline
def prediction(feedback):
    conf = get_apikey()
    client = OpenAI(api_key=conf["chat_gpt_api_kye"])
    common_text = "Sentiment analysis of the following test.Give me it positive, negative or neutral"
    completion = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-0125:personal::96Cz45g8",
        messages=[{"role": "user", "content": f"{common_text}:{feedback}"}], 
        max_tokens=1,
        temperature=0
        )
    feedbackPred = completion.choices[0].message.content
    return feedbackPred


# getting last 3 feedbacks   
def getting_last_feedback():
    connection = dbConnection()
    cursor = connection.cursor()
    cursor.execute("SELECT grade, subject, feedback, status FROM feedback")
    rows = cursor.fetchall()
    last_feedback = pd.DataFrame(rows, columns = ["Grade", "Subject", "Feedback", "Status"])
    last_feedback = last_feedback.tail(3)
    return last_feedback


# covert th numerical status into categorical
def status_conversion():
    df = getting_last_feedback()
    status_mapping = {-1: 'Negative', 0: 'Neutral', 1: 'Positive'}
    df['Status'] = df['Status'].replace(status_mapping)
    return df

def getting_date():
    response = requests.head('https://www.google.com')
    date_str = response.headers['Date']
    google_datetime = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
    google_date = google_datetime.date()
    return google_date

def feedbackstore(college_selection, grade_selection, subject_selection, feedback, feedbackPred):
    feedbackPred = feedbackPred.lower()
    college = college_selection.split(" - ")[1].upper()
    grade = re.search(r'\d+', grade_selection).group()
    date = getting_date()
    if (feedbackPred == "negative"):
        status = -1
    elif (feedbackPred == "positive"):
        status = 1
    else:
        status = 0
    connection = dbConnection()
    cursor = connection.cursor()
    insert_query = '''INSERT INTO feedback (college, date, grade, subject, feedback, status)
    VALUES (%s, %s, %s, %s, %s, %s)'''

    values = [college, date, grade, subject_selection, feedback, status]
    cursor.execute(insert_query, values)
    connection.commit()
    print("Record inserted successfully")
    return None


col_unique = unique_colleges()
sub_unique = unique_subjects()


st.title("EduFeedback Central")


college_selection = st.selectbox(
    "Choose the college", (col_unique),
    index=None,
    placeholder="choose Your College",)

grade_selection = st.selectbox(
    "Select the Grade",
    ("Grade 6", "Grade 7", "Grade 8", "Grade 9", "Grade 10", "Grade 11"),
    index=None,
    placeholder="Grades from 6 to 11",)

subject_selection = st.selectbox(
    "Select your subject", (sub_unique),
    index=None,
    placeholder="Select the subject that you want to enter feedback")

feedback = st.text_input('Enter your feedback here', 
                         placeholder='What you think about Sussex College')

feedbackPred = prediction(feedback)
if feedback:
    st.write("Your feedback: ", feedbackPred)
    feedbackstore(college_selection, grade_selection, subject_selection, feedback, feedbackPred)
    last_feedback = status_conversion()
    "### Last 3 feedback"
    last_feedback
