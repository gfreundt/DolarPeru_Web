from datetime import datetime as dt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as WebDriverOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import time
import csv


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
	driver = webdriver.Chrome(r'C:\Users\Gabriel Freundt\google drive\multi-sync\chromedriver.exe', options=options)
	driver.get(url)
	element = WebDriverWait(driver, 10)
	time.sleep(3)
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
	with open(r'C:\Users\Gabriel Freundt\google drive\multi-sync\tipodecambio\TDC.txt', mode='a', encoding='utf-8', newline="\n") as file:
		data = csv.writer(file, delimiter=',')
		data.writerow([url, tdc, time_date])



def main():
	options = set_options()
	urls, search = [], []
	with open(r'C:\Users\Gabriel Freundt\google drive\multi-sync\tipodecambio\fintechs.txt') as file:
		data = csv.reader(file, delimiter=',')
		for item in data:
			urls.append(item[0])
			search.append((item[1], int(item[2]), int(item[3]), int(item[4]), False if item[5] == "False" else True))
	for url, params in zip(urls, search):
		try:
			get_source(url, options, params)
		except:
			pass


main()
