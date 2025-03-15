import requests
from bs4 import BeautifulSoup
import sqlite3
import csv

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

# Функция для парсинга данных с сайта
def fetch_delays(airport_code):
    url = f"https://www.flightradar24.com/data/flights/{airport_code}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    delays = []
    # Примерный селектор, зависит от структуры страницы
    for row in soup.select('table tbody tr'):
        cells = row.find_all('td')
        if len(cells) > 0:
            flight_number = cells[0].text.strip()
            origin = cells[1].text.strip()
            destination = cells[2].text.strip()
            status = cells[3].text.strip()
            delay = int(cells[4].text.strip()) if cells[4].text.strip().isdigit() else 0
            
            delays.append((flight_number, origin, destination, status, delay))
    
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
    airport_code = 'JFK'  # Замените на нужный код аэропорта
    delays = fetch_delays(airport_code)
    save_to_database(delays)
    save_to_csv('delays.csv')