import os, platform
from flask import Flask, redirect, url_for, render_template, request
import json


def which_system():
	systems = [{'name': 'GFT-Tablet', 'root_path': r'C:\pythonCode'},
		 	   {'name': 'raspberrypi', 'root_path': r'/home/pi/pythonCode'},
			   {'name': 'Power', 'root_path': r'D:\pythonCode'},
			   {'name': 'all others', 'root_path': '/home/gfreundt/pythonCode'}]
	for system in systems:
		if system['name'] in platform.node():
			return system['root_path']
	return systems[-1]['root_path']


def construct_data(filename):
	with open(os.path.join(DATA_PATH, 'WEB_Venta.json'), mode='r') as file:
		data = json.load(file)
		details = data['details']
		details1, details2 = details[:len(details)//2], details[len(details)//2:]
		return data, details1, details2


DATA_PATH = os.path.join(which_system(), 'DolarPeru_data')
app = Flask(__name__)

@app.route("/venta")
def venta():
	data, details1, details2 = construct_data('WEB_Venta.json')
	return render_template('venta.html', head=data['head'], details1=details1, details2=details2)

@app.route("/compra")
def compra():
	data, details1, details2 = construct_data('WEB_Compra.json')
	return render_template('compra.html', head=data['head'], details1=details1, details2=details2)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

