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
warnings.filterwarnings('ignore')

import dash
import plotly.express as px
from dash import html
from dash import dcc
from dash import dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

# df = pd.read_excel("E:/Nibm/3rd year/Project/Dataset/feedback data.xlsx")
def dbConnection():
    sys.path.append("../model")
    from dbConnectivity import dbConnectivity
    connection  = dbConnectivity()
    return connection

def fetch_df():
    connection = dbConnection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM feedback")
    rows = cursor.fetchall()
    sub_df = pd.DataFrame(rows, columns = ["No", "College", "Date", "Grade", "Subject", "Feedback", "Status"])
    # sub_unique = sub_df["subject"].unique()
    return sub_df

df = fetch_df()
values = [df["Status"].value_counts()[-1], df["Status"].value_counts()[0], df["Status"].value_counts()[1]]
names = ["Negative", "Neutral", "Positive"]

fig = px.bar(x=names, y=values)
st.plotly_chart(fig, theme="streamlit", use_container_width=True)