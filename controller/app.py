import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os
import json
from openai import OpenAI
import warnings
import sys
import re
import dash
import plotly.express as px
import plotly.graph_objects as go
warnings.filterwarnings('ignore')


def dbConnection():
    sys.path.append("../model")
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

def getting_teacher(college):
    col_list = [college]
    connection = dbConnection()
    cursor = connection.cursor()
    query = "SELECT emp_no, name, designation FROM empdata WHERE location = %s"
    value = (col_list)
    cursor.execute(query, value)
    rows = cursor.fetchall()
    flt_df = pd.DataFrame(rows, columns= ["Emp_No", "Name", "Designation"])
    return flt_df

def fetch_feedback(college, grade, subject):
    college = college.split(" - ")[1].upper()
    grade = re.search(r'\d+', grade).group()
    search_list = [college, grade, subject]
    connection = dbConnection()
    cursor = connection.cursor()
    query = "SELECT college, grade, subject, feedback, status FROM feedback WHERE college = %s AND grade = %s AND subject = %s"
    cursor.execute(query, search_list)
    rows = cursor.fetchall()
    feedback_df = pd.DataFrame(rows, columns = ["College", "Grade", "Subject", "Feedback", "Status"])
    return feedback_df, rows

def fetch_feedback_for_otherViz(college):
    college = college.split(" - ")[1].upper()
    col_list = [college]
    connection = dbConnection()
    cursor = connection.cursor()
    query = "SELECT college, date, grade, subject, feedback, status FROM feedback WHERE college = %s"
    cursor.execute(query, col_list)
    rows = cursor.fetchall()
    feedback_df = pd.DataFrame(rows, columns = ["College", "Date", "Grade", "Subject", "Feedback", "Status"])
    return feedback_df


col_unique = unique_colleges()
sub_unique = unique_subjects()

college = st.sidebar.selectbox(
    "Choose the college", (col_unique),
    index=None,
    placeholder="Pick Your College",)

grade = st.sidebar.selectbox(
    "Select the Grade",
    ("Grade 6", "Grade 7", "Grade 8", "Grade 9", "Grade 10", "Grade 11"),
    index=None,
    placeholder="Grades from 6 to 11",
)

subject = st.sidebar.selectbox(
    "Select your subject", (sub_unique),
    index=None,
    placeholder="Select the subject that you want to enter feedback"
)


def titleLoading(college):
    college = college.split(" - ")[1].lower()
    if(college == "amb"):
        return "Ambalangoda College"
    elif(college == "amp"):
        return "Ampara College"
    elif(college == "anu"):
        return "Anuradhapura College"
    elif(college == "bad"):
        return "Badulla College"
    elif(college == "ban"):
        return "Bandarawela College"
    elif(college == "gal"):
        return "Galle College"
    elif(college == "gam"):
        return "Gampaha College"
    elif(college == "hor"):
        return "Horana College"
    elif(college == "kan"):
        return "Kandy College"
    elif(college == "keg"):
        return "Kegalle College"
    elif(college == "kir"):
        return "Kiribathgoda College"
    elif(college == "kul"):
        return "Kuliyapitiya College"
    elif(college == "kur"):
        return "kurunegala College"
    elif(college == "mal"):
        return "Malabe College"
    elif(college == "neg"):
        return "Negombo College"
    elif(college == "nug"):
        return "Nugegoda College"
    elif(college == "nuw"):
        return "Nuwara Eliya College"
    elif(college == "rat"):
        return "Rathnapura College"
    else:
        return "Wennappuwa College"
    
    
def visualizingDataTable(df, title):
    # getting the length of satatus column
    row_len = df.shape[0]
    unique_status = df["Status"].unique()
    len_unique_status = len(unique_status)
    if (len_unique_status == 1):
        msg = f"Data visualization of {title}"
        st.title(msg)
        values = []
        name = []
        if (unique_status[0] == 1):
            value = df[df["Status"] == 1].shape[0]
            values.append(value)
            name.append("Positive")
        elif(unique_status[0] == -1):
            value = df[df["Status"] == -1].shape[0]
            values.append(value)
            name.append("Negative")
        else:
            value = df[df["Status"] == 0].shape[0]
            values.append(value)
            name.append("Neutral")
        f_title = f"Feedback status for the grade {df.iloc[0,1]} and {df.iloc[0, 2]} subject"
        fig = px.bar(x=name, y=values, title=f_title)
        fig.update_xaxes(title="Feedback Status")
        fig.update_yaxes(title="Value Count")
        bar = st.plotly_chart(fig, theme="streamlit", use_container_width=True)
        return bar

    elif(len_unique_status == 2):
        msg = f"Data visualization of {title}"
        st.title(msg)
        values = []
        name = []
        # need to add netural nagative one
        if((unique_status[0] == 1 and unique_status[1] == -1) or (unique_status[0] == -1 and unique_status[1] == 1)):
            value = df[df["Status"] == 1].shape[0]
            values.append(value)

            value = df[df["Status"] == -1].shape[0]
            values.append(value)

            name.append("Positive")
            name.append("Negative")
        
        else:
            value = df[df["Status"] == 0].shape[0]
            values.append(value)

            value = df[df["Status"] == 1].shape[0]
            values.append(value)

            name.append("Neutral")
            name.append("Positive")
        f_title = f"Feedback status for the grade {df.iloc[0,1]} and {df.iloc[0, 2]} subject"
        fig = px.bar(x=name, y=values, title=f_title, color=["Electric Blue", "Orange"])
        fig.update_xaxes(title="Feedback Status")
        fig.update_yaxes(title="Value Count")
        fig.update_layout(showlegend=False)
        bar = st.plotly_chart(fig, theme="streamlit", use_container_width=True)
        return bar

    elif(len_unique_status >= 2):
        msg = f"Data visualization of {title}"
        st.title(msg)
        values = [df[df["Status"] == -1].shape[0], df[df["Status"] == 0].shape[0], df[df["Status"] == 1].shape[0]]
        name = ["Negative", "Neutral", "Positive"]
        f_title = f"Feedback status for the grade {df.iloc[0,1]} and {df.iloc[0, 2]} subject"
        fig = px.bar(x=name, y=values, title=f_title, color=["Electric Blue", "Neon Green", "Orange"])
        fig.update_xaxes(title="Feedback Status")
        fig.update_yaxes(title="Value Count")
        fig.update_layout(showlegend=False)
        bar = st.plotly_chart(fig, theme="streamlit", use_container_width=True)
        return bar
    
    else:
        msg = f"No any feedback for the {title}"
        return st.write(msg)
        # return f"No any feedback for the {title}"

def othervisulization(grade, subject, df):
    core_sub = ["English", "Mathematics", "Science", "GIT"]
    unique_sub = df["Subject"].unique()
    if ((core_sub[0] in unique_sub) and (core_sub[1] in unique_sub) and (core_sub[2] in unique_sub) and (core_sub[3] in unique_sub)):
        if (subject not in core_sub):
            for i in range(len(core_sub)):
                df_name = f"df_{i}"
                df_name = df[df["Subject"] == core_sub[i]]
                if (len(df_name["Status"].value_counts()) == 3):
                    values = [df_name["Status"].value_counts()[-1], df_name["Status"].value_counts()[0], df_name["Status"].value_counts()[1]]
                    names = ["Negative", "Neutral", "Positive"]
                    fig_title = f"Visualization of {core_sub[i]}"
                    fig = px.bar(x=names, y=values, title=fig_title, color=["Electric Blue", "Neon Green", "Orange"])
                    fig.update_xaxes(title="Feedback Status")
                    fig.update_yaxes(title="Value Count")
                    fig.update_layout(showlegend=False)
                    bar = st.plotly_chart(fig, theme="streamlit", use_container_width=True)

                elif(len(df_name["Status"].value_counts()) == 2):
                    uniqu_status = df_name["Status"].unique()
                    if((0 in uniqu_status) and (1 in uniqu_status)):
                        values = [df_name["Status"].value_counts()[0], df_name["Status"].value_counts()[1]]
                        names = ["Neutral", "Positive"]
                        fig_title = f"Visualization of {core_sub[i]}"
                        fig = px.bar(x=names, y=values, title=fig_title, color=["Electric Blue", "Neon Green"])
                        fig.update_xaxes(title="Feedback Status")
                        fig.update_yaxes(title="Value Count")
                        fig.update_layout(showlegend=False)
                        bar = st.plotly_chart(fig, theme="streamlit", use_container_width=True)
                    elif((-1 in uniqu_status) and (0 in uniqu_status)):
                        values = [df_name["Status"].value_counts()[-1], df_name["Status"].value_counts()[0]]
                        names = ["Negative", "Neutral"]
                        fig_title = f"Visualization of {core_sub[i]}"
                        fig = px.bar(x=names, y=values, title=fig_title, color=["Electric Blue", "Neon Green"])
                        fig.update_xaxes(title="Feedback Status")
                        fig.update_yaxes(title="Value Count")
                        fig.update_layout(showlegend=False)
                        bar = st.plotly_chart(fig, theme="streamlit", use_container_width=True)
                    else:
                        values = [df_name["Status"].value_counts()[-1], df_name["Status"].value_counts()[1]]
                        names = ["Negative", "Positive"]
                        fig_title = f"Visualization of {core_sub[i]}"
                        fig = px.bar(x=names, y=values, title=fig_title, color=["Electric Blue", "Neon Green"])
                        fig.update_xaxes(title="Feedback Status")
                        fig.update_yaxes(title="Value Count")
                        fig.update_layout(showlegend=False)
                        bar = st.plotly_chart(fig, theme="streamlit", use_container_width=True)
                elif(len(df_name["Status"].value_counts()) == 1):
                    uniqu_status = df_name["Status"].unique()
                    if(uniqu_status[0] == -1):
                        values = [df_name.shape[0]]
                        names = ["Negative"]
                        fig_title = f"Visualization of {core_sub[i]}"
                        fig = px.bar(x=names, y=values, title=fig_title, color=["Electric Blue"])
                        fig.update_xaxes(title="Feedback Status")
                        fig.update_yaxes(title="Value Count")
                        fig.update_layout(showlegend=False)
                        bar = st.plotly_chart(fig, theme="streamlit", use_container_width=True)
                    elif(uniqu_status[0] == 0):
                        values = [df_name.shape[0]]
                        names = ["Neutral"]
                        fig_title = f"Visualization of {core_sub[i]}"
                        fig = px.bar(x=names, y=values, title=fig_title, color=["Electric Blue"])
                        fig.update_xaxes(title="Feedback Status")
                        fig.update_yaxes(title="Value Count")
                        fig.update_layout(showlegend=False)
                        bar = st.plotly_chart(fig, theme="streamlit", use_container_width=True)
                    else:
                        values = [df_name.shape[0]]
                        names = ["Positive"]
                        fig_title = f"Visualization of {core_sub[i]}"
                        fig = px.bar(x=names, y=values, title=fig_title, color=["Electric Blue"])
                        fig.update_xaxes(title="Feedback Status")
                        fig.update_yaxes(title="Value Count")
                        fig.update_layout(showlegend=False)
                        bar = st.plotly_chart(fig, theme="streamlit", use_container_width=True)
                else:
                    return None
            return bar
        else:
            search_sub = subject
            index = core_sub.index(search_sub)
            del core_sub[index]
            for i in range(len(core_sub)):
                df_name = f"df_{i}"
                df_name = df[df["Subject"] == core_sub[i]]
                if (len(df_name["Status"].value_counts()) == 3):
                    values = [df_name["Status"].value_counts()[-1], df_name["Status"].value_counts()[0], df_name["Status"].value_counts()[1]]
                    names = ["Negative", "Neutral", "Positive"]
                    fig_title = f"Visualization of {core_sub[i]}"
                    fig = px.bar(x=names, y=values, title=fig_title, color=["Electric Blue", "Neon Green", "Orange"])
                    fig.update_xaxes(title="Feedback Status")
                    fig.update_yaxes(title="Value Count")
                    fig.update_layout(showlegend=False)
                    bar = st.plotly_chart(fig, theme="streamlit", use_container_width=True)

                elif(len(df_name["Status"].value_counts()) == 2):
                    uniqu_status = df_name["Status"].unique()
                    if((0 in uniqu_status) and (1 in uniqu_status)):
                        values = [df_name["Status"].value_counts()[0], df_name["Status"].value_counts()[1]]
                        names = ["Neutral", "Positive"]
                        fig_title = f"Visualization of {core_sub[i]}"
                        fig = px.bar(x=names, y=values, title=fig_title, color=["Electric Blue", "Neon Green"])
                        fig.update_xaxes(title="Feedback Status")
                        fig.update_yaxes(title="Value Count")
                        fig.update_layout(showlegend=False)
                        bar = st.plotly_chart(fig, theme="streamlit", use_container_width=True)
                    elif((-1 in uniqu_status) and (0 in uniqu_status)):
                        values = [df_name["Status"].value_counts()[-1], df_name["Status"].value_counts()[0]]
                        names = ["Negative", "Neutral"]
                        fig_title = f"Visualization of {core_sub[i]}"
                        fig = px.bar(x=names, y=values, title=fig_title, color=["Electric Blue", "Neon Green"])
                        fig.update_xaxes(title="Feedback Status")
                        fig.update_yaxes(title="Value Count")
                        fig.update_layout(showlegend=False)
                        bar = st.plotly_chart(fig, theme="streamlit", use_container_width=True)
                    else:
                        values = [df_name["Status"].value_counts()[-1], df_name["Status"].value_counts()[1]]
                        names = ["Negative", "Positive"]
                        fig_title = f"Visualization of {core_sub[i]}"
                        fig = px.bar(x=names, y=values, title=fig_title, color=["Electric Blue", "Neon Green"])
                        fig.update_xaxes(title="Feedback Status")
                        fig.update_yaxes(title="Value Count")
                        fig.update_layout(showlegend=False)
                        bar = st.plotly_chart(fig, theme="streamlit", use_container_width=True)
                elif(len(df_name["Status"].value_counts()) == 1):
                    uniqu_status = df_name["Status"].unique()
                    if(uniqu_status[0] == -1):
                        values = [df_name.shape[0]]
                        names = ["Negative"]
                        fig_title = f"Visualization of {core_sub[i]}"
                        fig = px.bar(x=names, y=values, title=fig_title, color=["Electric Blue"])
                        fig.update_xaxes(title="Feedback Status")
                        fig.update_yaxes(title="Value Count")
                        fig.update_layout(showlegend=False)
                        bar = st.plotly_chart(fig, theme="streamlit", use_container_width=True)
                    elif(uniqu_status[0] == 0):
                        values = [df_name.shape[0]]
                        names = ["Neutral"]
                        fig_title = f"Visualization of {core_sub[i]}"
                        fig = px.bar(x=names, y=values, title=fig_title, color=["Electric Blue"])
                        fig.update_xaxes(title="Feedback Status")
                        fig.update_yaxes(title="Value Count")
                        fig.update_layout(showlegend=False)
                        bar = st.plotly_chart(fig, theme="streamlit", use_container_width=True)
                    else:
                        values = [df_name.shape[0]]
                        names = ["Positive"]
                        fig_title = f"Visualization of {core_sub[i]}"
                        fig = px.bar(x=names, y=values, title=fig_title, color=["Electric Blue"])
                        fig.update_xaxes(title="Feedback Status")
                        fig.update_yaxes(title="Value Count")
                        fig.update_layout(showlegend=False)
                        bar = st.plotly_chart(fig, theme="streamlit", use_container_width=True)
                else:
                    return None
            return bar

    else:
        return None

if (college is not None) and (grade is not None) and (subject is not None):
    feedback_df, row = fetch_feedback(college, grade, subject)
    title = titleLoading(college)
    visualizingDataTable(feedback_df, title)
    otherViz = st.checkbox("Show other visualization")

    if (otherViz):
        otherVizDF = fetch_feedback_for_otherViz(college)
        othervisulization(grade, subject, otherVizDF)
        
else:
    st.write("Please select the visualization option in side bar")
    

