import os, sys, csv, json, time
import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime as dt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as WebDriverOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from statistics import mean
import threading
#import pytesseract
from PIL import Image

# Switches:	NOTEST = work with production data
#			DAILY-NOW = force once-a-day updates


class Basics:
	def __init__(self):
		self.switches = [i.upper() for i in sys.argv]
		data_path = self.find_path()
		if "NOTEST" not in self.switches:
			data_path = os.path.join(data_path, 'test')
		if "/home/pi" in data_path:
			self.CHROMEDRIVER = '/usr/bin/chromedriver'
			self.GRAPH_PATH = os.path.join('/home', 'pi', 'webing', 'static', 'images')
			self.DATA_STRUCTURE_FILE = os.path.join('/home', 'pi', 'Coding', 'tdc', 'data_structure.json')
			self.PYTESSERACT_PATH = os.path.join('/home', 'pi', 'Coding', 'tdc', 'tesseract')
		else:
			self.CHROMEDRIVER = os.path.join(data_path[:3], 'Coding', 'tdc', 'chromedriver.exe')
			self.GRAPH_PATH = os.path.join(data_path[:3], 'Webing', 'Static', 'Images')
			self.DATA_STRUCTURE_FILE = os.path.join(data_path[:3], 'Coding', 'tdc', 'data_structure.json')
			self.PYTESSERACT_PATH = os.path.join(data_path[:3], 'Program Files (x86)', 'Tesseract-OCR', 'tesseract.exe')
		self.SCREENSHOT_FILE = os.path.join(data_path, 'screenshot.png')
		self.LAST_USE_FILE = os.path.join(data_path, 'last_use.txt')
		self.VAULT_FILE = os.path.join(data_path,'TDC_vault.txt')
		self.ACTIVE_FILE = os.path.join(data_path,'TDC.txt')
		self.WEB_VENTA_FILE = os.path.join(data_path,'WEB_Venta.json')
		self.WEB_COMPRA_FILE = os.path.join(data_path,'WEB_Compra.json')
		self.AVG_VENTA_FILE = os.path.join(data_path,'AVG_Venta.txt')
		self.AVG_COMPRA_FILE = os.path.join(data_path,'AVG_Compra.txt')
		self.time_date = dt.now().strftime('%Y-%m-%d %H:%M:%S')
		self.results = []
		with open(self.DATA_STRUCTURE_FILE, 'r', encoding='utf-8') as file:
			self.fintechs = json.load(file)['fintechs']

	def find_path(self):
	    paths = (r'C:\Users\Gabriel Freundt\Google Drive\Multi-Sync\sharedData\data',r'D:\Google Drive Backup\Multi-Sync\sharedData\data',
	    		 r'C:\users\gfreu\Google Drive\Multi-Sync\sharedData\data', '/home/pi/webing/data')
	    for path in paths:
	        if os.path.exists(path):
	            return path


def set_options():
	options = WebDriverOptions()
	options.add_argument("--window-size=1440,810")
	options.add_argument("--headless")
	options.add_argument("--disable-gpu")
	options.add_argument("--silent")
	options.add_argument("--disable-notifications")
	options.add_argument("--incognito")
	options.add_argument("--log-level=3")
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	return options


def get_source(fintech, options):
	driver = webdriver.Chrome(os.path.join(os.getcwd(),active.CHROMEDRIVER), options=options)
	attempts = 1
	while attempts <= 3:
		try:
			driver.get(fintech['url'])
			break
		except:
			print("First Level Exception", fintech['name'])
			attempts += 1
			time.sleep(3)
	info, attempts = [], 1
	for quote in ['compra', 'venta']:
		if fintech[quote]['click']:
			driver.find_element_by_xpath(fintech[quote]['click_xpath']).click()
		element_present = EC.visibility_of_element_located((By.XPATH, fintech[quote]['xpath']))
		while attempts <= 3:
			try:
				WebDriverWait(driver, 10).until(element_present)
				time.sleep(fintech['sleep'])
				info.append(extract(driver.find_element_by_xpath(fintech[quote]['xpath']).text, fintech[quote]))
				success = True
				break
			except:
				print(fintech['name'], 'retrying')
				success = False
				attempts += 1
		if not success and 'ocr' in fintech:
			ocr_result = clean(get_source_ocr(fintech['ocr'][quote], driver).strip())
			print('ocr result:', ocr_result)
			if ocr_result:
				info.append(ocr_result)
	driver.quit()
	if info and info[0] != '':
		active.results.append({'url':fintech['url'], 'Compra': info[0], 'Venta': info[1]})
	

def get_source_ocr(coords, driver):
	driver.save_screenshot(active.SCREENSHOT_FILE)
	x, y, width, height = coords
	img = Image.open(active.SCREENSHOT_FILE).crop((x, y, width, height))
	pytesseract.pytesseract.tesseract_cmd = active.PYTESSERACT_PATH
	return pytesseract.image_to_string(img, lang='eng')


def clean(text):
	r = ''
	for digit in text.strip():
		if digit.isdigit() or digit == ".":
			r += digit
		else:
			break
	return r


def extract(source, fintech):
	init = 0
	text = source[init+fintech['extract_start']:init+fintech['extract_end']]
	return clean(text)


def save():
	with open(active.VAULT_FILE, mode='a', encoding='utf-8', newline="\n") as file:
		data = csv.writer(file, delimiter=',')
		for f in active.results:
			data.writerow([f['url'], f['Venta'], active.time_date, f['Compra']])


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
		fintechs = [i['url'] for i in active.fintechs]
	for quote, avg_filename, web_filename, graph_filename in zip([1,3], [active.AVG_VENTA_FILE, active.AVG_COMPRA_FILE], [active.WEB_VENTA_FILE, active.WEB_COMPRA_FILE], ['venta', 'compra']):
		this_time = data[-1][2] # Loads latest quote datetime
		datapoints = {i[0]: float(i[quote]) for i in data if i[2] == this_time and float(i[quote]) > 0}
		# Update every time the code runs

		# Add Average to Dataset
		averagetc = round(mean([datapoints[i] for i in datapoints.keys()]),4)
		# Append Text File with new Average
		item = [f'{averagetc:.4f}', active.time_date]
		with open(avg_filename, mode='a', newline='') as file:
			csv.writer(file, delimiter=",").writerow(item)
		# Create Text File for Web
		datax = [{'image': [i['image'] for i in active.fintechs if i['url'] == f][0], 'name': f, 'value': f'{datapoints[f]:0<6}'} for f in datapoints.keys()]
		with open(web_filename, mode='w', newline='') as json_file:
			# Append Average and Date
			dump = {'head': {'value':f'{averagetc:.4f}', 'time':data[-1][2][-8:], 'date':data[-1][2][:10]}} # tc_venta, time, date
			# Append latest from each fintech
			dump.update({'details': [i for i in sorted(datax, key=lambda x:x['value']) if i['value'] != '0.0000']})
			json.dump(dump,json_file)
		# Intraday Graph
		with open(avg_filename, mode='r') as file:
			datax = [i for i in csv.reader(file, delimiter=',')]
		data_avg_today = [(float(i[0]), dt.strptime(i[1], '%Y-%m-%d %H:%M:%S')) for i in datax if dt.strptime(i[1],'%Y-%m-%d %H:%M:%S').date() == dt.today().date()]
		datetime_midnight = dt.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
		x = [(i[1].timestamp()-datetime_midnight)/3600 for i in data_avg_today]
		y = [i[0] for i in data_avg_today]
		mid_axis_y = round((max(y) + min(y))/2,2)
		min_axis_y, max_axis_y = mid_axis_y - 0.05, mid_axis_y + 0.05
		axis = (int(x[0]), 22, min_axis_y, max_axis_y)
		xt = (range(axis[0],axis[1]),range(axis[0],axis[1]))
		yt = [i/1000 for i in range(int(axis[2]*1000), int(axis[3]*1000)+10, 10)]
		graph(data_avg_today, x, y, xt, yt, axis=axis, filename=f'intraday-{graph_filename}.png')

		# Update only on first run of the day
		
		if (dt.now().hour <= 7 and dt.now().minute < 15) or "DAILY-NOW" in active.switches:
			# Last 5 days Graph
			data_5days = [(float(i[0]), dt.strptime(i[1], '%Y-%m-%d %H:%M:%S')) for i in datax if delta(days=1) <= dt.today().date() - dt.strptime(i[1],'%Y-%m-%d %H:%M:%S').date() <= delta(days=5)]
			x = [(i[1].timestamp()-datetime_midnight)/3600/24 for i in data_5days]
			y = [i[0] for i in data_5days]
			mid_axis_y = round((max(y) + min(y))/2,2)
			min_axis_y, max_axis_y = mid_axis_y - 0.075, mid_axis_y + 0.075
			axis = (-5, 0, min_axis_y, max_axis_y)
			days_week = ['Dom', 'Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab']*2
			xt = ([days_week[i+dt.today().weekday()+1] for i in range(-5,1)], [i for i in range(-5,1)])
			yt = [round(i/1000,2) for i in range(int(axis[2]*1000), int(axis[3]*1000)+10, 10)]
			graph(data_5days, x, y, xt, yt, axis=axis, filename=f'last5days-{graph_filename}.png')
			# Last 30 days Graph
			data_30days = [(float(i[0]), dt.strptime(i[1], '%Y-%m-%d %H:%M:%S')) for i in datax if delta(days=1) <= dt.today().date() - dt.strptime(i[1],'%Y-%m-%d %H:%M:%S').date() <= delta(days=30)]
			x = [(i[1].timestamp()-datetime_midnight)/3600/24 for i in data_30days]
			y = [i[0] for i in data_30days]
			mid_axis_y = round((max(y) + min(y))/2,2)
			min_axis_y, max_axis_y = mid_axis_y - 0.1, mid_axis_y + 0.1
			axis = (-5, 0, min_axis_y, max_axis_y)
			xt = ([i for i in range(-30,1,2)], [i for i in range(-30,1,2)])
			yt = [round(i/1000,2) for i in range(int(axis[2]*1000), int(axis[3]*1000)+10, 20)]
			graph(data_30days, x, y, xt, yt, axis=axis, filename=f'last30days-{graph_filename}.png')



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


def last_use():
	with open(active.LAST_USE_FILE, 'w') as file:
		file.writerow(active.time_date)


def main():
	options = set_options()
	all_threads = []
	for fintech in active.fintechs:
		if fintech['online']:
			new_thread = threading.Thread(target=get_source, args=(fintech, options))
			all_threads.append(new_thread)
			try:
				new_thread.start()
			except:
				pass

	_ = [i.join() for i in all_threads]  # Ensures all threads end before moving forward

	save()
	file_extract_recent(9800)
	analysis()
	last_use()



active = Basics()
main()
#analysis()
