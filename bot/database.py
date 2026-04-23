import sqlite3 as sq
import asyncio
import env
class Database:
    def __init__(self , db_name : str):
        self.conn = sq.connect(db_name)
        self.cur = self.conn.cursor()
        self.lock = asyncio.Lock() 

    async def aread(self, request: str):
        async with self.lock: 
            return self.cur.execute(request ).fetchall()
    # В классе Database (в твоем файле)
    async def awrite(self, request: str, params: tuple = ()):
        async with self.lock:
            self.cur.execute(request, params)
            self.conn.commit()
            return self.cur.lastrowid  # Возвращает ID последней вставки
    def read(self ,request : str):
        return self.cur.execute(request).fetchall()
    def write(self , request: str):
        self.cur.execute(request)
        self.conn.commit()
    def save(self):
        self.conn.commit()
    def close(self):
        self.conn.close()
db = Database(env.db_file)
try:
    db.write("CREATE TABLE IF NOT EXISTS users(id INTEGER , role INTEGER)")#все 
    db.write("CREATE TABLE IF NOT EXISTS students(id INTEGER , class_id INTEGER )")#ученики 
    db.write("CREATE TABLE IF NOT EXISTS teachers_to_class(users_id INTEGER , class_id  INTEGER)")#учителя ( для назначения ДЗ на группу )
    db.write("CREATE TABLE IF NOT EXISTS teachers_to_student(users_id INTEGER , class_id  INTEGER)")#учителя ( для назначения ДЗ на человека )
    db.write("CREATE TABLE IF NOT EXISTS parents(users_id INTEGER , student_id  INTEGER)")# для родоков ( уведомления и тп )
    db.write("CREATE TABLE IF NOT EXISTS tasks( foruser_id  INTEGER, fromuser_id  INTEGER ,task_start INTEGER , task_end INTEGER, graded INTEGER , grade INTEGER, comment INTEGER )")# имя_таска , для_кого , от_кого , проевренно ? , оценка , commentid=  taskid
except:
    print("[?]DATABASE : may be already created ")


#SELECT ROWID FROM users WHERE user_id = 1