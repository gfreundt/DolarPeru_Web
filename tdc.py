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
		self.AVG_FILE = os.path.join(base_path, data_path,'TDC_fixed.txt')

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
	now = dt.now()
	time_date = now.strftime('%Y-%m-%d %H:%M:%S')
	with open(active.VAULT_FILE, mode='a', encoding='utf-8', newline="\n") as file:
		data = csv.writer(file, delimiter=',')
		data.writerow([url, tdc, time_date])


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
		zero_time = data[0][2]
		data = [[i[0], i[1], (dt.strptime(i[2], '%Y-%m-%d %H:%M:%S')-dt.strptime(zero_time, '%Y-%m-%d %H:%M:%S')).total_seconds()/3600] for i in data]
		fintechs = list(set([i[0] for i in data]))
		datapoints = {unique: [(f'{float(i[1]):.4f}', i[2]) for i in data if i[0] == unique] for unique in fintechs}

		# Add Average
		averagetc = mean([float(datapoints[f][-1][0]) for f in fintechs if float(datapoints[f][-1][0]) > 0])
		averageh = mean([float(datapoints[f][-1][1]) for f in fintechs if float(datapoints[f][-1][0]) > 0])
		datapoints.update({'Promedio':[(f'{averagetc:.4f}',averageh)]})

	with open(active.FIXED_FILE, mode='w') as file:
		data = [(f, datapoints[f][-1][0],dt.strftime(dt.strptime(zero_time, '%Y-%m-%d %H:%M:%S') + delta(hours = datapoints[f][-1][1]),'%H:%M:%S')) for f in (fintechs+['Promedio'])]
		for i in sorted(data, key=lambda x:x[1]):
			file.write(f'{i[0]:<30} {i[1]}    {i[2]}' + '\n')


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
	file_extract_recent(1000)
	analysis()


active = Basics()
main()
