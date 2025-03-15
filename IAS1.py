import requests
import sqlite3
import csv
from datetime import datetime

# Функция для создания базы данных и таблицы
def create_database():
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flights (
            id INTEGER PRIMARY KEY,
            flight_number TEXT,
            origin TEXT,
            destination TEXT,
            status TEXT,
            delay INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Функция для получения данных о рейсах из OpenSky API
def fetch_delays():
    url = 'https://opensky-network.org/api/states/all'
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Ошибка при доступе к OpenSky API: {response.status_code}")
        return []

    data = response.json()
    flights = []

    for flight in data['states']:
        flight_number = flight[1]  # Код рейса
        origin = flight[2]          # Код аэропорта вылета
        destination = flight[3]     # Код аэропорта назначения
        status = 'unknown'          # Статус, так как API не предоставляет его
        delay = 0                   # Задержка, так как API не предоставляет ее

        flights.append((flight_number, origin, destination, status, delay))

    return flights

# Функция для сохранения данных в базу данных
def save_to_database(flights):
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()

    cursor.executemany('''
        INSERT INTO flights (flight_number, origin, destination, status, delay)
        VALUES (?, ?, ?, ?, ?)
    ''', flights)

    conn.commit()
    conn.close()

# Функция для сохранения данных в CSV файл
def save_to_csv(filename):
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM flights')
    rows = cursor.fetchall()

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ID', 'Flight Number', 'Origin', 'Destination', 'Status', 'Delay'])
        writer.writerows(rows)

    conn.close()

# Основной блок выполнения
if __name__ == "__main__":
    create_database()
    flights = fetch_delays()

    if flights:
        save_to_database(flights)
        save_to_csv('flights.csv')
        print("Данные успешно сохранены в flights.csv")
    else:
        print("Нет данных для сохранения.")