import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime as dt
from datetime import timedelta as delta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as WebDriverOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import time
import csv
import os
from statistics import mean


class Basics:
	def __init__(self):
		base_path = self.find_path()
		if not base_path:
			print("PATH NOT FOUND")
			quit()
		data_path = os.path.join('sharedData', 'data')
		self.CHROMEDRIVER = os.path.join(base_path, 'chromedriver.exe')
		self.FINTECHS_FILE = os.path.join(base_path, data_path, 'fintechs.txt')
		self.VAULT_FILE = os.path.join(base_path, data_path,'TDC_vault.txt')
		self.ACTIVE_FILE = os.path.join(base_path, data_path,'TDC.txt')
		self.FIXED_FILE = os.path.join(base_path, data_path,'TDC_fixed.txt')
		self.AVG_FILE = os.path.join(base_path, data_path,'TDC_average.txt')

	def find_path(self):
	    paths = (r'C:\Users\Gabriel Freundt\Google Drive\Multi-Sync',r'D:\Google Drive Backup\Multi-Sync', r'C:\users\gfreu\Google Drive\Multi-Sync')
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
	driver = webdriver.Chrome(active.CHROMEDRIVER, options=options)
	driver.get(url)
	element = WebDriverWait(driver, 10)
	time.sleep(1)
	if params[4]:
		webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
		time.sleep(3)
	tdc = extract(driver.page_source, params)
	if tdc:
		save(url, tdc)
	driver.quit()


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
	
	#time_date = now.strftime('%Y-%m-%d %H:%M:%S')
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
		zero_time = dt.strptime(data[0][2], '%Y-%m-%d %H:%M:%S')
		data = [[i[0], i[1], (dt.strptime(i[2], '%Y-%m-%d %H:%M:%S')-zero_time).total_seconds()/3600] for i in data]
		fintechs = list(set([i[0] for i in data]))
		datapoints = {unique: [(f'{float(i[1]):.4f}', i[2]) for i in data if i[0] == unique] for unique in fintechs}

	# Add Average to Dataset
	averagetc = mean([float(datapoints[f][-1][0]) for f in fintechs if float(datapoints[f][-1][0]) > 0])
	averageh = mean([float(datapoints[f][-1][1]) for f in fintechs if float(datapoints[f][-1][0]) > 0])
	datapoints.update({'Promedio':[(f'{averagetc:.4f}',averageh)]})

	# Append Text File with new Average
	item = [f'{averagetc:.4f}', active.time_date]
	with open(active.AVG_FILE, mode='a', newline='') as file:
		csv.writer(file, delimiter=",").writerow(item)

	# Create Text File for Web Update
	datax = [(datapoints[f][-1][0], f, dt.strftime(zero_time + delta(hours = datapoints[f][-1][1]),'%H:%M:%S')) for f in (fintechs+['Promedio'])]
	with open(active.FIXED_FILE, mode='w', newline='') as file:
		for i in sorted(datax, key=lambda x:x[0]):
			csv.writer(file, delimiter=",").writerow(i)


def analysis2():

	# Create Intraday Graph
	#print(data)
	with open(active.AVG_FILE, mode='r') as file:
		data = [i for i in csv.reader(file, delimiter=',')]
		start_today7am = dt.strptime(dt.strftime(dt.now(),'%Y-%m-%d')+' 07:00:00', '%Y-%m-%d %H:%M:%S')
		finish_today10pm = dt.strptime(dt.strftime(dt.now(),'%Y-%m-%d')+' 23:00:00', '%Y-%m-%d %H:%M:%S')

		datax = [(float(i[0]), i[1]) for i in data if dt.strptime(i[1],'%Y-%m-%d %H:%M:%S')>start_today7am]
		datax = [(float(i[0]), dt.strptime(i[1],'%Y-%m-%d %H:%M:%S')) for i in data if dt.strptime(i[1],'%Y-%m-%d %H:%M:%S')>start_today7am]

	#graph(datax, start_today7am, finish_today10pm)


def graph(data, start, end):

	plt.rcParams['figure.figsize'] = (16, 10)
	y = [i[0] for i in data]
	x = [i[1] for i in data]
	plt.plot_date(x,y)
	#xt = [dt.strptime(str(i), '%H') for i in range(7,23)]
	#plt.xticks(xt, rotation='vertical')
	plt.axis((start,end,3.5,4))
	plt.ylabel(f'Tipo de Cambio (Venta)')
	plt.xlabel('Hora', labelpad=20)
	plt.suptitle(f'Cotización de Hoy \n({dt.strftime(x[0], "%Y-%m-%d")})', size='xx-large', y=.98)
	#	plt.grid(axis='y')
	plt.show()
		#plt.savefig(graph_filename)
		#plt.close('all')


def main():
	options = set_options()
	urls, search = [], []
	with open(active.FINTECHS_FILE) as file:
		data = csv.reader(file, delimiter=',')
		for item in data:
			urls.append(item[1])
			search.append((item[2], int(item[3]), int(item[4]), int(item[5]), False if item[6] == "False" else True))
	for url, params in zip(urls, search):
		try:
			get_source(url, options, params)
		except:
			pass
	file_extract_recent(2500)
	analysis()


active = Basics()
active.time_date = dt.now().strftime('%Y-%m-%d %H:%M:%S')
main()
#analysis()