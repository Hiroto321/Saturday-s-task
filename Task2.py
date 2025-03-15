import requests
import sqlite3
import csv
from datetime import datetime

# Ваш API ключ
API_KEY = 'base64'

# Функция для создания базы данных и таблицы
def create_database():
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS delays (
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

# Функция для получения данных о рейсах из FlightAware API
def fetch_delays(airport_code):
    # Запрос к API FlightAware
    url = f"https://flightaware.com/api/flights?airport={airport_code}&howMany=10"
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }
    response = requests.get(url, headers=headers)

    print(f"Fetching data from FlightAware API - Status Code: {response.status_code}")

    if response.status_code != 200:
        print("Failed to retrieve data")
        return []

    data = response.json()
    delays = []

    # Обработка данных
    for flight in data.get('flights', []):
        flight_number = flight.get('ident', 'N/A')
        origin = flight.get('origin', {}).get('code', 'N/A')
        destination = flight.get('destination', {}).get('code', 'N/A')
        status = flight.get('status', 'unknown')
        delay = flight.get('delay', 0)

        delays.append((flight_number, origin, destination, status, delay))
        print(f"Found flight: {flight_number}, {origin}, {destination}, {status}, {delay}")

    return delays

# Функция для сохранения данных в базу данных
def save_to_database(delays):
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()

    cursor.executemany('''
        INSERT INTO delays (flight_number, origin, destination, status, delay)
        VALUES (?, ?, ?, ?, ?)
    ''', delays)

    conn.commit()
    conn.close()

# Функция для сохранения данных в CSV файл
def save_to_csv(filename):
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM delays')
    rows = cursor.fetchall()

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ID', 'Flight Number', 'Origin', 'Destination', 'Status', 'Delay'])
        writer.writerows(rows)

    conn.close()

# Основной блок выполнения
if __name__ == "__main__":
    create_database()
    airport_code = 'SVO'  # Замените на нужный код аэропорта
    delays = fetch_delays(airport_code)

    if delays:
        save_to_database(delays)
        save_to_csv('delays.csv')
    else:
        print("No delays to save.")