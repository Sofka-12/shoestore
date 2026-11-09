import sys
import os
from decimal import Decimal
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QFont, QColor, QPainter, QPen, QIcon
from database import Database
from order_edit_window import OrderEditWindow

# Исправление кодировки для Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

class ClickableOrderFrame(QFrame):
    """Кликабельный фрейм для плитки заказа"""
    clicked = pyqtSignal(int)  # Сигнал с ID заказа
    
    def __init__(self, order_id):
        super().__init__()
        self.order_id = order_id
    
    def mousePressEvent(self, event):
        """Обработка клика мыши"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.order_id)
        super().mousePressEvent(event)

class OrdersWindow(QWidget):
    def __init__(self, user_id, role):
        super().__init__()
        self.user_id = user_id
        self.role = role
        self.db = Database()
        self.selected_statuses = []  # Выбранные статусы
        self.init_ui()
        self.load_orders()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)
        
        # Заголовок
        title = QLabel('УПРАВЛЕНИЕ ЗАКАЗАМИ')
        title.setFont(QFont("Times New Roman", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("title")
        title.setStyleSheet("margin-bottom: 8px; color: #000000;")
        main_layout.addWidget(title)
        
        # Панель управления - только для администраторов
        if self.role == 'Администратор':
            control_widget = QWidget()
            control_widget.setFixedHeight(50)
            control_layout = QHBoxLayout(control_widget)
            control_layout.setContentsMargins(0, 0, 0, 0)
            control_layout.setSpacing(15)
            
            # Левая часть - кнопка добавления
            left_widget = QWidget()
            left_layout = QHBoxLayout(left_widget)
            left_layout.setContentsMargins(0, 0, 0, 0)
            left_layout.setSpacing(10)
            
            # Кнопка добавления (только для админа)
            self.add_button = QPushButton('Добавить заказ')
            self.add_button.setFixedHeight(50)
            self.add_button.setMinimumWidth(140)
            self.add_button.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    border: 1px solid #000000;
                    padding: 8px 15px;
                    font-size: 11pt;
                    color: #000000;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #F0F0F0;
                }
                QPushButton:pressed {
                    background-color: #E0E0E0;
                }
            """)
            self.add_button.clicked.connect(self.add_order)
            
            left_layout.addWidget(self.add_button)
            left_layout.addStretch()
            control_layout.addWidget(left_widget)
            
            # Правая часть - поиск и фильтр
            right_widget = QWidget()
            right_layout = QHBoxLayout(right_widget)
            right_layout.setContentsMargins(0, 0, 0, 0)
            right_layout.setSpacing(8)
            
            # Кнопка фильтра
            self.filter_button = QPushButton('Фильтр')
            self.filter_button.setFixedHeight(50)
            self.filter_button.setMinimumWidth(80)
            self.filter_button.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    border: 1px solid #000000;
                    padding: 8px 15px;
                    font-size: 11pt;
                    color: #000000;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #F0F0F0;
                }
                QPushButton:pressed {
                    background-color: #E0F0F0;
                }
            """)
            self.filter_button.clicked.connect(self.show_filter_dialog)
            right_layout.addWidget(self.filter_button)
            
            # Поле поиска
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText('Поиск заказов...')
            self.search_input.setFixedHeight(36)
            self.search_input.setMinimumWidth(280)
            self.search_input.textChanged.connect(self.search_orders)
            
            self.search_input.setStyleSheet("""
                QLineEdit {
                    background-color: #FFFFFF;
                    border: 1px solid #000000;
                    padding: 8px 15px;
                    font-size: 11pt;
                    color: #000000;
                }
                QLineEdit:focus {
                    border: 1px solid #000000;
                    background-color: #FFFFFF;
                }
                QLineEdit::placeholder {
                    color: #666666;
                    font-style: italic;
                    font-size: 10.5pt;
                }
            """)
            
            right_layout.addWidget(self.search_input)
            right_layout.addStretch()
            control_layout.addWidget(right_widget)
            
            main_layout.addWidget(control_widget)
            
            # Отступ между панелью и плитками
            spacer = QWidget()
            spacer.setFixedHeight(15)
            spacer.setStyleSheet("background-color: transparent;")
            main_layout.addWidget(spacer)
        
        # Контейнер для плиток заказов
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #FFFFFF;
            }
        """)
        
        # Контейнер с плитками
        self.orders_container = QWidget()
        self.vertical_layout = QVBoxLayout(self.orders_container)
        self.vertical_layout.setSpacing(15)  # Отступы между плитками
        self.vertical_layout.setContentsMargins(8, 0, 8, 8)
        self.vertical_layout.setAlignment(Qt.AlignTop)
        
        self.scroll_area.setWidget(self.orders_container)
        main_layout.addWidget(self.scroll_area)
        
        self.setLayout(main_layout)
    
    def load_orders(self, search_text=""):
        # Загружаем заказы из БД с учетом фильтров
        query_parts = []
        params = []
        
        # Базовый запрос
        base_query = """
            SELECT o.order_id, o.order_number, u.full_name as customer_name, 
                   o.status, dp.address as delivery_point, o.order_date, 
                   o.delivery_date, o.total_amount, o.pickup_code
            FROM orders o
            LEFT JOIN users u ON o.user_id = u.user_id
            LEFT JOIN delivery_points dp ON o.delivery_point_id = dp.point_id
            WHERE 1=1
        """
        
        # Добавляем поиск по тексту (только для администраторов)
        if search_text and hasattr(self, 'search_input'):
            query_parts.append("""
                AND (o.order_number ILIKE %s OR u.full_name ILIKE %s OR dp.address ILIKE %s)
            """)
            search_pattern = f'%{search_text}%'
            params.extend([search_pattern, search_pattern, search_pattern])
        
        # Добавляем фильтр по статусам
        if self.selected_statuses:
            placeholders = ', '.join(['%s'] * len(self.selected_statuses))
            query_parts.append(f"AND o.status IN ({placeholders})")
            params.extend(self.selected_statuses)
        
        # Собираем базовый запрос
        query = base_query + ' '.join(query_parts) + " ORDER BY o.order_date DESC"
        
        orders = self.db.execute_query(query, tuple(params) if params else None)
        
        if orders:
            self.display_orders(orders)
        else:
            # Очищаем контейнер если заказов нет
            while self.vertical_layout.count():
                item = self.vertical_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # Показываем сообщение "Заказов нет"
            no_orders_label = QLabel('Заказы не найдены')
            no_orders_label.setFont(QFont("Times New Roman", 12))
            no_orders_label.setAlignment(Qt.AlignCenter)
            no_orders_label.setStyleSheet("color: #666666; padding: 30px;")
            self.vertical_layout.addWidget(no_orders_label)
    
    def show_filter_dialog(self):
        """Показывает диалоговое окно фильтра"""
        if self.role != 'Администратор':
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle('Фильтр заказов')
        dialog.setFixedSize(500, 400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
            QLabel {
                font-family: "Times New Roman";
                font-size: 11pt;
                color: #000000;
            }
            QPushButton {
                background-color: #F0F0F0;
                color: #000000;
                border: 1px solid #000000;
                padding: 8px 16px;
                font-size: 10pt;
                font-weight: bold;
                font-family: "Times New Roman";
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title = QLabel('ФИЛЬТРАЦИЯ ЗАКАЗОВ')
        title.setFont(QFont("Times New Roman", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Получаем уникальные статусы из БД
        statuses_query = "SELECT DISTINCT status FROM orders WHERE status IS NOT NULL ORDER BY status"
        statuses_result = self.db.execute_query(statuses_query)
        statuses = [s[0] for s in statuses_result] if statuses_result else []
        
        # Создаем скроллируемую область
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("border: none;")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        
        # Статусы
        if statuses:
            statuses_group = QGroupBox('Статусы заказов')
            statuses_group.setFont(QFont("Times New Roman", 12, QFont.Bold))
            statuses_group.setStyleSheet("""
                QGroupBox {
                    border: 1px solid #000000;
                    margin-top: 10px;
                    padding-top: 10px;
                    font-weight: bold;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
            """)
            
            statuses_layout = QVBoxLayout()
            
            # Кнопка "Выбрать все"
            select_all_status = QPushButton('Выбрать все')
            select_all_status.setFixedHeight(30)
            select_all_status.clicked.connect(lambda: self.select_all_checkboxes(statuses_checkboxes, True))
            statuses_layout.addWidget(select_all_status)
            
            # Кнопка "Очистить все"
            clear_all_status = QPushButton('Очистить все')
            clear_all_status.setFixedHeight(30)
            clear_all_status.clicked.connect(lambda: self.select_all_checkboxes(statuses_checkboxes, False))
            statuses_layout.addWidget(clear_all_status)
            
            statuses_checkboxes = []
            for status in statuses:
                checkbox = QCheckBox(status)
                checkbox.setFont(QFont("Times New Roman", 10))
                checkbox.setStyleSheet("""
                    QCheckBox {
                        padding: 5px;
                        color: #000000;
                    }
                    QCheckBox::indicator {
                        width: 16px;
                        height: 16px;
                    }
                """)
                if status in self.selected_statuses:
                    checkbox.setChecked(True)
                statuses_checkboxes.append(checkbox)
                statuses_layout.addWidget(checkbox)
            
            statuses_layout.addStretch()
            statuses_group.setLayout(statuses_layout)
            scroll_layout.addWidget(statuses_group)
        
        scroll_layout.addStretch()
        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        apply_button = QPushButton('Применить')
        apply_button.setFixedHeight(40)
        apply_button.setMinimumWidth(120)
        apply_button.clicked.connect(lambda: self.apply_filters(
            dialog, statuses_checkboxes if statuses else []
        ))
        
        reset_button = QPushButton('Сбросить фильтры')
        reset_button.setFixedHeight(40)
        reset_button.setMinimumWidth(140)
        reset_button.clicked.connect(lambda: self.reset_filters(dialog))
        
        cancel_button = QPushButton('Отмена')
        cancel_button.setFixedHeight(40)
        cancel_button.setMinimumWidth(100)
        cancel_button.clicked.connect(dialog.reject)
        
        buttons_layout.addWidget(reset_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(apply_button)
        
        layout.addLayout(buttons_layout)
        
        dialog.exec_()
    
    def select_all_checkboxes(self, checkboxes, selected):
        """Выбирает или очищает все checkbox"""
        for checkbox in checkboxes:
            checkbox.setChecked(selected)
    
    def apply_filters(self, dialog, statuses_checkboxes):
        """Применяет выбранные фильтры"""
        # Сохраняем выбранные статусы
        self.selected_statuses = []
        for checkbox in statuses_checkboxes:
            if checkbox.isChecked():
                self.selected_statuses.append(checkbox.text())
        
        dialog.accept()
        # Перезагружаем заказы с учетом фильтров
        self.load_orders(self.search_input.text() if hasattr(self, 'search_input') else "")
    
    def reset_filters(self, dialog):
        """Сбрасывает все фильтры"""
        self.selected_statuses = []
        dialog.accept()
        # Перезагружаем заказы без фильтров
        self.load_orders(self.search_input.text() if hasattr(self, 'search_input') else "")
    
    def display_orders(self, orders):
        # Очищаем текущие плитки
        while self.vertical_layout.count():
            item = self.vertical_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Заполняем плитками
        for order in orders:
            (order_id, order_number, customer_name, status, 
             delivery_point, order_date, delivery_date, total_amount, pickup_code) = order
            
            # Преобразуем даты
            order_date_str = str(order_date)[:10] if order_date else "Не указана"
            delivery_date_str = str(delivery_date)[:10] if delivery_date else "Не указана"
            
            # Преобразуем сумму
            total_amount_float = float(total_amount) if isinstance(total_amount, Decimal) else float(total_amount or 0)
            
            # Создаем плитку заказа
            order_card = self.create_order_card(
                order_id, order_number, customer_name, status, 
                delivery_point, order_date_str, delivery_date_str, 
                total_amount_float, pickup_code
            )
            
            # Добавляем плитку в вертикальный список
            self.vertical_layout.addWidget(order_card)
        
        # Добавляем растяжение в конце
        self.vertical_layout.addStretch()
    
    def create_order_card(self, order_id, order_number, customer_name, status, 
                         delivery_point, order_date, delivery_date, total_amount, pickup_code):
        """Создает плитку заказа с двумя частями и угольными блоками"""
        # Используем кликабельный фрейм
        card = ClickableOrderFrame(order_id)
        card.setObjectName("order_card")
        card.setMinimumHeight(220)
        card.setMaximumHeight(280)
        
        # ВСЕГДА БЕЛЫЙ ФОН - убрана зависимость от статуса
        bg_color = '#FFFFFF'  # Всегда белый
        text_color = '#000000'  # Всегда черный текст
        
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #F5F5F5;  /* Светлый фон всей плитки */
                margin: 5px;
                border: 2px solid #000000;
                border-radius: 5px;
            }}
            QFrame:hover {{
                background-color: #EDEDED;
            }}
        """)
        
        # Подключаем обработчик клика (только для администраторов)
        if self.role == 'Администратор':
            card.clicked.connect(self.on_order_clicked)
        
        # Основной горизонтальный макет для плитки с двумя частями
        main_card_layout = QHBoxLayout(card)
        main_card_layout.setSpacing(0)
        main_card_layout.setContentsMargins(0, 0, 0, 0)
        
        # ===== ЧАСТЬ 1: ИНФОРМАЦИЯ О ЗАКАЗЕ =====
        part1 = QWidget()
        part1_layout = QVBoxLayout(part1)
        part1_layout.setSpacing(0)
        part1_layout.setContentsMargins(0, 0, 0, 0)
        
        # Заголовок части 1 - ВСЕГДА БЕЛЫЙ
        part1_header = QWidget()
        part1_header.setFixedHeight(40)
        part1_header.setStyleSheet("background-color: #FFFFFF; border-bottom: 2px solid #000000;")
        part1_header_layout = QHBoxLayout(part1_header)
        part1_header_layout.setContentsMargins(10, 0, 10, 0)
        
        part1_layout.addWidget(part1_header)
        
        # Контейнер для блоков части 1
        part1_content = QWidget()
        part1_content_layout = QVBoxLayout(part1_content)
        part1_content_layout.setSpacing(0)
        part1_content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Блок 1.1: Артикул заказа
        block1 = QWidget()
        block1.setMinimumHeight(50)
        block1.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border-bottom: 1px solid #000000;
            }
        """)
        block1_layout = QHBoxLayout(block1)
        block1_layout.setContentsMargins(15, 0, 15, 0)
        
        block1_label = QLabel('Артикул заказа:')
        block1_label.setFont(QFont("Times New Roman", 11, QFont.Bold))
        block1_label.setStyleSheet("color: #000000; min-width: 140px;")
        
        block1_value = QLabel(order_number)
        block1_value.setFont(QFont("Times New Roman", 12))
        block1_value.setStyleSheet("color: #000000; font-weight: bold;")
        block1_value.setWordWrap(True)
        
        block1_layout.addWidget(block1_label)
        block1_layout.addWidget(block1_value, 1)
        part1_content_layout.addWidget(block1)
        
        # Блок 1.2: Статус заказа - ВСЕГДА СЕРЫЙ ФОН
        block2 = QWidget()
        block2.setMinimumHeight(50)
        block2.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border-bottom: 1px solid #000000;
            }
        """)
        block2_layout = QHBoxLayout(block2)
        block2_layout.setContentsMargins(15, 0, 15, 0)
        
        block2_label = QLabel('Статус заказа:')
        block2_label.setFont(QFont("Times New Roman", 11, QFont.Bold))
        block2_label.setStyleSheet("color: #000000; min-width: 140px;")
        
        block2_value = QLabel(status)
        block2_value.setFont(QFont("Times New Roman", 11))
        block2_value.setStyleSheet("""
            QLabel {
                color: #000000;
                background-color: #F0F0F0;  /* Всегда серый фон */
                padding: 5px 12px;
                border-radius: 4px;
                font-weight: bold;
                border: 1px solid #000000;
            }
        """)
        block2_value.setWordWrap(True)
        
        block2_layout.addWidget(block2_label)
        block2_layout.addWidget(block2_value, 1)
        part1_content_layout.addWidget(block2)
        
        # Блок 1.3: Адрес пункта выдачи
        block3 = QWidget()
        block3.setMinimumHeight(50)
        block3.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border-bottom: 1px solid #000000;
            }
        """)
        block3_layout = QHBoxLayout(block3)
        block3_layout.setContentsMargins(15, 0, 15, 0)
        
        block3_label = QLabel('Адрес пункта выдачи:')
        block3_label.setFont(QFont("Times New Roman", 11, QFont.Bold))
        block3_label.setStyleSheet("color: #000000; min-width: 140px;")
        
        block3_value = QLabel(delivery_point if delivery_point else 'Не указан')
        block3_value.setFont(QFont("Times New Roman", 10))
        block3_value.setStyleSheet("color: #000000;")
        block3_value.setWordWrap(True)
        
        block3_layout.addWidget(block3_label)
        block3_layout.addWidget(block3_value, 1)
        part1_content_layout.addWidget(block3)
        
        # Блок 1.4: Дата заказа
        block4 = QWidget()
        block4.setMinimumHeight(50)
        block4.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
            }
        """)
        block4_layout = QHBoxLayout(block4)
        block4_layout.setContentsMargins(15, 0, 15, 0)
        
        block4_label = QLabel('Дата заказа:')
        block4_label.setFont(QFont("Times New Roman", 11, QFont.Bold))
        block4_label.setStyleSheet("color: #000000; min-width: 140px;")
        
        block4_value = QLabel(order_date)
        block4_value.setFont(QFont("Times New Roman", 12))
        block4_value.setStyleSheet("""
            QLabel {
                color: #000000;
                background-color: #F0F0F0;
                padding: 5px 12px;
                border-radius: 4px;
                font-weight: bold;
                border: 1px solid #000000;
            }
        """)
        block4_value.setWordWrap(True)
        
        block4_layout.addWidget(block4_label)
        block4_layout.addWidget(block4_value, 1)
        part1_content_layout.addWidget(block4)
        
        part1_layout.addWidget(part1_content, 1)  # Добавляем растяжение
        main_card_layout.addWidget(part1, 2)  # Часть 1 занимает 2/3 ширины
        
        # ===== РАЗДЕЛИТЕЛЬ МЕЖДУ ЧАСТЯМИ =====
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #000000;")
        separator.setMaximumWidth(3)
        main_card_layout.addWidget(separator)
        
        # ===== ЧАСТЬ 2: ДАТА ДОСТАВКИ =====
        part2 = QWidget()
        part2_layout = QVBoxLayout(part2)
        part2_layout.setSpacing(0)
        part2_layout.setContentsMargins(0, 0, 0, 0)
        
        # Заголовок части 2 - ВСЕГДА БЕЛЫЙ
        part2_header = QWidget()
        part2_header.setFixedHeight(40)
        part2_header.setStyleSheet("background-color: #FFFFFF; border-bottom: 2px solid #000000;")
        part2_header_layout = QHBoxLayout(part2_header)
        part2_header_layout.setContentsMargins(10, 0, 10, 0)
        
        part2_layout.addWidget(part2_header)
        
        # Контейнер для блока даты доставки
        part2_content = QWidget()
        part2_content_layout = QVBoxLayout(part2_content)
        part2_content_layout.setSpacing(0)
        part2_content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Блок даты доставки (занимает всю доступную высоту)
        delivery_date_widget = QWidget()
        delivery_date_widget.setStyleSheet("background-color: #FFFFFF;")
        delivery_date_layout = QVBoxLayout(delivery_date_widget)
        delivery_date_layout.setSpacing(5)
        delivery_date_layout.setContentsMargins(20, 20, 20, 20)
        delivery_date_layout.setAlignment(Qt.AlignCenter)
        
        delivery_date_value = QLabel(delivery_date)
        delivery_date_value.setFont(QFont("Times New Roman", 16, QFont.Bold))
        delivery_date_value.setAlignment(Qt.AlignCenter)
        delivery_date_value.setStyleSheet("""
            QLabel {
                color: #000000;
                background-color: #F0F0F0;
                padding: 10px 20px;
                border-radius: 8px;
                border: 2px solid #000000;
                min-height: 40px;
            }
        """)
        delivery_date_value.setWordWrap(True)
        
        delivery_date_layout.addWidget(delivery_date_value, 1)
        
        part2_content_layout.addWidget(delivery_date_widget, 1)
        part2_layout.addWidget(part2_content, 1)
        main_card_layout.addWidget(part2, 1)  # Часть 2 занимает 1/3 ширины
        
        return card
    
    def on_order_clicked(self, order_id):
        """Обработчик клика по плитке заказа (только для администраторов)"""
        if self.role == 'Администратор':
            edit_window = OrderEditWindow(order_id, self.role)
            edit_window.order_saved.connect(self.load_orders)
            # НОВОЕ: Подключаем сигнал удаления заказа
            edit_window.order_deleted.connect(self.handle_order_deleted)
            edit_window.exec_()
    
    def handle_order_deleted(self, order_id):
        """Обработчик удаления заказа"""
        # Обновляем список заказов после удаления
        self.load_orders(self.search_input.text() if hasattr(self, 'search_input') else "")
    
    def search_orders(self):
        """Поиск заказов"""
        if hasattr(self, 'search_input'):
            search_text = self.search_input.text()
            self.load_orders(search_text)
    
    def add_order(self):
        """Добавление заказа (только для администраторов)"""
        if self.role == 'Администратор':
            edit_window = OrderEditWindow(None, self.role)
            edit_window.order_saved.connect(self.load_orders)
            edit_window.exec_()

# Для тестирования
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OrdersWindow(None, 'Администратор')
    window.show()
    sys.exit(app.exec_())
