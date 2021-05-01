import os
from flask import Flask, redirect, url_for, render_template, request
import updater
import datetime as dt
import time


def find_html_path():
    paths = (r"D:\Google Drive Backup\Multi-Sync\TipodeCambio", r"C:\users\gfreu\Google Drive\Multi-Sync\TipodeCambio")
    for path in paths:
        if os.path.exists(path):
            return path

MAIN_PATH = find_html_path()


app = Flask(__name__)

@app.route("/dog")
def index():
    latest = updater.main()
    latest = [f'{i[0]:.<30} {i[1]}    {i[2]}' for i in latest]
    return render_template('index.html', latest=latest)

#return render_template("dashboard.html", date=date, time=time, data=data)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
