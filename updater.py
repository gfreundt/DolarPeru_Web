import csv
from datetime import datetime as dt
from datetime import timedelta as delta
import time


def load_data(filename):
	with open(filename, mode='r') as file:
		data = [i for i in csv.reader(file, delimiter=',')]
		zero_time = data[0][2]
	return [[i[0], i[1], (dt.strptime(i[2], '%Y-%m-%d %H:%M:%S')-dt.strptime(zero_time, '%Y-%m-%d %H:%M:%S')).total_seconds()/3600] for i in data], zero_time


def analysis():
	data, zero_time = load_data('TDC.txt')
	fintechs = list(set([i[0] for i in data]))
	datapoints = {unique: [(f'{float(i[1]):.4f}', i[2]) for i in data if i[0] == unique] for unique in fintechs}
	return [(f, datapoints[f][-1][0],dt.strftime(dt.strptime(zero_time, '%Y-%m-%d %H:%M:%S') + delta(hours = datapoints[f][-1][1]),'%H:%M:%S')) for f in fintechs]


def main():
	return analysis()
	


if '__name__' == '__main__':
	main()

