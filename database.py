import threading
import sqlite3
import time

lock = threading.Lock()

# Подключаемся к файлу базы данных
con = sqlite3.connect("main.db", check_same_thread=False)
# Берём управление базой данных
cur = con.cursor()

# Создаём таблицу данных земли, если не создана
cur.execute("create table if not exists ground (id INTEGER PRIMARY KEY AUTOINCREMENT, humidity FLOAT NOT NULL, timestamp BIGINT NOT NULL)")

# Создаём таблицу данных воздуха, если не создана
cur.execute("create table if not exists air (id INTEGER PRIMARY KEY AUTOINCREMENT, temperature FLOAT NOT NULL, humidity FLOAT NOT NULL, timestamp BIGINT NOT NULL)")

def execute_and_commit(sql, parameters = ()):
    """Выполняем sql команду и сразу сохраняем её в файл"""

    try:
        lock.acquire(True)

        cur.execute(sql, parameters)
        con.commit()
    finally:
        lock.release()

    return

def execute_and_fetchall(sql, parameters = ()):
    """Выполняем sql команду и сразу возвращаем результат"""

    try:
        lock.acquire(True)

        cur.execute(sql, parameters)
        ret = cur.fetchall()
    finally:
        lock.release()

    return ret

def add_ground_hum(humidity):
    """Добавляем данные о влажности земли"""

    if humidity == None:
        humidity = 0

    cur_time = round(time.time())
    
    execute_and_commit("INSERT into ground (humidity, timestamp) values (?, ?)", (humidity, cur_time))

    return True

def add_air_temp_hum(temperature, humidity):
    """Добавляем данные о температуре и влажности воздуха"""

    if temperature == None:
        temperature = 0

    if humidity == None:
        humidity = 0

    cur_time = round(time.time())

    execute_and_commit("INSERT into air (temperature, humidity, timestamp) values (?, ?, ?)", (temperature, humidity, cur_time))

    return True
