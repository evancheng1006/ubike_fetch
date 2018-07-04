# encoding: utf-8

import MySQLdb
import requests
import sys
from bs4 import BeautifulSoup
import json
import numpy as np

def get_current_time():
	from time import gmtime, strftime
	#https://stackoverflow.com/questions/415511/how-to-get-current-time-in-python
	return strftime("%Y-%,-%d %H:%M:%S", gmtime)

def url_to_content(url):
	content = requests.get(url).text
	return content
def content_to_json_text(content):
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
def json_text_to_dict_arr(json_text):
	result_dict = json.loads(json_text)
	if len(result_dict) == 0:
		raise Exception('No Data')
	result = []
	for k in result_dict:
		v = result_dict[k]
		result.append(v)
	#sort data by sno
	result = sorted(result, key=lambda k: int(k['sno']))
	return result

def update_station_info(data, db, dbc):
	try:
		sql = 'INSERT IGNORE INTO `station` (`sno`, `sna`, `sarea`, `ar`, `lat`, `lng`) VALUES (%s, %s, %s, %s, %s, %s)'
		for i in range(len(data)):
			dbc.execute(sql, (data[i]['sno'], data[i]['sna'], data[i]['sarea'], data[i]['ar'], data[i]['lat'], data[i]['lng']))
		db.commit()
	except MySQLdb.Error as e:
		print "Error %d: %s" % (e.args[0], e.args[1])
	return
def record_bike_status(data, db, dbc):
	'''
CREATE TABLE `bike_status` (
    `sno` INT NOT NULL,
    `tot` INT NOT NULL,
    `sbi` INT NOT NULL,
    `bemp` INT NOT NULL,
    `mday` VARCHAR(16) NOT NULL,
    `sv` INT NOT NULL,
    PRIMARY KEY (`sno`, `tot`, `sbi`, `bemp`, `mday`, `sv`)
) ENGINE=INNODB;
	'''

	try:
		sql = 'INSERT IGNORE INTO `bike_status` (`sno`, `tot`, `sbi`, `bemp`, `mday`, `sv`) VALUES (%s, %s, %s, %s, %s, %s)'
		for i in range(len(data)):
			status = (data[i]['sno'], data[i]['tot'], data[i]['sbi'], data[i]['bemp'], data[i]['mday'], data[i]['sv'])
			dbc.execute(sql, status)
		db.commit()
	except MySQLdb.Error as e:
		print "Error %d: %s" % (e.args[0], e.args[1])
	return
	

if __name__ == '__main__':
	reload(sys)
	sys.setdefaultencoding('utf8')
	
	db = MySQLdb.connect(host='localhost', user='ShiXiang', passwd='XiangShi', db='youbike')
	db.set_character_set('utf8')
	dbc = db.cursor()

	url = 'http://taipei.youbike.com.tw/cht/index.php'
	content = requests.get(url).text
	#content = url_to_content(url)
	json_text = content_to_json_text(content)
	data = json_text_to_dict_arr(json_text)
	update_station_info(data, db, dbc)
	record_bike_status(data, db, dbc)

	db.close()
