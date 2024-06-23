import mysql.connector

def dbConnectivity():
    conn = mysql.connector.connect(
        host="127.0.0.1",
        database="sussexfeedbackanalysis",
        user="root",
        password=""
    )
    return conn