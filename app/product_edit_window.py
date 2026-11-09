import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QFont, QIcon
from database import Database
from PIL import Image

# Исправление кодировки для Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

class ProductEditWindow(QDialog):
    product_saved = pyqtSignal()
    product_deleted = pyqtSignal(int)  # Новый сигнал для удаления товара
    
    def __init__(self, product_id, role):
        super().__init__()
        self.product_id = product_id
        self.role = role
        self.db = Database()
        self.image_path = None
        self.temp_image_path = None
        self.setModal(True)
        self.init_ui()
        self.load_product_data()
    
    def init_ui(self):
        self.setWindowTitle('Добавить товар' if not self.product_id else 'Редактировать товар')
        self.setFixedSize(900, 900)  # Увеличил высоту для кнопки удаления
        
        # Устанавливаем иконку
        if os.path.exists("Icon.ico"):
            self.setWindowIcon(QIcon("Icon.ico"))
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок окна
        title_label = QLabel('Добавить товар' if not self.product_id else 'Редактировать товар')
        title_label.setFont(QFont("Times New Roman", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("title")
        main_layout.addWidget(title_label)
        
        # Горизонтальный контейнер для фото и информации
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Левая часть - фото
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)
        
        # Контейнер для фото с рамкой
        photo_frame = QFrame()
        photo_frame.setObjectName("image_container")
        photo_frame.setFixedSize(300, 250)
        
        photo_layout = QVBoxLayout(photo_frame)
        photo_layout.setContentsMargins(10, 10, 10, 10)
        
        self.image_label = QLabel()
        self.image_label.setFixedSize(280, 230)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(True)
        
        # Кнопка загрузки фото
        self.image_button = QPushButton('Загрузить изображение')
        self.image_button.setFixedWidth(250)
        self.image_button.clicked.connect(self.load_image)
        
        photo_layout.addWidget(self.image_label)
        left_layout.addWidget(photo_frame, 0, Qt.AlignCenter)
        left_layout.addWidget(self.image_button, 0, Qt.AlignCenter)
        
        # Правая часть - форма
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)
        
        # Создаем форму по макету
        form_container = QWidget()
        form_layout = QFormLayout(form_container)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(20)
        
        # Стиль для заголовков полей
        label_style = "font-weight: bold; font-size: 11pt; min-width: 150px;"
        
        # Строка 1: Категория товара | Наименование товара
        row1_widget = QWidget()
        row1_layout = QHBoxLayout(row1_widget)
        row1_layout.setSpacing(10)
        
        # Категория товара
        category_container = QWidget()
        category_vertical = QVBoxLayout(category_container)
        category_vertical.setSpacing(5)
        
        category_label = QLabel('Категория товара:')
        category_label.setStyleSheet(label_style)
        
        self.category_combo = QComboBox()
        self.category_combo.setFixedWidth(150)
        self.load_categories()
        
        category_vertical.addWidget(category_label)
        category_vertical.addWidget(self.category_combo)
        
        # Разделитель
        separator = QLabel('|')
        separator.setFont(QFont("Times New Roman", 14, QFont.Bold))
        separator.setFixedWidth(20)
        
        # Наименование товара
        name_container = QWidget()
        name_vertical = QVBoxLayout(name_container)
        name_vertical.setSpacing(5)
        
        name_label = QLabel('Наименование товара:')
        name_label.setStyleSheet(label_style)
        
        self.name_input = QLineEdit()
        self.name_input.setFixedWidth(200)
        
        name_vertical.addWidget(name_label)
        name_vertical.addWidget(self.name_input)
        
        row1_layout.addWidget(category_container)
        row1_layout.addWidget(separator)
        row1_layout.addWidget(name_container)
        row1_layout.addStretch()
        
        form_layout.addRow(row1_widget)
        
        # Строка 2: Описание товара
        desc_label = QLabel('Описание товара:')
        desc_label.setStyleSheet(label_style)
        
        self.description_input = QTextEdit()
        self.description_input.setFixedHeight(100)
        
        form_layout.addRow(desc_label, self.description_input)
        
        # Строка 3: Производитель
        manufacturer_label = QLabel('Производитель:')
        manufacturer_label.setStyleSheet(label_style)
        
        self.manufacturer_combo = QComboBox()
        self.load_manufacturers()
        
        form_layout.addRow(manufacturer_label, self.manufacturer_combo)
        
        # Строка 4: Поставщик
        supplier_label = QLabel('Поставщик:')
        supplier_label.setStyleSheet(label_style)
        
        self.supplier_input = QLineEdit()
        
        form_layout.addRow(supplier_label, self.supplier_input)
        
        # Строка 5: Цена
        price_label = QLabel('Цена:')
        price_label.setStyleSheet(label_style)
        
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("0.00")
        
        form_layout.addRow(price_label, self.price_input)
        
        # Строка 6: Единица измерения
        unit_label = QLabel('Единица измерения:')
        unit_label.setStyleSheet(label_style)
        
        self.unit_input = QLineEdit('шт.')
        
        form_layout.addRow(unit_label, self.unit_input)
        
        # Строка 7: Количество на складе
        quantity_label = QLabel('Количество на складе:')
        quantity_label.setStyleSheet(label_style)
        
        self.quantity_input = QLineEdit('0')
        
        form_layout.addRow(quantity_label, self.quantity_input)
        
        # Строка 8: Действующая скидка
        discount_label = QLabel('Действующая скидка (%):')
        discount_label.setStyleSheet(label_style)
        
        self.discount_input = QLineEdit('0')
        self.discount_input.setPlaceholderText("0-100")
        
        form_layout.addRow(discount_label, self.discount_input)
        
        # Строка 9: Артикул
        article_label = QLabel('Артикул:')
        article_label.setStyleSheet(label_style)
        
        self.article_input = QLineEdit()
        
        form_layout.addRow(article_label, self.article_input)
        
        right_layout.addWidget(form_container)
        right_layout.addStretch()
        
        # Добавляем обе части в основной контейнер
        content_layout.addWidget(left_widget)
        content_layout.addWidget(right_widget)
        
        main_layout.addLayout(content_layout)
        
        # Кнопки Сохранить, Удалить и Отмена
        button_layout = QHBoxLayout()
        button_layout.setSpacing(30)
        
        self.save_button = QPushButton('Сохранить')
        self.save_button.setFixedSize(150, 45)
        self.save_button.clicked.connect(self.save_product)
        
        # Кнопка удаления (только для редактирования существующего товара)
        if self.product_id:
            self.delete_button = QPushButton('Удалить товар')
            self.delete_button.setFixedSize(150, 45)
            self.delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #00FA9A;
                    color: #000000;
                    border: 1px solid #000000;
                    font-size: 10pt;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #00E68A;
                }
                QPushButton:pressed {
                    background-color: #00D47A;
                }
            """)
            self.delete_button.clicked.connect(self.delete_product)
        
        self.cancel_button = QPushButton('Отмена')
        self.cancel_button.setFixedSize(150, 45)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        
        if self.product_id:
            button_layout.addWidget(self.delete_button)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # Загружаем изображение по умолчанию
        self.load_default_image()
    
    def load_default_image(self):
        """Загружает заглушку или существующее изображение"""
        # Если редактируем товар, пробуем загрузить его фото
        if self.product_id:
            product_photo = self.find_product_photo(self.product_id)
            if product_photo:
                self.load_image_from_path(product_photo)
                return
        
        # Иначе используем picture.png или создаем заглушку
        if os.path.exists("picture.png"):
            pixmap = QPixmap("picture.png")
            pixmap = pixmap.scaled(280, 230, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
        else:
            # Создаем красивую заглушку
            pixmap = QPixmap(280, 230)
            pixmap.fill(QColor(245, 245, 245))
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Рисуем рамку
            painter.setPen(QPen(QColor(200, 200, 200), 2))
            painter.drawRect(5, 5, 270, 220)
            
            # Рисуем иконку фото
            painter.setPen(QPen(QColor(150, 150, 150), 1))
            painter.drawEllipse(140, 80, 40, 40)
            painter.drawLine(140, 100, 120, 120)
            painter.drawLine(180, 100, 200, 120)
            
            # Текст
            painter.setPen(QPen(QColor(100, 100, 100), 2))
            font = painter.font()
            font.setPointSize(12)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignBottom | Qt.AlignHCenter, "ФОТО ТОВАРА")
            
            painter.end()
            self.image_label.setPixmap(pixmap)
    
    def find_product_photo(self, product_id):
        """Находит фото товара по ID"""
        # Проверяем в папке images
        possible_paths = [
            f"images/{product_id}.jpg",
            f"images/{product_id}.png",
            f"{product_id}.jpg",
            f"{product_id}.png",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def load_categories(self):
        query = "SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category != '' ORDER BY category"
        result = self.db.execute_query(query)
        if result:
            for row in result:
                self.category_combo.addItem(row[0])
        self.category_combo.addItem('Другое')
    
    def load_manufacturers(self):
        query = "SELECT DISTINCT manufacturer FROM products WHERE manufacturer IS NOT NULL AND manufacturer != '' ORDER BY manufacturer"
        result = self.db.execute_query(query)
        if result:
            for row in result:
                self.manufacturer_combo.addItem(row[0])
        self.manufacturer_combo.addItem('Другое')
    
    def load_product_data(self):
        if self.product_id:
            query = """
                SELECT article, name, category, manufacturer, supplier, price, 
                       discount, quantity, unit, description
                FROM products 
                WHERE product_id = %s
            """
            result = self.db.execute_query(query, (self.product_id,))
            
            if result:
                article, name, category, manufacturer, supplier, price, \
                discount, quantity, unit, description = result[0]
                
                self.article_input.setText(article if article else '')
                self.name_input.setText(name if name else '')
                
                if category:
                    index = self.category_combo.findText(category)
                    if index >= 0:
                        self.category_combo.setCurrentIndex(index)
                    else:
                        self.category_combo.setCurrentText(category)
                
                if manufacturer:
                    index = self.manufacturer_combo.findText(manufacturer)
                    if index >= 0:
                        self.manufacturer_combo.setCurrentIndex(index)
                    else:
                        self.manufacturer_combo.setCurrentText(manufacturer)
                
                self.supplier_input.setText(supplier if supplier else '')
                self.price_input.setText(str(price) if price else '0.00')
                self.discount_input.setText(str(discount) if discount else '0')
                self.quantity_input.setText(str(quantity) if quantity else '0')
                self.unit_input.setText(unit if unit else 'шт.')
                self.description_input.setText(description if description else '')
                
                # Загружаем фото товара
                self.load_product_photo()
    
    def load_product_photo(self):
        """Загружает фото товара"""
        if not self.product_id:
            return
            
        # Ищем фото в разных местах
        photo_paths = [
            f"images/{self.product_id}.jpg",
            f"images/{self.product_id}.png",
            f"{self.product_id}.jpg",
            f"{self.product_id}.png",
        ]
        
        for path in photo_paths:
            if os.path.exists(path):
                self.load_image_from_path(path)
                break
    
    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Выберите изображение', '', 
            'Images (*.png *.jpg *.jpeg *.bmp *.gif)'
        )
        
        if file_path:
            self.load_image_from_path(file_path)
            self.temp_image_path = file_path
    
    def load_image_from_path(self, path):
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            # Сохраняем пропорции
            scaled_pixmap = pixmap.scaled(280, 230, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
            self.image_path = path
    
    def delete_product(self):
        """Удаляет текущий товар"""
        if not self.product_id:
            return
            
        reply = QMessageBox.question(
            self, 'Подтверждение удаления',
            'Вы уверены, что хотите удалить этот товар?\nЭто действие нельзя отменить.',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Получаем информацию о товаре перед удалением
            query_info = "SELECT name FROM products WHERE product_id = %s"
            product_info = self.db.execute_query(query_info, (self.product_id,))
            
            # Удаляем фото товара если оно существует
            query_photo = "SELECT photo_path FROM products WHERE product_id = %s"
            photo_result = self.db.execute_query(query_photo, (self.product_id,))
            
            if photo_result and photo_result[0][0] and os.path.exists(photo_result[0][0]):
                try:
                    os.remove(photo_result[0][0])
                except:
                    pass
            
            # Удаляем товар из базы данных
            query = "DELETE FROM products WHERE product_id = %s"
            result = self.db.execute_query(query, (self.product_id,))
            
            if result is not None:
                product_name = product_info[0][0] if product_info and product_info[0][0] else "Товар"
                QMessageBox.information(self, 'Успех', f'Товар "{product_name}" удален!')
                # Отправляем сигнал с ID удаленного товара
                self.product_deleted.emit(self.product_id)
                self.accept()
            else:
                QMessageBox.critical(self, 'Ошибка', 'Не удалось удалить товар')
    
    def save_product(self):
        # Валидация обязательных полей
        if not self.name_input.text().strip():
            QMessageBox.critical(self, 'Ошибка', 'Введите наименование товара')
            self.name_input.setFocus()
            return
            
        if not self.article_input.text().strip():
            QMessageBox.critical(self, 'Ошибка', 'Введите артикул товара')
            self.article_input.setFocus()
            return
        
        # Валидация числовых полей
        try:
            price_text = self.price_input.text().replace(',', '.')
            price = float(price_text) if price_text else 0.0
            if price < 0:
                raise ValueError
        except ValueError:
            QMessageBox.critical(self, 'Ошибка', 'Введите корректную цену (положительное число)')
            self.price_input.setFocus()
            return
        
        try:
            discount_text = self.discount_input.text()
            discount = int(discount_text) if discount_text else 0
            if discount < 0 or discount > 100:
                raise ValueError
        except ValueError:
            QMessageBox.critical(self, 'Ошибка', 'Скидка должна быть от 0 до 100%')
            self.discount_input.setFocus()
            return
        
        try:
            quantity_text = self.quantity_input.text()
            quantity = int(quantity_text) if quantity_text else 0
            if quantity < 0:
                raise ValueError
        except ValueError:
            QMessageBox.critical(self, 'Ошибка', 'Количество должно быть положительным числом')
            self.quantity_input.setFocus()
            return
        
        # Обработка изображения
        photo_filename = None
        if self.temp_image_path:
            if not os.path.exists('images'):
                os.makedirs('images')
            
            if self.product_id:
                photo_filename = f"{self.product_id}.jpg"
            else:
                # Получаем следующий ID для нового товара
                query = "SELECT MAX(product_id) FROM products"
                result = self.db.execute_query(query)
                next_id = (result[0][0] or 0) + 1
                photo_filename = f"{next_id}.jpg"
            
            save_path = os.path.join('images', photo_filename)
            
            try:
                img = Image.open(self.temp_image_path)
                img = img.resize((300, 250), Image.Resampling.LANCZOS)
                
                # Конвертируем RGBA в RGB если нужно
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                
                img.save(save_path, 'JPEG', quality=90)
                photo_path = save_path
                
                # Удаляем старое фото если оно существует и отличается от нового
                if self.product_id:
                    old_query = "SELECT photo_path FROM products WHERE product_id = %s"
                    old_result = self.db.execute_query(old_query, (self.product_id,))
                    if old_result and old_result[0][0]:
                        old_path = old_result[0][0]
                        if os.path.exists(old_path) and os.path.abspath(old_path) != os.path.abspath(save_path):
                            try:
                                os.remove(old_path)
                            except:
                                pass
            except Exception as e:
                print(f"Ошибка сохранения изображения: {e}")
                photo_path = None
        else:
            photo_path = None
        
        # Подготавливаем данные
        article = self.article_input.text().strip()
        name = self.name_input.text().strip()
        category = self.category_combo.currentText()
        manufacturer = self.manufacturer_combo.currentText()
        supplier = self.supplier_input.text().strip()
        unit = self.unit_input.text().strip() if self.unit_input.text().strip() else 'шт.'
        description = self.description_input.toPlainText().strip()
        
        if self.product_id:
            # Обновление существующего товара
            query = """
                UPDATE products SET 
                article = %s, name = %s, category = %s, manufacturer = %s,
                supplier = %s, price = %s, discount = %s, quantity = %s,
                unit = %s, description = %s, photo_path = %s, updated_at = NOW()
                WHERE product_id = %s
            """
            params = (
                article, name, category, manufacturer,
                supplier, price, discount, quantity,
                unit, description, photo_path,
                self.product_id
            )
        else:
            # Добавление нового товара
            query = """
                INSERT INTO products 
                (article, name, category, manufacturer, supplier, price, discount,
                 quantity, unit, description, photo_path, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                RETURNING product_id
            """
            params = (
                article, name, category, manufacturer,
                supplier, price, discount, quantity,
                unit, description, photo_path
            )
        
        # Выполняем запрос
        result = self.db.execute_query(query, params)
        if result is not None:
            QMessageBox.information(self, 'Успех', 'Товар успешно сохранен!')
            self.product_saved.emit()
            self.accept()
        else:
            QMessageBox.critical(self, 'Ошибка', 'Не удалось сохранить товар. Проверьте данные.')

# Для тестирования
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductEditWindow(None, "Администратор")
    window.show()
    sys.exit(app.exec_())
