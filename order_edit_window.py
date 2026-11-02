import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QIcon
from database import Database
from datetime import datetime

# Исправление кодировки для Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

class OrderEditWindow(QDialog):
    order_saved = pyqtSignal()
    order_deleted = pyqtSignal(int)
    
    def __init__(self, order_id, role):
        super().__init__()
        self.order_id = order_id
        self.role = role
        self.db = Database()
        self.setModal(True)
        self.init_ui()
        self.load_order_data()
    
    def init_ui(self):
        self.setWindowTitle('Добавить заказ' if not self.order_id else 'Редактировать заказ')
        self.setFixedSize(500, 580)
        
        if os.path.exists("Icon.ico"):
            self.setWindowIcon(QIcon("Icon.ico"))
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel('Добавить заказ' if not self.order_id else 'Редактировать заказ')
        title.setFont(QFont("Times New Roman", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setSpacing(10)
        
        order_number_label = QLabel('Номер заказа:')
        order_number_label.setFont(QFont("Times New Roman", 11, QFont.Bold))
        
        self.order_number_input = QLineEdit()
        self.order_number_input.setPlaceholderText('ORD-011')
        
        form_layout.addRow(order_number_label, self.order_number_input)
        
        customer_label = QLabel('Клиент:')
        customer_label.setFont(QFont("Times New Roman", 11, QFont.Bold))
        
        self.customer_combo = QComboBox()
        self.load_customers()
        
        form_layout.addRow(customer_label, self.customer_combo)
        
        status_label = QLabel('Статус:')
        status_label.setFont(QFont("Times New Roman", 11, QFont.Bold))
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(['Новый', 'В обработке', 'Ожидает оплаты', 'Оплачен', 'Отправлен', 'Доставлен', 'Отменен'])
        
        form_layout.addRow(status_label, self.status_combo)
        
        delivery_label = QLabel('Пункт выдачи:')
        delivery_label.setFont(QFont("Times New Roman", 11, QFont.Bold))
        
        self.delivery_combo = QComboBox()
        self.load_delivery_points()
        
        form_layout.addRow(delivery_label, self.delivery_combo)
        
        order_date_label = QLabel('Дата заказа:')
        order_date_label.setFont(QFont("Times New Roman", 11, QFont.Bold))
        
        self.order_date_input = QDateEdit()
        self.order_date_input.setCalendarPopup(True)
        self.order_date_input.setDate(QDate.currentDate())
        self.order_date_input.setDisplayFormat("dd.MM.yyyy")
        self.order_date_input.setMinimumDate(QDate(2020, 1, 1))
        
        form_layout.addRow(order_date_label, self.order_date_input)
        
        delivery_date_label = QLabel('Дата доставки:')
        delivery_date_label.setFont(QFont("Times New Roman", 11, QFont.Bold))
        
        self.delivery_date_input = QDateEdit()
        self.delivery_date_input.setCalendarPopup(True)
        self.delivery_date_input.setDate(QDate.currentDate().addDays(7))
        self.delivery_date_input.setDisplayFormat("dd.MM.yyyy")
        self.delivery_date_input.setMinimumDate(QDate(2020, 1, 1))
        
        form_layout.addRow(delivery_date_label, self.delivery_date_input)
        
        pickup_label = QLabel('Код получения:')
        pickup_label.setFont(QFont("Times New Roman", 11, QFont.Bold))
        
        self.pickup_input = QLineEdit()
        self.pickup_input.setPlaceholderText('ABC123')
        
        form_layout.addRow(pickup_label, self.pickup_input)
        
        total_label = QLabel('Сумма заказа:')
        total_label.setFont(QFont("Times New Roman", 11, QFont.Bold))
        
        self.total_input = QLineEdit('0')
        
        form_layout.addRow(total_label, self.total_input)
        
        main_layout.addLayout(form_layout)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        if self.order_id:
            self.delete_button = QPushButton('Удалить заказ')
            self.delete_button.setFixedSize(140, 40)
            self.delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #00FA9A;
                    color: 000000;
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
            self.delete_button.clicked.connect(self.delete_order)
            button_layout.addWidget(self.delete_button)
        
        button_layout.addStretch()
        
        self.save_button = QPushButton('Сохранить')
        self.save_button.setFixedSize(120, 40)
        self.save_button.clicked.connect(self.save_order)
        
        self.cancel_button = QPushButton('Отмена')
        self.cancel_button.setFixedSize(120, 40)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def load_customers(self):
        query = """
            SELECT user_id, full_name, email 
            FROM users 
            WHERE role IN ('Авторизированный клиент', 'Менеджер', 'Администратор')
            ORDER BY full_name
        """
        result = self.db.execute_query(query)
        
        self.customer_combo.clear()
        self.customer_combo.addItem('Выберите клиента', None)
        
        if result:
            for row in result:
                user_id, full_name, email = row
                display_text = f"{full_name} ({email})"
                self.customer_combo.addItem(display_text, user_id)
    
    def load_delivery_points(self):
        query = "SELECT point_id, address FROM delivery_points WHERE is_active = true ORDER BY address"
        result = self.db.execute_query(query)
        
        self.delivery_combo.clear()
        self.delivery_combo.addItem('Выберите пункт выдачи', None)
        
        if result:
            for row in result:
                point_id, address = row
                self.delivery_combo.addItem(address, point_id)
    
    def load_order_data(self):
        if self.order_id:
            query = """
                SELECT order_number, user_id, status, delivery_point_id,
                       total_amount, order_date, delivery_date, pickup_code
                FROM orders 
                WHERE order_id = %s
            """
            result = self.db.execute_query(query, (self.order_id,))
            
            if result:
                (order_number, user_id, status, delivery_point_id,
                 total_amount, order_date, delivery_date, pickup_code) = result[0]
                
                self.order_number_input.setText(order_number or '')
                
                if user_id:
                    index = self.customer_combo.findData(user_id)
                    if index >= 0:
                        self.customer_combo.setCurrentIndex(index)
                
                if status:
                    index = self.status_combo.findText(status)
                    if index >= 0:
                        self.status_combo.setCurrentIndex(index)
                
                if delivery_point_id:
                    index = self.delivery_combo.findData(delivery_point_id)
                    if index >= 0:
                        self.delivery_combo.setCurrentIndex(index)
                
                self.total_input.setText(str(total_amount) if total_amount else '0')
                
                if order_date:
                    try:
                        if isinstance(order_date, str):
                            date_obj = datetime.strptime(str(order_date), "%Y-%m-%d %H:%M:%S")
                        else:
                            date_obj = order_date
                        self.order_date_input.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))
                    except:
                        self.order_date_input.setDate(QDate.currentDate())
                
                if delivery_date:
                    try:
                        if isinstance(delivery_date, str):
                            date_obj = datetime.strptime(str(delivery_date), "%Y-%m-%d")
                        else:
                            date_obj = delivery_date
                        self.delivery_date_input.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))
                    except:
                        self.delivery_date_input.setDate(QDate.currentDate().addDays(7))
                
                self.pickup_input.setText(pickup_code or '')
    
    def save_order(self):
        if not self.order_number_input.text().strip():
            QMessageBox.critical(self, 'Ошибка', 'Введите номер заказа')
            self.order_number_input.setFocus()
            return
        
        try:
            total_amount = float(self.total_input.text().replace(',', '.'))
            if total_amount < 0:
                raise ValueError
        except ValueError:
            QMessageBox.critical(self, 'Ошибка', 'Введите корректную сумму заказа (положительное число)')
            self.total_input.setFocus()
            return
        
        order_number = self.order_number_input.text().strip()
        user_id = self.customer_combo.currentData()
        status = self.status_combo.currentText()
        delivery_point_id = self.delivery_combo.currentData()
        
        order_date_qdate = self.order_date_input.date()
        if not order_date_qdate.isValid():
            order_date_qdate = QDate.currentDate()
        order_date = order_date_qdate.toString("yyyy-MM-dd 00:00:00")
        
        delivery_date_qdate = self.delivery_date_input.date()
        if not delivery_date_qdate.isValid():
            delivery_date_qdate = QDate.currentDate().addDays(7)
        delivery_date = delivery_date_qdate.toString("yyyy-MM-dd 00:00:00")
        
        pickup_code = self.pickup_input.text().strip() or None
        
        if self.order_id:
            query = """
                UPDATE orders SET 
                order_number = %s, user_id = %s, status = %s,
                delivery_point_id = %s, total_amount = %s,
                order_date = %s::timestamp, delivery_date = %s::timestamp, 
                pickup_code = %s, updated_at = NOW()
                WHERE order_id = %s
            """
            params = (
                order_number, user_id, status, delivery_point_id,
                total_amount, order_date, delivery_date, pickup_code,
                self.order_id
            )
        else:
            query = """
                INSERT INTO orders 
                (order_number, user_id, status, delivery_point_id,
                 total_amount, order_date, delivery_date, pickup_code,
                 created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s::timestamp, %s::timestamp, %s, NOW(), NOW())
                RETURNING order_id
            """
            params = (
                order_number, user_id, status, delivery_point_id,
                total_amount, order_date, delivery_date, pickup_code
            )
        
        try:
            result = self.db.execute_query(query, params)
            if result is not None:
                QMessageBox.information(self, 'Успех', 'Заказ сохранен!')
                self.order_saved.emit()
                self.accept()
            else:
                QMessageBox.critical(self, 'Ошибка', 'Не удалось сохранить заказ')
        except Exception as e:
            print(f"Ошибка при сохранении заказа: {e}")
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при сохранении: {str(e)}')
    
    def delete_order(self):
        if not self.order_id:
            return
        
        reply = QMessageBox.question(
            self, 
            'Подтверждение удаления',
            f'Вы уверены, что хотите удалить заказ "{self.order_number_input.text()}"?\n\nЭто действие нельзя отменить!',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Получаем информацию о заказе перед удалением
                query_info = """
                    SELECT order_number FROM orders WHERE order_id = %s
                """
                order_info = self.db.execute_query(query_info, (self.order_id,))
                
                # Сначала удаляем связанные записи
                delete_items_query = "DELETE FROM order_items WHERE order_id = %s"
                self.db.execute_query(delete_items_query, (self.order_id,))
                
                # Удаляем сам заказ
                query = "DELETE FROM orders WHERE order_id = %s"
                result = self.db.execute_query(query, (self.order_id,))
                
                if result is not None:
                    order_number = order_info[0][0] if order_info and order_info[0][0] else "Заказ"
                    QMessageBox.information(self, 'Успех', f'Заказ "{order_number}" удален!')
                    self.order_deleted.emit(self.order_id)
                    self.accept()
                else:
                    QMessageBox.critical(self, 'Ошибка', 'Не удалось удалить заказ')
            
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Ошибка при удалении: {str(e)}')

# Для тестирования
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OrderEditWindow(None, "Администратор")
    window.show()
    sys.exit(app.exec_())