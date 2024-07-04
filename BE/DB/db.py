import pymysql

#connect
db = pymysql.connect(host="localhost", user="root", password="1234", charset="utf8")
cursor = db.cursor()
cursor.execute('use test;')
cursor.execute('insert into test values("5", "Java", "Java is for programing", 1);')

db.commit()