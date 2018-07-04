# encoding: utf-8

import requests
import sys
import MySQLdb

if __name__ == '__main__':
	reload(sys)
	sys.setdefaultencoding('utf8')
	url = 'http://taipei.youbike.com.tw/cht/index.php'
	content = requests.get(url).text
try:
	db = MySQLdb.connect(host='localhost', user='ShiXiang', passwd='ShiXiang', db='webpage')
	db.set_character_set('utf8')
	cursor = db.cursor()
	sql = 'INSERT INTO `youbike_data` (`snapshot`) VALUES (%s)'
	cursor.execute(sql, (content,))
	db.commit()
	db.close()
except MySQLdb.Error as e:
	print "Error %d: %s" % (e.args[0], e.args[1])	

