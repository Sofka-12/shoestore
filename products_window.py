import sys
import os
from decimal import Decimal
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QFont, QColor, QPainter, QPen, QIcon
from database import Database
from product_edit_window import ProductEditWindow

# Исправление кодировки для Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

class ClickableFrame(QFrame):
    """Кликабельный фрейм для плитки товара"""
    clicked = pyqtSignal(int)  # Сигнал с ID товара
    
    def __init__(self, product_id):
        super().__init__()
        self.product_id = product_id
    
    def mousePressEvent(self, event):
        """Обработка клика мыши"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.product_id)
        super().mousePressEvent(event)

class ProductsWindow(QWidget):
    def __init__(self, user_id, role):
        super().__init__()
        self.user_id = user_id
        self.role = role
        self.db = Database()
        self.selected_manufacturers = []  # Выбранные производители
        self.selected_categories = []  # Выбранные категории
        self.selected_supplier = "Все поставщики"  # Выбранный поставщик
        self.quantity_sort = "none"  # Сортировка количества: "none", "asc", "desc"
        self.init_ui()
        self.load_products()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)
        
        # Заголовок
        title = QLabel('КАТАЛОГ ТОВАРОВ')
        title.setFont(QFont("Times New Roman", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("title")
        title.setStyleSheet("margin-bottom: 8px; color: #000000;")
        main_layout.addWidget(title)
        
        # Панель управления - для администраторов и менеджеров
        if self.role in ['Администратор', 'Менеджер']:
            control_widget = QWidget()
            control_widget.setFixedHeight(60)
            control_widget.setStyleSheet("background-color: transparent;")
            
            control_layout = QHBoxLayout(control_widget)
            control_layout.setContentsMargins(0, 0, 0, 0)
            control_layout.setSpacing(15)
            
            # ЛЕВАЯ часть панели - кнопка добавления (ТОЛЬКО ДЛЯ АДМИНИСТРАТОРОВ)
            left_panel = QWidget()
            left_panel.setStyleSheet("background-color: transparent;")
            left_layout = QHBoxLayout(left_panel)
            left_layout.setContentsMargins(0, 0, 0, 0)
            left_layout.setSpacing(10)
            
            # Кнопка добавления товара - только для администраторов
            if self.role == 'Администратор':
                self.add_button = QPushButton('Добавить товар')
                self.add_button.setFixedHeight(45)
                self.add_button.setMinimumWidth(160)
                self.add_button.setStyleSheet("""
                    QPushButton {
                        background-color: #FFFFFF;
                        border: 2px solid #000000;
                        padding: 10px 20px;
                        font-size: 12pt;
                        color: #000000;
                        font-weight: bold;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #F0F0F0;
                        border: 2px solid #333333;
                    }
                    QPushButton:pressed {
                        background-color: #E0E0E0;
                    }
                """)
                self.add_button.clicked.connect(self.add_product)
                left_layout.addWidget(self.add_button)
            
            left_layout.addStretch()
            
            # ПРАВАЯ часть панели - поиск и фильтры (ДЛЯ ВСЕХ МЕНЕДЖЕРОВ И АДМИНИСТРАТОРОВ)
            right_panel = QWidget()
            right_panel.setStyleSheet("background-color: transparent;")
            right_layout = QHBoxLayout(right_panel)
            right_layout.setContentsMargins(0, 0, 0, 0)
            right_layout.setSpacing(10)
            
           
            
            # Кнопка сортировки количества (ДЛЯ ВСЕХ МЕНЕДЖЕРОВ И АДМИНИСТРАТОРОВ)
            self.quantity_sort_button = QPushButton('Кол-во ↑↓')
            self.quantity_sort_button.setFixedHeight(45)
            self.quantity_sort_button.setMinimumWidth(120)
            self.quantity_sort_button.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    border: 2px solid #000000;
                    padding: 10px 15px;
                    font-size: 11pt;
                    color: #000000;
                    font-weight: bold;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #F0F0F0;
                    border: 2px solid #333333;
                }
                QPushButton:pressed {
                    background-color: #E0E0E0;
                }
            """)
            self.quantity_sort_button.clicked.connect(self.toggle_quantity_sort)
            right_layout.addWidget(self.quantity_sort_button)
            
            # Фильтр по поставщику (ДЛЯ ВСЕХ МЕНЕДЖЕРОВ И АДМИНИСТРАТОРОВ)
            self.supplier_combo = QComboBox()
            self.supplier_combo.setFixedHeight(45)
            self.supplier_combo.setMinimumWidth(200)
            self.supplier_combo.setStyleSheet("""
                QComboBox {
                    background-color: #FFFFFF;
                    border: 2px solid #000000;
                    padding: 10px 15px;
                    font-size: 11pt;
                    color: #000000;
                    border-radius: 4px;
                }
                QComboBox:hover {
                    border: 2px solid #333333;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 30px;
                }
                QComboBox::down-arrow {
                    width: 16px;
                    height: 16px;
                }
                QComboBox QAbstractItemView {
                    background-color: #FFFFFF;
                    border: 1px solid #000000;
                    selection-background-color: #F0F0F0;
                    selection-color: #000000;
                    font-size: 11pt;
                }
            """)
            self.supplier_combo.currentTextChanged.connect(self.on_supplier_changed)
            right_layout.addWidget(self.supplier_combo)
            
            # Поле поиска (ДЛЯ ВСЕХ МЕНЕДЖЕРОВ И АДМИНИСТРАТОРОВ)
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText('Поиск...')
            self.search_input.setFixedHeight(45)
            self.search_input.setMinimumWidth(300)
            self.search_input.textChanged.connect(self.search_products)
            
            self.search_input.setStyleSheet("""
                QLineEdit {
                    background-color: #FFFFFF;
                    border: 2px solid #000000;
                    padding: 10px 15px;
                    font-size: 11pt;
                    color: #000000;
                    border-radius: 4px;
                }
                QLineEdit:focus {
                    border: 2px solid #333333;
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
            
            # Собираем панель управления
            control_layout.addWidget(left_panel, 1)
            control_layout.addWidget(right_panel, 2)
            
            main_layout.addWidget(control_widget)
            
            # Отступ между панелью и плитками
            spacer = QWidget()
            spacer.setFixedHeight(15)
            spacer.setStyleSheet("background-color: transparent;")
            main_layout.addWidget(spacer)
        
        # Контейнер для плиток товаров
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
        self.products_container = QWidget()
        self.vertical_layout = QVBoxLayout(self.products_container)
        self.vertical_layout.setSpacing(15)
        self.vertical_layout.setContentsMargins(8, 0, 8, 8)
        self.vertical_layout.setAlignment(Qt.AlignTop)
        
        self.scroll_area.setWidget(self.products_container)
        main_layout.addWidget(self.scroll_area)
        
        self.setLayout(main_layout)
        
        # Загружаем список поставщиков и обновляем UI
        if self.role in ['Администратор', 'Менеджер']:
            self.load_suppliers()
            self.update_quantity_sort_button_text()
    
    def load_suppliers(self):
        """Загружает список поставщиков для комбобокса"""
        query = "SELECT DISTINCT supplier FROM products WHERE supplier IS NOT NULL ORDER BY supplier"
        suppliers_result = self.db.execute_query(query)
        suppliers = ["Все поставщики"]  # Первый элемент - "Все поставщики"
        
        if suppliers_result:
            suppliers.extend([s[0] for s in suppliers_result])
        
        self.supplier_combo.clear()
        self.supplier_combo.addItems(suppliers)
        
        # Устанавливаем сохраненное значение
        self.supplier_combo.setCurrentText(self.selected_supplier)
    
    def on_supplier_changed(self, supplier):
        """Обработчик изменения выбранного поставщика"""
        self.selected_supplier = supplier
        self.load_products(self.search_input.text() if hasattr(self, 'search_input') else "")
    
    def update_quantity_sort_button_text(self):
        """Обновляет текст кнопки сортировки количества"""
        if self.quantity_sort == "none":
            self.quantity_sort_button.setText('Кол-во ↑↓')
            self.quantity_sort_button.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    border: 2px solid #000000;
                    padding: 10px 15px;
                    font-size: 11pt;
                    color: #000000;
                    font-weight: bold;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #F0F0F0;
                    border: 2px solid #333333;
                }
                QPushButton:pressed {
                    background-color: #E0E0E0;
                }
            """)
        elif self.quantity_sort == "asc":
            self.quantity_sort_button.setText('Кол-во ↑')
            self.quantity_sort_button.setStyleSheet("""
                QPushButton {
                    background-color: #F0F0F0;
                    border: 2px solid #000000;
                    padding: 10px 15px;
                    font-size: 11pt;
                    color: #000000;
                    font-weight: bold;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #E0E0E0;
                }
                QPushButton:pressed {
                    background-color: #D0D0D0;
                }
            """)
        elif self.quantity_sort == "desc":
            self.quantity_sort_button.setText('Кол-во ↓')
            self.quantity_sort_button.setStyleSheet("""
                QPushButton {
                    background-color: #F0F0F0;
                    border: 2px solid #000000;
                    padding: 10px 15px;
                    font-size: 11pt;
                    color: #000000;
                    font-weight: bold;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #E0E0E0;
                }
                QPushButton:pressed {
                    background-color: #D0D0D0;
                }
            """)
    
    def toggle_quantity_sort(self):
        """Переключает режим сортировки количества"""
        if self.quantity_sort == "none":
            self.quantity_sort = "asc"  # По возрастанию
        elif self.quantity_sort == "asc":
            self.quantity_sort = "desc"  # По убыванию
        else:
            self.quantity_sort = "none"  # Без сортировки
        
        self.update_quantity_sort_button_text()
        # Перезагружаем товары с новой сортировкой
        self.load_products(self.search_input.text() if hasattr(self, 'search_input') else "")
    
    def load_products(self, search_text=""):
        """Загружает товары с учетом всех фильтров, поиска и сортировки"""
        query_parts = []
        params = []
        
        # Базовый запрос
        base_query = """
            SELECT product_id, name, category, price, discount, quantity, 
                   description, manufacturer, supplier, unit, photo_path
            FROM products 
            WHERE 1=1
        """
        
        # Добавляем расширенный поиск по тексту (для менеджеров и администраторов)
        if search_text and hasattr(self, 'search_input') and self.role in ['Администратор', 'Менеджер']:
            # Разбиваем поисковый запрос на отдельные слова
            search_words = [word.strip() for word in search_text.strip().split() if word.strip()]
            
            if search_words:
                # Создаем список условий для каждого слова
                word_conditions_list = []
                
                for word in search_words:
                    word_conditions = []
                    search_pattern = f'%{word}%'
                    
                    # Поиск по всем текстовым полям для каждого слова
                    text_fields = [
                        'name', 'category', 'manufacturer', 'supplier', 
                        'description', 'unit'
                    ]
                    
                    for field in text_fields:
                        word_conditions.append(f"{field} ILIKE %s")
                        params.append(search_pattern)
                    
                    # Также проверяем числовые поля, если слово - число
                    if word.replace('.', '', 1).isdigit():
                        try:
                            search_number = float(word)
                            # Поиск по цене (точное совпадение или округленное)
                            word_conditions.append(f"ROUND(price::numeric, 2) = ROUND(%s::numeric, 2)")
                            params.append(search_number)
                            
                            # Поиск по количеству (точное совпадение)
                            if '.' not in word:
                                word_conditions.append(f"quantity = %s")
                                params.append(int(word))
                            
                            # Поиск по скидке (точное совпадение)
                            word_conditions.append(f"discount = %s")
                            params.append(int(search_number))
                        except:
                            pass
                    
                    # Объединяем условия для одного слова с OR
                    if word_conditions:
                        word_conditions_list.append(f"({' OR '.join(word_conditions)})")
                
                # Объединяем условия для всех слов с AND
                if word_conditions_list:
                    query_parts.append(f"AND ({' AND '.join(word_conditions_list)})")
        
        # Добавляем фильтр по производителям (для менеджеров и администраторов)
        if self.selected_manufacturers and self.role in ['Администратор', 'Менеджер']:
            placeholders = ', '.join(['%s'] * len(self.selected_manufacturers))
            query_parts.append(f"AND manufacturer IN ({placeholders})")
            params.extend(self.selected_manufacturers)
        
        # Добавляем фильтр по категориям (для менеджеров и администраторов)
        if self.selected_categories and self.role in ['Администратор', 'Менеджер']:
            placeholders = ', '.join(['%s'] * len(self.selected_categories))
            query_parts.append(f"AND category IN ({placeholders})")
            params.extend(self.selected_categories)
        
        # Добавляем фильтр по поставщику (для менеджеров и администраторов)
        if self.selected_supplier and self.selected_supplier != "Все поставщики" and self.role in ['Администратор', 'Менеджер']:
            query_parts.append("AND supplier = %s")
            params.append(self.selected_supplier)
        
        # Собираем базовый запрос
        query = base_query + ' '.join(query_parts)
        
        # Добавляем сортировку по количеству (для менеджеров и администраторов)
        if self.role in ['Администратор', 'Менеджер']:
            if self.quantity_sort == "asc":
                query += " ORDER BY quantity ASC NULLS LAST"
            elif self.quantity_sort == "desc":
                query += " ORDER BY quantity DESC NULLS LAST"
            else:
                query += " ORDER BY product_id"
        else:
            # Для гостей и авторизованных пользователей - обычная сортировка по ID
            query += " ORDER BY product_id"
        
        products = self.db.execute_query(query, tuple(params) if params else None)
        
        if products:
            self.display_products(products)
        else:
            # Очищаем контейнер если товаров нет
            while self.vertical_layout.count():
                item = self.vertical_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # Показываем сообщение "Товаров нет"
            no_products_label = QLabel('Товары не найдены')
            no_products_label.setFont(QFont("Times New Roman", 12))
            no_products_label.setAlignment(Qt.AlignCenter)
            no_products_label.setStyleSheet("color: #666666; padding: 30px;")
            self.vertical_layout.addWidget(no_products_label)
    
    def show_filter_dialog(self):
        """Показывает диалоговое окно фильтра (для менеджеров и администраторов)"""
        if self.role not in ['Администратор', 'Менеджер']:
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle('Фильтр товаров')
        dialog.setFixedSize(600, 500)  # Увеличили ширину для новых фильтров
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
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title = QLabel('ФИЛЬТРАЦИЯ ТОВАРОВ')
        title.setFont(QFont("Times New Roman", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Получаем уникальных производителей из БД
        manufacturers_query = "SELECT DISTINCT manufacturer FROM products WHERE manufacturer IS NOT NULL ORDER BY manufacturer"
        manufacturers_result = self.db.execute_query(manufacturers_query)
        manufacturers = [m[0] for m in manufacturers_result] if manufacturers_result else []
        
        # Получаем уникальные категории (виды ботинок) из БД
        categories_query = "SELECT DISTINCT category FROM products WHERE category IS NOT NULL ORDER BY category"
        categories_result = self.db.execute_query(categories_query)
        categories = [c[0] for c in categories_result] if categories_result else []
        
        # Создаем скроллируемую область
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("border: none;")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        
        # Производители
        if manufacturers:
            manufacturers_group = QGroupBox('Производители')
            manufacturers_group.setFont(QFont("Times New Roman", 12, QFont.Bold))
            
            manufacturers_layout = QVBoxLayout()
            
            # Кнопка "Выбрать все"
            select_all_manuf = QPushButton('Выбрать все')
            select_all_manuf.setFixedHeight(30)
            select_all_manuf.clicked.connect(lambda: self.select_all_checkboxes(manufacturers_checkboxes, True))
            manufacturers_layout.addWidget(select_all_manuf)
            
            # Кнопка "Очистить все"
            clear_all_manuf = QPushButton('Очистить все')
            clear_all_manuf.setFixedHeight(30)
            clear_all_manuf.clicked.connect(lambda: self.select_all_checkboxes(manufacturers_checkboxes, False))
            manufacturers_layout.addWidget(clear_all_manuf)
            
            manufacturers_checkboxes = []
            for manufacturer in manufacturers:
                checkbox = QCheckBox(manufacturer)
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
                if manufacturer in self.selected_manufacturers:
                    checkbox.setChecked(True)
                manufacturers_checkboxes.append(checkbox)
                manufacturers_layout.addWidget(checkbox)
            
            manufacturers_layout.addStretch()
            manufacturers_group.setLayout(manufacturers_layout)
            scroll_layout.addWidget(manufacturers_group)
        
        # Категории (виды ботинок)
        if categories:
            categories_group = QGroupBox('Виды ботинок')
            categories_group.setFont(QFont("Times New Roman", 12, QFont.Bold))
            
            categories_layout = QVBoxLayout()
            
            # Кнопка "Выбрать все"
            select_all_cat = QPushButton('Выбрать все')
            select_all_cat.setFixedHeight(30)
            select_all_cat.clicked.connect(lambda: self.select_all_checkboxes(categories_checkboxes, True))
            categories_layout.addWidget(select_all_cat)
            
            # Кнопка "Очистить все"
            clear_all_cat = QPushButton('Очистить все')
            clear_all_cat.setFixedHeight(30)
            clear_all_cat.clicked.connect(lambda: self.select_all_checkboxes(categories_checkboxes, False))
            categories_layout.addWidget(clear_all_cat)
            
            categories_checkboxes = []
            for category in categories:
                checkbox = QCheckBox(category)
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
                if category in self.selected_categories:
                    checkbox.setChecked(True)
                categories_checkboxes.append(checkbox)
                categories_layout.addWidget(checkbox)
            
            categories_layout.addStretch()
            categories_group.setLayout(categories_layout)
            scroll_layout.addWidget(categories_group)
        
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
            dialog, manufacturers_checkboxes if manufacturers else [],
            categories_checkboxes if categories else []
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
    
    def apply_filters(self, dialog, manufacturers_checkboxes, categories_checkboxes):
        """Применяет выбранные фильтры"""
        # Сохраняем выбранных производителей
        self.selected_manufacturers = []
        for checkbox in manufacturers_checkboxes:
            if checkbox.isChecked():
                self.selected_manufacturers.append(checkbox.text())
        
        # Сохраняем выбранные категории
        self.selected_categories = []
        for checkbox in categories_checkboxes:
            if checkbox.isChecked():
                self.selected_categories.append(checkbox.text())
        
        dialog.accept()
        # Перезагружаем товары с учетом фильтров
        self.load_products(self.search_input.text() if hasattr(self, 'search_input') else "")
    
    def reset_filters(self, dialog):
        """Сбрасывает все фильтры"""
        self.selected_manufacturers = []
        self.selected_categories = []
        self.selected_supplier = "Все поставщики"
        self.quantity_sort = "none"  # Сбрасываем сортировку
        
        # Обновляем UI
        self.update_quantity_sort_button_text()
        if hasattr(self, 'supplier_combo'):
            self.supplier_combo.setCurrentText("Все поставщики")
        
        dialog.accept()
        # Перезагружаем товары без фильтров
        self.load_products(self.search_input.text() if hasattr(self, 'search_input') else "")
    
    def display_products(self, products):
        """Отображает товары в виде плиток"""
        # Очищаем текущие плитки
        while self.vertical_layout.count():
            item = self.vertical_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Заполняем плитками
        for product in products:
            product_id, name, category, price, discount, quantity, description, manufacturer, supplier, unit, photo_path = product
            
            # Преобразуем decimal.Decimal в float для вычислений
            price_float = float(price) if isinstance(price, Decimal) else float(price or 0)
            discount_int = int(discount) if discount is not None else 0
            quantity_int = int(quantity) if quantity is not None else 0
            
            # Создаем плитку товара
            product_card = self.create_product_card(
                product_id, name, category, price_float, discount_int, quantity_int,
                description, manufacturer, supplier, unit, photo_path
            )
            
            # Подключаем обработчик клика только для администраторов
            if self.role == 'Администратор':
                product_card.clicked.connect(self.on_product_clicked)
            
            # Добавляем плитку в вертикальный список
            self.vertical_layout.addWidget(product_card)
        
        # Добавляем растяжение в конце
        self.vertical_layout.addStretch()
    
    def create_product_card(self, product_id, name, category, price, discount, quantity,
                           description, manufacturer, supplier, unit, photo_path):
        """Создает плитку товара с тремя колонками"""
        # Используем кликабельный фрейм
        card = ClickableFrame(product_id)
        card.setObjectName("product_card")
        card.setMinimumHeight(400)
        card.setMaximumHeight(500)
        
        # Определяем стиль плитки в зависимости от скидки и количества
        if discount > 15:
            # Скидка > 15% - подсвечиваем плитку цветом #2E8B57
            card.setStyleSheet("""
                QFrame {
                    background-color: #2E8B57;
                    margin: 5px;
                }
                QFrame:hover {
                    background-color: #3CB371;
                }
            """)
            text_color = "#FFFFFF"  # Белый текст на зеленом фоне
            separator_color = "#FFFFFF"  # Белый для разделителей
        else:
            # Обычный стиль
            card.setStyleSheet("""
                QFrame {
                    background-color: #FFFFFF;
                    margin: 5px;
                }
                QFrame:hover {
                    background-color: #F8F8F8;
                }
            """)
            text_color = "#000000"  # Черный текст на белом фоне
            separator_color = "#000000"  # Черный для разделителей
        
        # Основной горизонтальный макет для плитки с тремя колонками
        main_card_layout = QHBoxLayout(card)
        main_card_layout.setSpacing(10)
        main_card_layout.setContentsMargins(10, 10, 10, 10)
        
        # ===== КОЛОНКА 1: ФОТО =====
        photo_column = QWidget()
        photo_column.setMinimumWidth(220)
        photo_column.setMaximumWidth(280)
        photo_layout = QVBoxLayout(photo_column)
        photo_layout.setSpacing(8)
        photo_layout.setContentsMargins(10, 10, 10, 10)
        
        # Заголовок "ФОТО"
        photo_title = QLabel('ФОТО')
        photo_title.setFont(QFont("Times New Roman", 14, QFont.Bold))
        photo_title.setAlignment(Qt.AlignCenter)
        photo_title.setStyleSheet(f"color: {text_color}; margin-bottom: 8px;")
        photo_layout.addWidget(photo_title)
        
        # Область для фото товара
        photo_frame = QFrame()
        photo_frame.setMinimumSize(180, 180)
        photo_frame.setMaximumSize(220, 220)
        
        if discount > 15:
            photo_frame.setStyleSheet("""
                QFrame {
                    background-color: #3CB371;
                }
            """)
        else:
            photo_frame.setStyleSheet("""
                QFrame {
                    background-color: #F5F5F5;
                }
            """)
        
        photo_inner_layout = QVBoxLayout(photo_frame)
        photo_inner_layout.setContentsMargins(2, 2, 2, 2)
        
        photo_label = QLabel()
        photo_label.setAlignment(Qt.AlignCenter)
        photo_label.setScaledContents(True)
        
        # Загружаем фото товара
        if photo_path and os.path.exists(photo_path):
            pixmap = QPixmap(photo_path)
            if not pixmap.isNull():
                # Масштабируем с сохранением пропорций
                pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                photo_label.setPixmap(pixmap)
                photo_label.setFixedSize(pixmap.size())
        else:
            # Если путь к фото не указан, показываем заглушку picture.png
            possible_paths = [
                "picture.png",
                "assets/picture.png",
                "images/picture.png",
                "resources/picture.png",
                os.path.join(os.path.dirname(__file__), "picture.png"),
                os.path.join(os.path.dirname(__file__), "assets", "picture.png"),
                os.path.join(os.path.dirname(__file__), "images", "picture.png")
            ]
            
            picture_found = False
            picture_path = None
            
            for path in possible_paths:
                if os.path.exists(path):
                    picture_found = True
                    picture_path = path
                    break
            
            if picture_found and picture_path:
                # Загружаем стандартную заглушку
                pixmap = QPixmap(picture_path)
                if not pixmap.isNull():
                    # Масштабируем с сохранением пропорций
                    pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    photo_label.setPixmap(pixmap)
                    photo_label.setFixedSize(pixmap.size())
                else:
                    # Если не удалось загрузить picture.png, создаем простую заглушку
                    self.create_default_photo(photo_label, quantity, discount, text_color)
            else:
                # Если picture.png не найден, создаем простую заглушку
                self.create_default_photo(photo_label, quantity, discount, text_color)
        
        photo_inner_layout.addWidget(photo_label)
        photo_layout.addWidget(photo_frame, 0, Qt.AlignCenter)
        photo_layout.addStretch()
        
        main_card_layout.addWidget(photo_column)
        
        # Разделитель между колонками 1 и 2
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.VLine)
        separator1.setFrameShadow(QFrame.Sunken)
        separator1.setStyleSheet(f"background-color: {separator_color};")
        separator1.setMaximumWidth(1)
        main_card_layout.addWidget(separator1)
        
        # ===== КОЛОНКА 2: ТЕКСТОВАЯ ИНФОРМАЦИЯ =====
        text_column = QWidget()
        text_layout = QVBoxLayout(text_column)
        text_layout.setSpacing(8)
        text_layout.setContentsMargins(15, 10, 15, 10)
        text_layout.setAlignment(Qt.AlignTop)
        
        # 1. Категория товара
        category_widget = QWidget()
        category_layout = QHBoxLayout(category_widget)
        category_layout.setSpacing(5)
        category_layout.setContentsMargins(0, 0, 0, 0)
        
        category_label = QLabel('Категория:')
        category_label.setFont(QFont("Times New Roman", 10, QFont.Bold))
        category_label.setStyleSheet(f"color: {text_color}; min-width: 100px;")
        category_label.setMinimumWidth(100)
        
        category_value = QLabel(category if category else 'Не указана')
        category_value.setFont(QFont("Times New Roman", 10))
        category_value.setStyleSheet(f"color: {text_color};")
        category_value.setWordWrap(True)
        
        category_layout.addWidget(category_label)
        category_layout.addWidget(category_value, 1)
        text_layout.addWidget(category_widget)
        
        # 2. Наименование товара
        name_widget = QWidget()
        name_layout = QHBoxLayout(name_widget)
        name_layout.setSpacing(5)
        name_layout.setContentsMargins(0, 0, 0, 0)
        
        name_label = QLabel('Наименование:')
        name_label.setFont(QFont("Times New Roman", 10, QFont.Bold))
        name_label.setStyleSheet(f"color: {text_color}; min-width: 100px;")
        name_label.setMinimumWidth(100)
        
        name_value = QLabel(name)
        name_value.setFont(QFont("Times New Roman", 10))
        name_value.setWordWrap(True)
        name_value.setStyleSheet(f"color: {text_color};")
        
        name_layout.addWidget(name_label)
        name_layout.addWidget(name_value, 1)
        text_layout.addWidget(name_widget)
        
        # 3. Описание товара
        desc_widget = QWidget()
        desc_layout = QVBoxLayout(desc_widget)
        desc_layout.setSpacing(2)
        desc_layout.setContentsMargins(0, 0, 0, 0)
        
        desc_label = QLabel('Описание:')
        desc_label.setFont(QFont("Times New Roman", 10, QFont.Bold))
        desc_label.setStyleSheet(f"color: {text_color};")
        
        desc_value = QLabel(description if description else 'Описание отсутствует')
        desc_value.setFont(QFont("Times New Roman", 9))
        desc_value.setWordWrap(True)
        desc_value.setMaximumHeight(45)
        desc_value.setStyleSheet(f"""
            QLabel {{
                padding: 4px;
                color: {text_color};
                margin-top: 3px;
                border: none;
                background-color: transparent;
            }}
        """)
        
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(desc_value)
        text_layout.addWidget(desc_widget)
        
        # 4. Производитель
        manufacturer_widget = QWidget()
        manufacturer_layout = QHBoxLayout(manufacturer_widget)
        manufacturer_layout.setSpacing(5)
        manufacturer_layout.setContentsMargins(0, 0, 0, 0)
        
        manufacturer_label = QLabel('Производитель:')
        manufacturer_label.setFont(QFont("Times New Roman", 10, QFont.Bold))
        manufacturer_label.setStyleSheet(f"color: {text_color}; min-width: 100px;")
        manufacturer_label.setMinimumWidth(100)
        
        manufacturer_value = QLabel(manufacturer if manufacturer else 'Не указан')
        manufacturer_value.setFont(QFont("Times New Roman", 10))
        manufacturer_value.setStyleSheet(f"color: {text_color};")
        manufacturer_value.setWordWrap(True)
        
        manufacturer_layout.addWidget(manufacturer_label)
        manufacturer_layout.addWidget(manufacturer_value, 1)
        text_layout.addWidget(manufacturer_widget)
        
        # 5. Поставщик
        supplier_widget = QWidget()
        supplier_layout = QHBoxLayout(supplier_widget)
        supplier_layout.setSpacing(5)
        supplier_layout.setContentsMargins(0, 0, 0, 0)
        
        supplier_label = QLabel('Поставщик:')
        supplier_label.setFont(QFont("Times New Roman", 10, QFont.Bold))
        supplier_label.setStyleSheet(f"color: {text_color}; min-width: 100px;")
        supplier_label.setMinimumWidth(100)
        
        supplier_value = QLabel(supplier if supplier else 'Не указан')
        supplier_value.setFont(QFont("Times New Roman", 10))
        supplier_value.setStyleSheet(f"color: {text_color};")
        supplier_value.setWordWrap(True)
        
        supplier_layout.addWidget(supplier_label)
        supplier_layout.addWidget(supplier_value, 1)
        text_layout.addWidget(supplier_widget)
        
        # 6. Цена
        price_widget = QWidget()
        price_layout = QHBoxLayout(price_widget)
        price_layout.setSpacing(5)
        price_layout.setContentsMargins(0, 0, 0, 0)
        
        price_label = QLabel('Цена:')
        price_label.setFont(QFont("Times New Roman", 10, QFont.Bold))
        price_label.setStyleSheet(f"color: {text_color}; min-width: 100px;")
        price_label.setMinimumWidth(100)
        
        # Контейнер для цен
        price_container = QWidget()
        price_container_layout = QVBoxLayout(price_container)
        price_container_layout.setSpacing(0)
        price_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Рассчитываем цену со скидкой
        if discount > 0:
            final_price = price * (1 - discount / 100)
            
            # Исходная цена (перечеркнутая)
            original_price_label = QLabel(f"{price:.2f} руб.")
            original_price_label.setFont(QFont("Times New Roman", 9))
            if discount > 15:
                # Белый перечеркнутый текст для зеленого фона
                original_price_label.setStyleSheet("""
                    QLabel {
                        color: #FFFFFF;
                        text-decoration: line-through;
                        font-weight: normal;
                    }
                """)
            else:
                # Красный перечеркнутый текст для белого фона
                original_price_label.setStyleSheet("""
                    QLabel {
                        color: #FF0000;
                        text-decoration: line-through;
                        font-weight: normal;
                    }
                """)
            
            # Цена со скидкой
            discounted_price_label = QLabel(f"{final_price:.2f} руб.")
            discounted_price_label.setFont(QFont("Times New Roman", 11, QFont.Bold))
            discounted_price_label.setStyleSheet(f"color: {text_color};")
            
            price_container_layout.addWidget(original_price_label)
            price_container_layout.addWidget(discounted_price_label)
        else:
            # Только одна цена (без скидки)
            price_value = QLabel(f"{price:.2f} руб.")
            price_value.setFont(QFont("Times New Roman", 11, QFont.Bold))
            price_value.setStyleSheet(f"color: {text_color};")
            price_container_layout.addWidget(price_value)
        
        price_layout.addWidget(price_label)
        price_layout.addWidget(price_container, 1)
        text_layout.addWidget(price_widget)
        
        # 7. Единица измерения
        unit_widget = QWidget()
        unit_layout = QHBoxLayout(unit_widget)
        unit_layout.setSpacing(5)
        unit_layout.setContentsMargins(0, 0, 0, 0)
        
        unit_label = QLabel('Единица:')
        unit_label.setFont(QFont("Times New Roman", 10, QFont.Bold))
        unit_label.setStyleSheet(f"color: {text_color}; min-width: 100px;")
        unit_label.setMinimumWidth(100)
        
        unit_value = QLabel(unit if unit else 'шт.')
        unit_value.setFont(QFont("Times New Roman", 10))
        unit_value.setStyleSheet(f"color: {text_color};")
        
        unit_layout.addWidget(unit_label)
        unit_layout.addWidget(unit_value, 1)
        text_layout.addWidget(unit_widget)
        
        # 8. Количество на складе
        quantity_widget = QWidget()
        quantity_layout = QHBoxLayout(quantity_widget)
        quantity_layout.setSpacing(5)
        quantity_layout.setContentsMargins(0, 0, 0, 0)
        
        quantity_label = QLabel('Количество:')
        quantity_label.setFont(QFont("Times New Roman", 10, QFont.Bold))
        quantity_label.setStyleSheet(f"color: {text_color}; min-width: 100px;")
        quantity_label.setMinimumWidth(100)
        
        quantity_value = QLabel(str(quantity))
        quantity_value.setFont(QFont("Times New Roman", 10))
        
        # Если количество = 0, подсвечиваем только поле "Количество" голубым
        if quantity == 0:
            quantity_widget.setStyleSheet("""
                QWidget {
                    background-color: #E6F3FF;
                    padding: 5px;
                    border-radius: 4px;
                }
            """)
            # Количество всегда черным
            quantity_value.setStyleSheet("""
                QLabel {
                    color: #000000;
                    font-weight: bold;
                }
            """)
        else:
            quantity_value.setStyleSheet(f"color: {text_color};")
        
        quantity_layout.addWidget(quantity_label)
        quantity_layout.addWidget(quantity_value, 1)
        text_layout.addWidget(quantity_widget)
        
        text_layout.addStretch()
        
        # Добавляем среднюю колонку с растяжением
        main_card_layout.addWidget(text_column, 2)
        
        # Разделитель между колонками 2 и 3
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.VLine)
        separator2.setFrameShadow(QFrame.Sunken)
        separator2.setStyleSheet(f"background-color: {separator_color};")
        separator2.setMaximumWidth(1)
        main_card_layout.addWidget(separator2)
        
        # ===== КОЛОНКА 3: СКИДКА =====
        discount_column = QWidget()
        discount_column.setMinimumWidth(120)
        discount_column.setMaximumWidth(150)
        discount_layout = QVBoxLayout(discount_column)
        discount_layout.setSpacing(0)
        discount_layout.setContentsMargins(10, 10, 10, 10)
        discount_layout.setAlignment(Qt.AlignCenter)
        
        # Заголовок "СКИДКА"
        discount_title = QLabel('СКИДКА')
        discount_title.setFont(QFont("Times New Roman", 14, QFont.Bold))
        discount_title.setAlignment(Qt.AlignCenter)
        discount_title.setStyleSheet(f"margin-bottom: 20px; color: {text_color};")
        
        # Значение скидки
        discount_value = QLabel(f"{discount}%")
        discount_value.setFont(QFont("Times New Roman", 24, QFont.Bold))
        discount_value.setAlignment(Qt.AlignCenter)
        discount_value.setStyleSheet(f"color: {text_color};")
        
        discount_layout.addWidget(discount_title)
        discount_layout.addWidget(discount_value)
        discount_layout.addStretch()
        
        # Добавляем правую колонку
        main_card_layout.addWidget(discount_column)
        
        return card
    
    def create_default_photo(self, photo_label, quantity, discount, text_color):
        """Создает заглушку для фото, если picture.png не найден"""
        pixmap = QPixmap(180, 180)
        if discount > 15:
            pixmap.fill(QColor(60, 179, 113))
        else:
            pixmap.fill(QColor(240, 240, 240))
        
        painter = QPainter(pixmap)
        if discount > 15:
            painter.setPen(QPen(QColor(255, 255, 255), 1))
        else:
            painter.setPen(QPen(QColor(180, 180, 180), 1))
        
        font = QFont("Times New Roman", 14, QFont.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "НЕТ ФОТО")
        painter.end()
        photo_label.setPixmap(pixmap)
        photo_label.setFixedSize(180, 180)
    
    def on_product_clicked(self, product_id):
        """Обработчик клика по плитке товара (только для администраторов)"""
        if self.role == 'Администратор':
            edit_window = ProductEditWindow(product_id, self.role)
            edit_window.product_saved.connect(self.load_products)
            edit_window.product_deleted.connect(self.handle_product_deleted)
            edit_window.exec_()
    
    def handle_product_deleted(self, product_id):
        """Обработчик удаления товара"""
        # Обновляем список товаров после удаления
        self.load_products(self.search_input.text() if hasattr(self, 'search_input') else "")
    
    def search_products(self):
        """Расширенный поиск товаров в реальном времени"""
        if hasattr(self, 'search_input'):
            search_text = self.search_input.text()
            self.load_products(search_text)
    
    def add_product(self):
        """Добавление товара (только для администраторов)"""
        if self.role == 'Администратор':
            edit_window = ProductEditWindow(None, self.role)
            edit_window.product_saved.connect(self.load_products)
            edit_window.exec_()

# Для тестирования
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductsWindow(None, 'Администратор')
    window.show()
    sys.exit(app.exec_())