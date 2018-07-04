# encoding: utf-8

import requests
import sys
from bs4 import BeautifulSoup
#from BeautifulSoup import BeautifulSoup
#import selenium
# we don't use selenium because simulation takes too much resourses
# instead, we parse json ourselves
import json
import numpy as np

def get_current_time():
	from time import gmtime, strftime
	#https://stackoverflow.com/questions/415511/how-to-get-current-time-in-python
	return strftime("%Y-%,-%d %H:%M:%S", gmtime)

def fetch_data(content):
	soup = BeautifulSoup(content, 'html.parser')
	js_text = soup.find_all('script')
	js_text = [x for x in soup.find_all('script') if np.any(['var siteContent' in x for x in x.contents])]
	if len(js_text) != 1:
		raise Exception('Cannot locate content')
	js_text = js_text[0]
	json_text = [x for x in js_text.split('\n') if 'siteContent=' in x][0]
	json_text = json_text.split(';')[0]
	json_text = '='.join(json_text.split('=')[1:])
	json_text = '\''.join(json_text.split('\'')[1:-1])
	return json_text
def json_text_to_result(json_text):
	result_dict = json.loads(json_text)
	if len(result_dict) == 0:
		raise Exception('No Data')

	result = []
	for k in result_dict:
		v = result_dict[k]
		# only fetch data we need
		#station = {
		#	'sno': v['sno'],
		#	'sna': v['sna'],
		#	'sarea': v['sarea']
		#	}
		#result.append(station)
		result.append(v)
	#sort data by sno
	result = sorted(result, key=lambda k: int(k['sno']))
	'''
	for i in range(len(result)):
		needed = ['sno', 'sna', 'tot', 'sbi', 'bemp']
		needed = ['sno', 'sv']
		line = []
		for j in range(len(needed)):
			line.append(str(result[i][needed[j]]))
		line = ','.join(line)
		result[i] = line
	'''
	for i in range(len(result)):
		station = result[i]
		line = ''
		line += str(station['sno'])
		line += station['sna'] + ': '
		if station['sv'] == '1':
			if 'sbi' == '0':
				line += '無車可借'
			elif 'bemp' == '0':
				line += '車位滿載'
			else:
				line += '正常租借'

			line += ', 可借車輛: ' + station['sbi']
			line += ', 可停空位: ' + station['bemp']	
		else:
			line += '暫停營運'

		mday = station['mday']
		d={
			'y': mday[:4],
			'm': mday[4:6],
			'd': mday[6:8],
			'H': mday[8:10],
			'M': mday[10:12],
			'S': mday[12:14],
		}
		line += ', 時間: ' + '%s/%s/%s %s:%s:%s' % (d['y'], d['m'], d['d'], d['H'], d['M'], d['S'])
		result[i] = line

	return result
	

def fetch_data_by_url(url):
	content = requests.get(url).text
	json_text = fetch_data(content)
	result = json_text_to_result(json_text)
	return result	

if __name__ == '__main__':
	reload(sys)
	sys.setdefaultencoding('utf8')
	
	url = 'http://taipei.youbike.com.tw/cht/index.php'
	result = fetch_data_by_url(url)
	print('\n'.join(result))
