import sqlite3
import os

os.remove('rentDB.db')

conn = sqlite3.connect('rentDB.db')
c = conn.cursor()

c.execute('CREATE TABLE CityList(\
			city TEXT PRIMARY KEY)')

c.execute('CREATE TABLE HouseList(\
			house TEXT PRIMARY KEY, \
			city TEXT NOT NULL)')

c.execute('CREATE TABLE TenantList (\
			ID INTEGER PRIMARY KEY, \
			city TEXT NOT NULL, \
			house TEXT NOT NULL, \
			startDate DATE NOT NULL, \
			endDate DATE NOT NULL, \
			name TEXT NOT NULL, \
			phoneMain TEXT NOT NULL,\
			phoneAlt TEXT DEFAULT NULL,\
			email TEXT DEFAULT NULL, \
			wechat TEXT DEFAULT NULL)')

c.execute('CREATE TABLE FeeList (\
			ID INTEGER PRIMARY KEY, \
			house TEXT NOT NULL, \
			feeType TEXT NOT NULL, \
			amount REAL NOT NULL, \
			enter_date DATE NOT NULL, \
			pay_before_date DATE NOT NULL, \
			paid_date DATE DEFAULT NULL, \
			note TEXT DEFAULT NULL)')

conn.commit()
conn.close()