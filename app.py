import os
from flask import Flask, redirect, url_for, render_template, request
import updater
import datetime as dt
import time


def find_path():
    paths = (r'C:\Users\Gabriel Freundt\Google Drive\Multi-Sync\tdcData\data',r"D:\Google Drive Backup\Multi-Sync\tdcData\data", r"C:\users\gfreu\Google Drive\Multi-Sync\tdcData\data")
    for path in paths:
        if os.path.exists(path):
            return path

MAIN_PATH = find_path()


app = Flask(__name__)

@app.route("/dog")
def index():
	with open(os.path.join(MAIN_PATH, 'TDC_fixed.txt'), mode='r') as file:
		latest = [i for i in file.readlines()]
		return render_template('index.html', latest=latest)

#return render_template("dashboard.html", date=date, time=time, data=data)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")


