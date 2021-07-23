import os, json, platform
from flask import Flask, redirect, url_for, render_template, request
from  google.cloud import storage


def which_system():
	systems = [{'name': 'GFT-Tablet', 'root_path': r'C:\pythonCode'},
		 	   {'name': 'raspberrypi', 'root_path': r'/home/pi/pythonCode'},
			   {'name': 'Power', 'root_path': r'D:\pythonCode'},
			   {'name': 'Ubuntu-gft', 'root_path': '/home/gabriel/pythonCode'},
			   {'name': 'all others', 'root_path': '/home/gabfre/pythonCode'}]
	for system in systems:
		if system['name'] in platform.node():
			return system['root_path']
	return systems[-1]['root_path']


def construct_data(filename):
	# Access Google Cloud Storage Bucket
	client = storage.Client.from_service_account_json(json_credentials_path=GCLOUD_KEYS)
	bucket = client.get_bucket('data-bucket-gft')
	file_in_bucket = bucket.blob('/DolarPeru_data/' + filename)
	data = json.loads(file_in_bucket.download_as_string().decode('utf-8'))
	details = data['details']
	details1, details2 = details[:len(details)//2], details[len(details)//2:]
	return data, details1, details2


ROOT_PATH = which_system()
SCRAPER_PATH = os.path.join(ROOT_PATH, 'DolarPeru_Scraper')
WEB_PATH = os.path.join(ROOT_PATH, 'DolarPeru_Web')
DATA_PATH = os.path.join(ROOT_PATH, 'DolarPeru_data')
GCLOUD_KEYS = os.path.join(ROOT_PATH, 'gcloud_keys.json')


app = Flask(__name__)

@app.route("/")
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

