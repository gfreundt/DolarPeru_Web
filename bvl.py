import yagmail
from datetime import datetime as dt
from datetime import timedelta as delta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as WebDriverOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import time
import csv
import os


class Basics:
	def __init__(self):
		base_path = self.find_path()
		if not base_path:
			print("PATH NOT FOUND")
			quit()
		data_path = os.path.join('sharedData', 'data')
		self.CHROMEDRIVER = os.path.join(base_path, 'chromedriver.exe')
		self.BVL_FILE = os.path.join(base_path, data_path, 'bvl.csv')

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


def get_source(url):
	driver = webdriver.Chrome(active.CHROMEDRIVER, options=options)
	driver.get(url)
	element = WebDriverWait(driver, 10)
	time.sleep(3)
	return driver.page_source


def get_string(raw, idx):
	r = ''
	while True:
		s = raw[idx:idx+1]
		if s == '"' or s=="<":
			return r.strip()
		else:
			r += s
			idx += 1

def codes(raw):
	idx = 0
	extract=[]
	while True:
		nidx = raw.find('ng-star-inserted" title=', idx) + 25
		e = get_string(raw, nidx)
		extract.append(e)
		if e == 'XOM':
			return extract[1::3]
		else:
			idx = int(nidx)

def prices(raw):
	idx = 0
	extract=[]
	while idx<len(raw):
		nidx = raw.find('"amount"', idx) + 20
		if nidx == 19:
			return extract
		e = get_string(raw, nidx)
		if not e:
			extract.append('0.00')
		elif e[0] == "U" or e[0] == "S":
			extract.append(e)
		idx = int(nidx)

def combine(codes, prices):
	r = [['Nemónico','Anterior','Apertura','Última','Monto']]
	for n, code in enumerate(codes):
		r.append([code] + [prices[i] for i in range(n*4, n*4+4)])
	with open(active.BVL_FILE, mode='w', newline="") as file:
		w = csv.writer(file, delimiter="|")
		for line in r:
			w.writerow(line)
	return r


def send_gmail(to, subject, text_content, attach):
	user = 'gfreundt@gmail.com'
	app_password = 'brwd tjfk tpuo gimo'
	content = [text_content, attach]

	with yagmail.SMTP(user, app_password) as yag:
	    yag.send(to, subject, content)




active = Basics()
options=set_options()
raw = get_source('https://www.bvl.com.pe/mercado/movimientos-diarios')

codes = codes(raw)
prices = prices(raw)
combine(codes, prices)
send_gmail('jlcastanedaherrera@gmail.com', 'Cierre BVL del ' + dt.strftime(dt.now(), '%Y.%m.%d'), 'Abrirlo como CSV con delimitador |', active.BVL_FILE)