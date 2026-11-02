import psycopg2
import sys
import os
from psycopg2 import OperationalError

# Устанавливаем кодировку UTF-8 для Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    os.environ["PYTHONUTF8"] = "1"

class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_connection()
        return cls._instance
    
    def _init_connection(self):
        try:
            self.connection = psycopg2.connect(
                host="localhost",
                database="shoestore",
                user="postgres",
                password="200703"  # Измените на ваш пароль
            )
            self.cursor = self.connection.cursor()
            print("Подключение к базе данных успешно!")
        except OperationalError as e:
            print(f"Ошибка подключения: {e}")
            self.connection = None
            self.cursor = None
    
    def execute_query(self, query, params=None):
        if not self.connection:
            return None
        
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                return self.cursor.fetchall()
            else:
                self.connection.commit()
                return self.cursor.rowcount
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            self.connection.rollback()
            return None
    
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()