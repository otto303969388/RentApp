import tkinter as tk
from tkinter import *
from tkinter import messagebox
import sqlite3
import time
from datetime import date, timedelta
import calendar

def add_months(sourcedate,months):
	month = sourcedate.month - 1 + months
	year = sourcedate.year + month // 12
	month = month % 12 + 1
	day = min(sourcedate.day,calendar.monthrange(year,month)[1])
	return date(year,month,day)

class RentApp(Tk):

	def __init__(self, *args, **kwargs):
		
		Tk.__init__(self, *args, **kwargs)
		self.conn = sqlite3.connect('rentDB.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		self.c = self.conn.cursor()
		self.container = Frame(self)

		self.container.pack(side="top", fill="both", expand=True)

		self.container.grid_rowconfigure(0, weight=1)
		self.container.grid_columnconfigure(0, weight=1)

		self.to_home_page()

	def show_frame(self, cont):

		frame = cont(self.container, self)
		frame.grid(row=0, column=0, sticky="nsew")
		frame.tkraise()

	def to_home_page(self):
		self.show_frame(HomePage)

	def on_closing(self):
		if messagebox.askokcancel("退出", "你现在要退出吗？记得要先保存哦！"):
			self.destroy()

	def to_add_city_page(self):
		self.show_frame(AddCityPage)

	def to_add_house_page(self, city):
		frame = AddHousePage(self.container, self, city)
		frame.grid(row=0, column=0, sticky="nsew")
		frame.tkraise()

	def to_house_detail_page(self, city, house):
		frame = HouseDetailPage(self.container, self, city, house)
		frame.grid(row=0, column=0, sticky="nsew")
		frame.tkraise()

	def to_add_tenant_page(self, city, house):
		frame = AddTenantPage(self.container, self, city, house)
		frame.grid(row=0, column=0, sticky="nsew")
		frame.tkraise()

	def to_add_fee_page(self, city, house):
		frame = AddFeePage(self.container, self, city, house)
		frame.grid(row=0, column=0, sticky="nsew")
		frame.tkraise()

	def to_all_past_fee_page(self, offset):
		frame = AllPastFeePage(self.container, self, offset)
		frame.grid(row=0, column=0, sticky="nsew")
		frame.tkraise()

	def to_all_future_fee_page(self, offset):
		frame = AllFutureFeePage(self.container, self, offset)
		frame.grid(row=0, column=0, sticky="nsew")
		frame.tkraise()

	def to_house_past_fee_page(self, city, house, offset):
		frame = HousePastFeePage(self.container, self, city, house, offset)
		frame.grid(row=0, column=0, sticky="nsew")
		frame.tkraise()

	def to_house_future_fee_page(self, city, house, offset):
		frame = HouseFutureFeePage(self.container, self, city, house, offset)
		frame.grid(row=0, column=0, sticky="nsew")
		frame.tkraise()

	def fee_paid(self, fee_id, city, house, time, offset):
		if messagebox.askyesno("付费", "你确定结账了?"):
			today = date.today()
			self.c.execute("UPDATE FeeList SET paid_date='%s' WHERE ID='%s'" % (today, fee_id))
			self.conn.commit()
			messagebox.showinfo("提示", "结账完成!")
			if city and house and time:
				if time == "past":
					self.to_house_past_fee_page(city,house,offset)
				else:
					self.to_house_future_fee_page(city,house,offset)
			elif city and house:
				self.to_house_detail_page(city, house)
			elif time:
				if time == "past":
					self.to_all_past_fee_page(offset)
				else:
					self.to_all_future_fee_page(offset)


class HomePage(Frame):

	def __init__(self, parent, controller):
		Frame.__init__(self, parent)
		self.controller = controller
		controller.c.execute("SELECT * FROM CityList")

		cityList = controller.c.fetchall()

		row = 0

		for city in cityList:
			
			row += 1
			label = Label(self, text=city[0], font="underline")
			label.grid(row=row, column=1, sticky=W)
			button = Button(self, text="添加房子", command = lambda city=city[0]: controller.to_add_house_page(city))
			button.grid(row=row, column=3, sticky=W)
			row += 1
			for house in controller.c.execute("SELECT * FROM HouseList WHERE city='%s'" % (city[0])):
				button = Button(self, text=house[0], relief=FLAT, command = lambda city=city[0], house=house[0]: controller.to_house_detail_page(city, house))
				button.grid(row=row, column=1, columnspan=3, sticky=W)
				row += 1
			w = Canvas(self,width=180, height=10)
			w.create_line(0,10,200,10, width=1)
			w.grid(row=row, column=1, columnspan=3)
			
			row += 1
		Label(self, text = " ").grid(row=row, column=0)
		button = Button(self, text="添加城市", command=controller.to_add_city_page)
		button.grid(row=row+1, column=3, sticky=E)
		button = Button(self, text="过去费用", command= lambda offset=0: controller.to_all_past_fee_page(offset))
		button.grid(row=row+2, column=1, sticky=E)
		button = Button(self, text="将来费用", command= lambda offset=0: controller.to_all_future_fee_page(offset))
		button.grid(row=row+2, column=3, sticky=E)
		#empty, positional label
		Label(self, text = " ").grid(row=0, column=0)
		Label(self, text = " ").grid(row=row+3, column=4)
		Label(self, text = "   ").grid(row=row+3, column=2)

class AddCityPage(Frame):

	def __init__(self, parent, controller):
		self.controller = controller
		Frame.__init__(self, parent)
		label = Label(self, text="城市: ")
		label.pack(pady=10, padx=10)
		self.cityText = Entry(self)
		self.cityText.pack(pady=10, padx=10)
		saveButton = Button(self, text="保存", command=self.save_city)
		saveButton.pack(pady=10, padx=10)
		backButton = Button(self, text="返回", command=controller.to_home_page)
		backButton.pack(pady=10, padx=10)

	def save_city(self):
		city = self.cityText.get()
		self.controller.c.execute('SELECT * FROM CityList WHERE city="%s"' % (city))
		repeat = self.controller.c.fetchall()
		if repeat:
			messagebox.showwarning("警告", "你已经添加过此城市了")
		elif messagebox.askyesno("添加城市", "你确定要添加 %s ?" % (city)):
			self.controller.c.execute('INSERT INTO CityList (city) VALUES ("%s")' % (city))
			self.controller.conn.commit()
			messagebox.showinfo("提示", "添加成功!")
			self.controller.to_home_page()

class AddHousePage(Frame):

	def __init__(self, parent, controller, city):
		self.controller = controller
		Frame.__init__(self, parent)
		self.city = city
		label = Label(self, text="所在城市: %s" % (city))
		label.pack(pady=10, padx=10)
		label = Label(self, text="房子名称/地址: ")
		label.pack(pady=10, padx=10)
		self.houseText = Entry(self)
		self.houseText.pack(pady=10, padx=10)
		saveButton = Button(self, text="保存", command=self.save_house)
		saveButton.pack(pady=10, padx=10)
		backButton = Button(self, text="返回", command=controller.to_home_page)
		backButton.pack(pady=10, padx=10)

	def save_house(self):
		house = self.houseText.get()
		self.controller.c.execute('SELECT * FROM HouseList WHERE city="%s" AND house="%s"' % (self.city, house))
		repeat = self.controller.c.fetchall()
		if repeat:
			messagebox.showwarning("警告", "你添加过这个房子了")
		elif messagebox.askyesno("添加房子", "你确定要添加 %s 到 %s ?" % (house, self.city)):
			self.controller.c.execute('INSERT INTO HouseList (house, city) VALUES ("%s", "%s")' % (house, self.city))
			self.controller.conn.commit()
			messagebox.showinfo("提示", "添加成功!")
			self.controller.to_home_page()

class HouseDetailPage(Frame):

	def __init__(self, parent, controller, city, house):
		self.controller = controller
		Frame.__init__(self, parent)
		self.city = city
		self.house = house
		controller.c.execute('SELECT * FROM TenantList WHERE city="%s" AND house="%s" ORDER BY endDate DESC' % (self.city, self.house))
		tenant = controller.c.fetchone()
		row = 0
		if not tenant:
			Label(self, text="这房子还没有出租记录").grid(row=row,column=0); row+=1
		else:
			startDate = tenant[3]
			endDate = tenant[4]
			tenantName = tenant[5]
			phoneMain = tenant[6]
			phoneAlt = tenant[7]
			email = tenant[8]
			wechat = tenant[9]
			today = date.today()
			if startDate <= today and endDate >= today:
				status = "出租中"
			else:
				status = "空置"
			Label(self, text= "房子:").grid(row=row,column=0); Label(self,text=house).grid(row=0,column=1); row+=1
			Label(self, text="出租状态:").grid(row=row,column=0); Label(self, text=status).grid(row=row,column=1); row+=1
			Label(self, text="最近出租记录:").grid(row=row,column=0,columnspan=2,sticky=W); row+=1
			Label(self, text="开始日期:").grid(row=row,column=0); Label(self, text=startDate).grid(row=row,column=1); row+=1
			Label(self, text="结束日期:").grid(row=row,column=0); Label(self, text=endDate).grid(row=row,column=1); row+=1
			Label(self, text="租客名称:").grid(row=row,column=0); Label(self, text=tenantName).grid(row=row,column=1); row+=1
			Label(self, text="电话:").grid(row=row,column=0); Label(self, text=phoneMain).grid(row=row,column=1); row+=1
			if phoneAlt:
				Label(self, text="其他电话:").grid(row=row,column=0); Label(self, text=phoneAlt).grid(row=row,column=1); row+=1
			if email:
				Label(self, text="email:").grid(row=row,column=0); Label(self, text=email).grid(row=row,column=1); row+=1
			if wechat:
				Label(self, text="wechat:").grid(row=row,column=0); Label(self, text=wechat).grid(row=row,column=1); row+=1

			#fees section
			later = add_months(today, 2)
			later = date(later.year, later.month, 1)
			Label(self, text="近期费用:").grid(row=row,column=0); row+=1
			controller.c.execute("SELECT * FROM FeeList WHERE house='%s' AND pay_before_date > '%s' AND pay_before_date < '%s' ORDER BY pay_before_date" % (self.house,today,later))
			feeList = controller.c.fetchall()
			col = 0
			if feeList:
				Label(self, text="费用").grid(row=row,column=col)
				Label(self, text="数额").grid(row=row,column=col+1)
				Label(self, text="缴费日期").grid(row=row,column=col+2)
				Label(self, text="完成日期").grid(row=row,column=col+3)
				Label(self, text="备注").grid(row=row,column=col+4)
				row+=1
				for fee in feeList:
					Label(self, text=fee[2]).grid(row=row,column=col)
					Label(self, text=fee[3]).grid(row=row,column=col+1)
					Label(self, text=fee[5]).grid(row=row,column=col+2)
					if not fee[6]:
						Button(self, text="结账", command=lambda fee_id=fee[0],city=city,house=house: controller.fee_paid(fee_id,city,house,None,None)).grid(row=row,column=col+3)
					else:
						Label(self, text=fee[6]).grid(row=row,column=col+3)
					if not fee[7]:
						Label(self, text="-").grid(row=row,column=col+4)
					else:
						Label(self, text=fee[7]).grid(row=row,column=col+4)

					row+=1
		feeButton = Button(self, text="添加费用", command=lambda house=house: controller.to_add_fee_page(city,house))
		feeButton.grid(row=row,column=0)
		addButton = Button(self, text="添加租客", command=lambda house=house: controller.to_add_tenant_page(city,house))
		addButton.grid(row=row,column=1)
		pastFeeButton = Button(self, text="过去费用", command= lambda offset=0: controller.to_house_past_fee_page(city,house,offset))
		pastFeeButton.grid(row=row, column=2)
		futureFeeButton = Button(self, text="将来费用", command= lambda offset=0: controller.to_house_future_fee_page(city,house,offset))
		futureFeeButton.grid(row=row, column=3)
		backButton = Button(self, text="返回", command=controller.to_home_page)
		backButton.grid(row=row,column=4)


class AddTenantPage(Frame):

	def __init__(self, parent, controller, city, house):
		self.controller = controller
		Frame.__init__(self, parent)
		self.house = house
		self.city = city
		Label(self, text="出租房屋 : %s" % (house)).grid(row=0,column=0)
		Label(self, text="租客名称 :").grid(row=1,column=0)
		self.nameText = Entry(self)
		self.nameText.grid(row=1,column=1)
		Label(self, text="开始日期 :").grid(row=2,column=0)
		Label(self, text="年 :").grid(row=3,column=0)
		self.startYearText = Entry(self)
		self.startYearText.grid(row=3,column=1)
		Label(self, text="月 :").grid(row=3,column=2)
		self.startMonthText = Entry(self)
		self.startMonthText.grid(row=3,column=3)
		Label(self, text="日 :").grid(row=3,column=4)
		self.startDayText = Entry(self)
		self.startDayText.grid(row=3,column=5)
		Label(self, text="结束日期 :").grid(row=4,column=0)
		Label(self, text="年 :").grid(row=5,column=0)
		self.endYearText = Entry(self)
		self.endYearText.grid(row=5,column=1)
		Label(self, text="月 :").grid(row=5,column=2)
		self.endMonthText = Entry(self)
		self.endMonthText.grid(row=5,column=3)
		Label(self, text="日 :").grid(row=5,column=4)
		self.endDayText = Entry(self)
		self.endDayText.grid(row=5,column=5)
		Label(self, text="电话: ").grid(row=6,column=0)
		self.phoneMainText = Entry(self)
		self.phoneMainText.grid(row=6,column=1)
		Label(self, text="其他电话: ").grid(row=7,column=0)
		self.phoneAltText = Entry(self)
		self.phoneAltText.grid(row=7,column=1)
		Label(self, text="email: ").grid(row=8,column=0)
		self.emailText = Entry(self)
		self.emailText.grid(row=8,column=1)
		Label(self, text="wechat: ").grid(row=9,column=0)
		self.wechatText = Entry(self)
		self.wechatText.grid(row=9,column=1)
		Label(self, text="租金: ").grid(row=10,column=0)
		self.amount = Entry(self)
		self.amount.grid(row=10,column=1)
		saveButton = Button(self, text="保存", command=self.save_tenant)
		saveButton.grid(row=11,column=0)
		backButton = Button(self, text="返回", command=lambda city=city, house=house: controller.to_house_detail_page(city, house))
		backButton.grid(row=11,column=1)

	def save_tenant(self):
		startYear = int(self.startYearText.get())
		startMonth = int(self.startMonthText.get())
		startDay = int(self.startDayText.get())
		startDate = date(year=startYear, month=startMonth, day=startDay)
		endYear = int(self.endYearText.get())
		endMonth = int(self.endMonthText.get())
		endDay = int(self.endDayText.get())
		endDate = date(year=endYear, month=endMonth, day=endDay)
		name = self.nameText.get()
		phoneMain = self.phoneMainText.get()
		phoneAlt = self.phoneAltText.get()
		email = self.emailText.get()
		wechat = self.wechatText.get()
		amount = self.amount.get()
		try:
			amount = float(amount)
		except ValueError:
			messagebox.showwarning("警告", "请输入正确的金额")
			return
		self.controller.c.execute('SELECT * FROM TenantList WHERE house="%s" ORDER BY endDate DESC' % (self.house))
		latest = self.controller.c.fetchone()
		print(latest)
		if latest != None:
			if (latest[3] <= startDate <= latest[4]) or (latest[3] <= endDate <= latest[4]):
				if name == latest[5]:
					messagebox.showwarning("警告", "这个租客已经在租这个房子, 如果是延长合同了, 请回到房子页面, 点击 延长合同")
				else:
					messagebox.showwarning("警告", "已经有人在租这个房子")
			elif messagebox.askyesno("添加房子", "你确定要添加 %s 到 %s ?" % (name, self.house)):
				self.controller.c.execute('INSERT INTO TenantList(city, house, startDate, endDate,name,phoneMain,phoneAlt,email,wechat) \
											VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' % (self.city, self.house, startDate,endDate,name,phoneMain,phoneAlt,email,wechat))
				today = date.today()
				curDate = startDate
				while curDate < endDate:
					self.controller.c.execute("INSERT INTO FeeList(house, feeType, amount, enter_date, pay_before_date) VALUES ('%s', '%s', %d, '%s', '%s')" % ((self.house, "租金", amount, today, curDate)))
					curDate = add_months(curDate, 1)
				self.controller.conn.commit()
				messagebox.showinfo("提示", "添加成功!")
				self.controller.to_house_detail_page(self.city, self.house)
		elif messagebox.askyesno("添加房子", "你确定要添加 %s 到 %s ?" % (name, self.house)):
			self.controller.c.execute('INSERT INTO TenantList(city, house, startDate, endDate,name,phoneMain,phoneAlt,email,wechat) \
										VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' % (self.city, self.house, startDate,endDate,name,phoneMain,phoneAlt,email,wechat))
			today = date.today()
			curDate = startDate
			while curDate < endDate:
				self.controller.c.execute("INSERT INTO FeeList(house, feeType, amount, enter_date, pay_before_date) VALUES ('%s', '%s', %d, '%s', '%s')" % ((self.house, "租金", amount, today, curDate)))
				curDate = add_months(curDate, 1)
			self.controller.conn.commit()
			messagebox.showinfo("提示", "添加成功!")
			self.controller.to_house_detail_page(self.city, self.house)

class AddFeePage(Frame):

	def __init__(self, parent, controller, city, house):
		self.controller = controller
		Frame.__init__(self, parent)
		self.house = house
		self.city = city
		controller.c.execute('SELECT * FROM TenantList WHERE house="%s" ORDER BY endDate DESC' % (self.house))
		tenant = self.controller.c.fetchone()
		if tenant:
			self.name = tenant[5]
		else:
			self.name = "无"
		Label(self, text="出租房屋 : %s" % (self.house)).grid(row=0,column=0)
		Label(self, text="租客名称 : %s" % (self.name)).grid(row=1,column=0)
		Label(self, text="费用类型: ").grid(row=2,column=0)
		variable = StringVar(self)
		variable.set("支出")
		self.feeType = OptionMenu(self, variable, "支出", "收入")
		self.feeType.grid(row=2,column=1)
		Label(self, text="金额: ").grid(row=3,column=0)
		self.amount = Entry(self)
		self.amount.grid(row=3,column=1)
		Label(self, text="支付日期: ").grid(row=4,column=0)
		Label(self, text="年 :").grid(row=5,column=0)
		self.payBeforeYearText = Entry(self)
		self.payBeforeYearText.grid(row=5,column=1)
		Label(self, text="月 :").grid(row=5,column=2)
		self.payBeforeMonthText = Entry(self)
		self.payBeforeMonthText.grid(row=5,column=3)
		Label(self, text="日 :").grid(row=5,column=4)
		self.payBeforeDayText = Entry(self)
		self.payBeforeDayText.grid(row=5,column=5)
		Label(self, text="备注 :").grid(row=6,column=0)
		self.NoteText = Entry(self)
		self.NoteText.grid(row=6,column=1)
		saveButton = Button(self, text="保存", command=self.save_fee)
		saveButton.grid(row=7,column=0)
		backButton = Button(self, text="返回", command=lambda city=city, house=house: controller.to_house_detail_page(city, house))
		backButton.grid(row=7,column=1)

	def save_fee(self):
		feeType = self.feeType.cget("text")
		amount = self.amount.get()
		try:
			amount = float(amount)
		except ValueError:
			messagebox.showwarning("警告", "请输入正确的金额")
			return
		payBeforeYear = int(self.payBeforeYearText.get())
		payBeforeMonth = int(self.payBeforeMonthText.get())
		payBeforeDay = int(self.payBeforeDayText.get())
		payBeforeDate = date(year=payBeforeYear, month=payBeforeMonth, day=payBeforeDay)
		note = self.NoteText.get()
		today = date.today()
		if messagebox.askyesno("添加费用", "你确定要添加此费用?"):
			self.controller.c.execute("INSERT INTO FeeList(house, feeType, amount, enter_date, pay_before_date, note) VALUES ('%s', '%s', %d, '%s', '%s', '%s')" % ((self.house, feeType, amount, today, payBeforeDate, note)))
			self.controller.conn.commit()
			messagebox.showinfo("提示", "添加成功!")
			self.controller.to_house_detail_page(self.city, self.house)


class AllPastFeePage(Frame):

	def __init__(self, parent, controller, offset):
		Frame.__init__(self, parent)
		today = date.today()
		self.count=15
		controller.c.execute("SELECT * FROM FeeList WHERE pay_before_date <= '%s' ORDER BY pay_before_date DESC LIMIT %d,%d" % (today,offset*self.count, self.count))
		fees = controller.c.fetchall()
		Label(self, text="房屋").grid(row=1,column=0)
		Label(self, text="类型").grid(row=1,column=1)
		Label(self, text="数额").grid(row=1,column=2)
		Label(self, text="输入日期").grid(row=1,column=3)
		Label(self, text="期限").grid(row=1,column=4)
		Label(self, text="完场日期").grid(row=1,column=5)
		Label(self, text="备注").grid(row=1,column=6)
		row = 2
		num = 0
		for fee in fees:
			Label(self, text=fee[1]).grid(row=row,column=0)
			Label(self, text=fee[2]).grid(row=row,column=1)
			Label(self, text=fee[3]).grid(row=row,column=2)
			Label(self, text=fee[4]).grid(row=row,column=3)
			Label(self, text=fee[5]).grid(row=row,column=4)
			if not fee[6]:
				Button(self, text="结账", command=lambda fee_id=fee[0],time="past",offset=offset: controller.fee_paid(fee_id,None,None,time,offset)).grid(row=row,column=5)
			else:
				Label(self, text=fee[6]).grid(row=row,column=5)
			if not fee[7]:
				Label(self, text="-").grid(row=row,column=6)
			else:
				Label(self, text=fee[7]).grid(row=row,column=6)
			row += 1
			num += 1
		if offset != 0:
			prevButton = Button(self, text="上一页", command=lambda offset=offset-1: controller.to_all_past_fee_page(offset))
			prevButton.grid(row=row,column=4)
		if num == 15:
			nextButton = Button(self, text="下一页", command=lambda offset=offset+1: controller.to_all_past_fee_page(offset))
			nextButton.grid(row=row,column=5)
		backButton = Button(self, text="返回", command=controller.to_home_page)
		backButton.grid(row=row,column=6)


class AllFutureFeePage(Frame):

	def __init__(self, parent, controller, offset):
		Frame.__init__(self, parent)
		today = date.today()
		self.count=15
		controller.c.execute("SELECT * FROM FeeList WHERE pay_before_date >= '%s' ORDER BY pay_before_date LIMIT %d,%d" % (today,offset*self.count, self.count))
		fees = controller.c.fetchall()
		Label(self, text="房屋").grid(row=1,column=0)
		Label(self, text="类型").grid(row=1,column=1)
		Label(self, text="数额").grid(row=1,column=2)
		Label(self, text="输入日期").grid(row=1,column=3)
		Label(self, text="期限").grid(row=1,column=4)
		Label(self, text="完成日期").grid(row=1,column=5)
		Label(self, text="备注").grid(row=1,column=6)
		row = 2
		num = 0
		for fee in fees:
			Label(self, text=fee[1]).grid(row=row,column=0)
			Label(self, text=fee[2]).grid(row=row,column=1)
			Label(self, text=fee[3]).grid(row=row,column=2)
			Label(self, text=fee[4]).grid(row=row,column=3)
			Label(self, text=fee[5]).grid(row=row,column=4)
			if not fee[6]:
				Button(self, text="结账", command=lambda fee_id=fee[0],time="future",offset=offset: controller.fee_paid(fee_id,None,None,time,offset)).grid(row=row,column=5)
			else:
				Label(self, text=fee[6]).grid(row=row,column=5)
			if not fee[7]:
				Label(self, text="-").grid(row=row,column=6)
			else:
				Label(self, text=fee[7]).grid(row=row,column=6)
			row += 1
			num += 1
		if offset != 0:
			prevButton = Button(self, text="上一页", command=lambda offset=offset-1: controller.to_all_future_fee_page(offset))
			prevButton.grid(row=row,column=4)
		if num == 15:
			nextButton = Button(self, text="下一页", command=lambda offset=offset+1: controller.to_all_future_fee_page(offset))
			nextButton.grid(row=row,column=5)
		backButton = Button(self, text="返回", command=controller.to_home_page)
		backButton.grid(row=row,column=6)


class HousePastFeePage(Frame):

	def __init__(self, parent, controller, city, house, offset):
		Frame.__init__(self, parent)
		today = date.today()
		self.count=15
		controller.c.execute("SELECT * FROM FeeList WHERE pay_before_date <= '%s' AND house='%s' ORDER BY pay_before_date DESC LIMIT %d,%d" % (today,house,offset*self.count, self.count))
		fees = controller.c.fetchall()
		Label(self, text="房屋").grid(row=1,column=0)
		Label(self, text="类型").grid(row=1,column=1)
		Label(self, text="数额").grid(row=1,column=2)
		Label(self, text="输入日期").grid(row=1,column=3)
		Label(self, text="期限").grid(row=1,column=4)
		Label(self, text="完成日期").grid(row=1,column=5)
		Label(self, text="备注").grid(row=1,column=6)
		row = 2
		num = 0
		for fee in fees:
			Label(self, text=fee[1]).grid(row=row,column=0)
			Label(self, text=fee[2]).grid(row=row,column=1)
			Label(self, text=fee[3]).grid(row=row,column=2)
			Label(self, text=fee[4]).grid(row=row,column=3)
			Label(self, text=fee[5]).grid(row=row,column=4)
			if not fee[6]:
				Button(self, text="结账", command=lambda fee_id=fee[0],city=city,house=house,time="past",offset=offset: controller.fee_paid(fee_id,city,house,time,offset)).grid(row=row,column=5)
			else:
				Label(self, text=fee[6]).grid(row=row,column=5)
			if not fee[7]:
				Label(self, text="-").grid(row=row,column=6)
			else:
				Label(self, text=fee[7]).grid(row=row,column=6)
			row += 1
			num += 1
		if offset != 0:
			prevButton = Button(self, text="上一页", command=lambda offset=offset-1, house=house: controller.to_house_past_fee_page(house,offset))
			prevButton.grid(row=row,column=4)
		if num == 15:
			nextButton = Button(self, text="下一页", command=lambda offset=offset+1, house=house: controller.to_house_past_fee_page(house,offset))
			nextButton.grid(row=row,column=5)
		backButton = Button(self, text="返回", command = lambda city=city, house=house: controller.to_house_detail_page(city, house))
		backButton.grid(row=row,column=6)

class HouseFutureFeePage(Frame):

	def __init__(self, parent, controller, city, house, offset):
		Frame.__init__(self, parent)
		today = date.today()
		self.count=15
		controller.c.execute("SELECT * FROM FeeList WHERE pay_before_date >= '%s' AND house='%s' ORDER BY pay_before_date LIMIT %d,%d" % (today,house,offset*self.count, self.count))
		fees = controller.c.fetchall()
		Label(self, text="房屋").grid(row=1,column=0)
		Label(self, text="类型").grid(row=1,column=1)
		Label(self, text="数额").grid(row=1,column=2)
		Label(self, text="输入日期").grid(row=1,column=3)
		Label(self, text="期限").grid(row=1,column=4)
		Label(self, text="完成日期").grid(row=1,column=5)
		Label(self, text="备注").grid(row=1,column=6)
		row = 2
		num = 0
		for fee in fees:
			Label(self, text=fee[1]).grid(row=row,column=0)
			Label(self, text=fee[2]).grid(row=row,column=1)
			Label(self, text=fee[3]).grid(row=row,column=2)
			Label(self, text=fee[4]).grid(row=row,column=3)
			Label(self, text=fee[5]).grid(row=row,column=4)
			if not fee[6]:
				Button(self, text="结账", command=lambda fee_id=fee[0],city=city,house=house,time="future",offset=offset: controller.fee_paid(fee_id,city,house,time,offset)).grid(row=row,column=5)
			else:
				Label(self, text=fee[6]).grid(row=row,column=5)
			if not fee[7]:
				Label(self, text="-").grid(row=row,column=6)
			else:
				Label(self, text=fee[7]).grid(row=row,column=6)
			row += 1
			num += 1
		if offset != 0:
			prevButton = Button(self, text="上一页", command=lambda offset=offset-1, house=house: controller.to_house_future_fee_page(house,offset))
			prevButton.grid(row=row,column=4)
		if num == 15:
			nextButton = Button(self, text="下一页", command=lambda offset=offset+1, house=house: controller.to_house_future_fee_page(house,offset))
			nextButton.grid(row=row,column=5)
		backButton = Button(self, text="返回", command = lambda city=city, house=house: controller.to_house_detail_page(city, house))
		backButton.grid(row=row,column=6)

app = RentApp()
app.title("EasyRent")
app.protocol("WM_DELETE_WINDOW", app.on_closing)
app.mainloop()