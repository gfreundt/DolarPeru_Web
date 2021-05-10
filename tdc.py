import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime as dt
from datetime import date as date
from datetime import timedelta as delta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as WebDriverOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import time
import csv
import os
from statistics import mean
import subprocess


class Basics:
	def __init__(self):
		base_path = self.find_path()
		if not base_path:
			print("PATH NOT FOUND")
			quit()
		data_path = os.path.join('sharedData', 'data')
		self.CHROMEDRIVER = os.path.join(base_path, 'chromedriver.exe')
		self.GRAPH_PATH = os.path.join(base_path[:3], 'Webing', 'Static', 'Images')
		self.FINTECHS_FILE = os.path.join(base_path, data_path, 'fintechs.txt')
		self.VAULT_FILE = os.path.join(base_path, data_path,'TDC_vault.txt')
		self.ACTIVE_FILE = os.path.join(base_path, data_path,'TDC.txt')
		self.FIXED_FILE = os.path.join(base_path, data_path,'TDC_fixed.txt')
		self.AVG_FILE = os.path.join(base_path, data_path,'TDC_average.txt')

		with open(self.FINTECHS_FILE) as file:
			data = csv.reader(file, delimiter=',')
			self.fintech_data = [{'name': item[0], 'url': item[1], 'search': (item[2], int(item[3]), int(item[4]), int(item[5]), False if item[6] == "False" else True), 'image': item[7]} for item in data]

	def find_path(self):
	    paths = (r'C:\Users\Gabriel Freundt\Google Drive\Multi-Sync',r'D:\Google Drive Backup\Multi-Sync', r'C:\users\gfreu\Google Drive\Multi-Sync', '/home/pi/webing')
	    for path in paths:
	        if os.path.exists(path):
	            return path


def set_options():
	options = WebDriverOptions()
	options.add_argument("--window-size=800,800")
	options.add_argument("--headless")
	options.add_argument("--disable-gpu")
	options.add_argument("--silent")
	options.add_argument("--disable-notifications")
	options.add_argument("--incognito")
	options.add_argument("--log-level=3")
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	return options


def get_source(url, options, params):
	print(url)
	if params[4]:
		raw = subprocess.check_output(['chrome.exe', '--headless', '--enable-logging', '--disable-gpu', '--dump-dom', url, '--virtual-time-budget=10000']).decode('utf-8')
	else:
		driver = webdriver.Chrome(active.CHROMEDRIVER, options=options)
		driver.get(url)
		element = WebDriverWait(driver, 10)
		time.sleep(1)
		raw = driver.page_source
		driver.quit()
	tdc = extract(raw, params)
	if tdc:
		save(url, tdc)
	

def clean(text):
	r = ''
	for digit in text.strip():
		if digit.isdigit() or digit == ".":
			r += digit
		else:
			break
	return r


def extract(source, params):
	init = 0
	for i in range(params[1]):
		init = source.find(params[0], init+1)
		text = source[init+params[2]:init+params[3]]
	return clean(text)


def save(url, tdc):
	with open(active.VAULT_FILE, mode='a', encoding='utf-8', newline="\n") as file:
		data = csv.writer(file, delimiter=',')
		data.writerow([url, tdc, active.time_date])


def file_extract_recent(n):
	with open(active.VAULT_FILE, mode='r', encoding='utf-8', newline="\n") as file:
		data1 = [i for i in csv.reader(file, delimiter=',')]
		with open(active.ACTIVE_FILE, mode='w', encoding='utf-8', newline="\n") as file2:
			data2 = csv.writer(file2, delimiter=',')
			for lines in data1[-n:]:
				data2.writerow(lines)


def analysis():
	with open(active.ACTIVE_FILE, mode='r') as file:
		data = [i for i in csv.reader(file, delimiter=',')]
	fintechs = list(set([i[0] for i in data]))
	datapoints = {unique: [float(i[1]) for i in data if i[0] == unique] for unique in fintechs}

	# Update every time the code runs

	# Add Average to Dataset
	averagetc = round(mean([datapoints[f][-1] for f in fintechs if datapoints[f][-1] > 0]),4)

	# Append Text File with new Average
	item = [f'{averagetc:.4f}', active.time_date]
	with open(active.AVG_FILE, mode='a', newline='') as file:
		csv.writer(file, delimiter=",").writerow(item)

	# Create Text File for Web 
	datax = [([i['image'] for i in active.fintech_data if i['url'] == f][0], f, f'{datapoints[f][-1]:0<6}') for f in fintechs]
	with open(active.FIXED_FILE, mode='w', newline='') as file:
		w = csv.writer(file, delimiter=",")
		# Append Average and Date
		w.writerow([f'{averagetc:.4f}', data[-1][2][-8:], data[-1][2][:10]]) # tc, time, date
		# Append latest from each fintech
		for i in sorted(datax, key=lambda x:x[2]):
			w.writerow(i)

	# Intraday Graph
	with open(active.AVG_FILE, mode='r') as file:
		data = [i for i in csv.reader(file, delimiter=',')]
	data_avg_today = [(float(i[0]), dt.strptime(i[1], '%Y-%m-%d %H:%M:%S')) for i in data if dt.strptime(i[1],'%Y-%m-%d %H:%M:%S').date() == dt.today().date()]
	datetime_midnight = dt.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
	x = [(i[1].timestamp()-datetime_midnight)/3600 for i in data_avg_today]
	y = [i[0] for i in data_avg_today]
	mid_axis_y = round((max(y) + min(y))/2,2)
	min_axis_y, max_axis_y = mid_axis_y - 0.05, mid_axis_y + 0.05
	axis = (int(x[0]), 22, min_axis_y, max_axis_y)
	xt = (range(axis[0],axis[1]+1),range(axis[0],axis[1]+1))
	yt = [i/1000 for i in range(int(axis[2]*1000), int(axis[3]*1000)+10, 10)]
	graph(data_avg_today, x, y, xt, yt, axis=axis, filename='intraday.png')

	# Update only on first run of the day
	if dt.now().hour <= 7 and dt.now().minute < 15:

		# Last 5 days Graph
		data_5days = [(float(i[0]), dt.strptime(i[1], '%Y-%m-%d %H:%M:%S')) for i in data if delta(days=1) <= dt.today().date() - dt.strptime(i[1],'%Y-%m-%d %H:%M:%S').date() <= delta(days=5)]
		x = [(i[1].timestamp()-datetime_midnight)/3600/24 for i in data_5days]
		y = [i[0] for i in data_5days]
		mid_axis_y = round((max(y) + min(y))/2,2)
		min_axis_y, max_axis_y = mid_axis_y - 0.05, mid_axis_y + 0.05
		axis = (-5, 0, min_axis_y, max_axis_y)
		days_week = ['Dom', 'Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab']*2
		xt = ([days_week[i+dt.today().weekday()+1] for i in range(-5,1)], [i for i in range(-5,1)])
		yt = [i/1000 for i in range(int(axis[2]*1000), int(axis[3]*1000)+10, 10)]
		graph(data_5days, x, y, xt, yt, axis=axis, filename='last5days.png')

		# Last 30 days Graph
		data_30days = [(float(i[0]), dt.strptime(i[1], '%Y-%m-%d %H:%M:%S')) for i in data if delta(days=1) <= dt.today().date() - dt.strptime(i[1],'%Y-%m-%d %H:%M:%S').date() <= delta(days=30)]
		x = [(i[1].timestamp()-datetime_midnight)/3600/24 for i in data_30days]
		y = [i[0] for i in data_30days]
		mid_axis_y = round((max(y) + min(y))/2,2)
		min_axis_y, max_axis_y = mid_axis_y - 0.05, mid_axis_y + 0.05
		axis = (-5, 0, min_axis_y, max_axis_y)
		xt = ([i for i in range(-30,1,2)], [i for i in range(-30,1,2)])
		yt = [i/1000 for i in range(int(axis[2]*1000), int(axis[3]*1000)+10, 10)]
		graph(data_30days, x, y, xt, yt, axis=axis, filename='last30days.png')



def graph(data, x, y, xt, yt, axis, filename):
	plt.rcParams['figure.figsize'] = (4, 2.5)
	plt.plot(x,y)
	ax = plt.gca()
	ax.set_facecolor('#F5F1F5')
	ax.spines['bottom'].set_color('#DFD8DF')
	ax.spines['top'].set_color('#DFD8DF')
	ax.spines['left'].set_color('white')
	ax.spines['right'].set_color('#DFD8DF')
	plt.tick_params(axis='both', length = 0)
	plt.axis(axis)

	plt.xticks(xt[1], xt[0], color='#606060', fontsize=8)
	plt.yticks(yt, color='#606060', fontsize=8)
	plt.grid(color='#DFD8DF')
	plt.savefig(os.path.join(active.GRAPH_PATH, filename), pad_inches=0, bbox_inches = 'tight', transparent=True)
	plt.close()


def main():
	options = set_options()
	urls, search, images = [], [], []
	with open(active.FINTECHS_FILE) as file:
		data = csv.reader(file, delimiter=',')
		#active.fintech_data = [{'name': item[0], 'url': item[1], 'search': (item[2], int(item[3]), int(item[4]), int(item[5]), False if item[6] == "False" else True), 'image': item[7]} for item in data]
		for item in data:
			urls.append(item[1])
			search.append((item[2], int(item[3]), int(item[4]), int(item[5]), False if item[6] == "False" else True))
	for url, params in zip(urls, search):
		try:
			get_source(url, options, params)
		except:
			pass
	file_extract_recent(9800)
	analysis()


active = Basics()
active.time_date = dt.now().strftime('%Y-%m-%d %H:%M:%S')
#main()
analysis()