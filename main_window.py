import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Исправление кодировки для Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

class MainWindow(QMainWindow):
    def __init__(self, user_id, full_name, role):
        super().__init__()
        self.user_id = user_id
        self.full_name = full_name
        self.role = role
        print(f"Создаем MainWindow для {full_name} ({role})")
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f'Личный кабинет - {self.full_name}')
        self.setFixedSize(1600, 900)
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной макет
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Верхняя панель
        header = self.create_header()
        main_layout.addLayout(header)
        
        # Контентная область
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)
        
        # Загружаем окно товаров сразу
        self.load_products_window()
        
        # Устанавливаем активной кнопку товаров
        self.products_button.setProperty("checked", "true")
    
    def create_header(self):
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 10, 20, 10)
        header_layout.setSpacing(0)  # Убираем все отступы между элементами
        
        # ===== ПАНЕЛЬ НАВИГАЦИИ - В ЛЕВЫЙ КРАЙ =====
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(20)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        
        self.products_button = QPushButton('Товары')
        self.products_button.setFixedSize(100, 35)
        self.products_button.setCheckable(True)
        self.products_button.clicked.connect(self.show_products)
        
        if self.role in ['Менеджер', 'Администратор']:
            self.orders_button = QPushButton('Заказы')
            self.orders_button.setFixedSize(100, 35)
            self.orders_button.setCheckable(True)
            self.orders_button.clicked.connect(self.show_orders)
            nav_layout.addWidget(self.orders_button)
        
        nav_layout.addWidget(self.products_button)
        
        # Добавляем панель навигации в левый край
        header_layout.addLayout(nav_layout)
        
        # ===== ГИБКИЙ ПРОМЕЖУТОК =====
        header_layout.addStretch()
        
        # ===== КНОПКА ВЫХОДА - ЧУТЬ ЛЕВЕЕ ОТ ИМЕНИ =====
        logout_button = QPushButton('Выйти')
        logout_button.setFixedSize(80, 35)
        logout_button.clicked.connect(self.logout)
        header_layout.addWidget(logout_button)
        
        # ===== ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ - В САМЫЙ ПРАВЫЙ КРАЙ =====
        user_label = QLabel(f'{self.full_name}')
        user_label.setAlignment(Qt.AlignRight)
        user_font = QFont("Times New Roman", 10, QFont.Bold)
        user_label.setFont(user_font)
        user_label.setStyleSheet("color: #000000; padding-left: 10px; min-width: 150px;")
        header_layout.addWidget(user_label)
        
        return header_layout
    
    def load_products_window(self):
        """Загружает окно товаров"""
        try:
            from products_window import ProductsWindow
            self.products_window = ProductsWindow(self.user_id, self.role)
            self.content_stack.addWidget(self.products_window)
            print("Окно товаров успешно загружено")
        except Exception as e:
            print(f"Ошибка загрузки окна товаров: {e}")
            # Создаем заглушку
            error_widget = QWidget()
            layout = QVBoxLayout(error_widget)
            layout.addWidget(QLabel(f"Ошибка загрузки товаров: {str(e)}"))
            self.content_stack.addWidget(error_widget)
            self.products_window = error_widget
    
    def load_orders_window(self):
        """Загружает окно заказов"""
        try:
            from orders_window import OrdersWindow
            self.orders_window = OrdersWindow(self.user_id, self.role)
            self.content_stack.addWidget(self.orders_window)
            print("Окно заказов успешно загружено")
        except Exception as e:
            print(f"Ошибка загрузки окна заказов: {e}")
            # Создаем заглушку
            error_widget = QWidget()
            layout = QVBoxLayout(error_widget)
            layout.addWidget(QLabel(f"Окно заказов не доступно: {str(e)}"))
            self.content_stack.addWidget(error_widget)
            self.orders_window = error_widget
    
    def show_products(self):
        """Показывает окно товаров"""
        if not hasattr(self, 'products_window'):
            self.load_products_window()
        
        self.products_button.setChecked(True)
        self.products_button.setProperty("checked", "true")
        
        if self.role in ['Менеджер', 'Администратор'] and hasattr(self, 'orders_button'):
            self.orders_button.setChecked(False)
            self.orders_button.setProperty("checked", "false")
        
        self.content_stack.setCurrentWidget(self.products_window)
        
        # Обновляем стили
        self.products_button.style().polish(self.products_button)
        if hasattr(self, 'orders_button'):
            self.orders_button.style().polish(self.orders_button)
    
    def show_orders(self):
        """Показывает окно заказов"""
        if self.role in ['Менеджер', 'Администратор']:
            if not hasattr(self, 'orders_window'):
                self.load_orders_window()
            
            self.orders_button.setChecked(True)
            self.orders_button.setProperty("checked", "true")
            
            self.products_button.setChecked(False)
            self.products_button.setProperty("checked", "false")
            
            self.content_stack.setCurrentWidget(self.orders_window)
            
            # Обновляем стили
            self.orders_button.style().polish(self.orders_button)
            self.products_button.style().polish(self.products_button)
    
    def logout(self):
        from auth_window import AuthWindow
        self.auth_window = AuthWindow()
        self.auth_window.show()
        self.close()