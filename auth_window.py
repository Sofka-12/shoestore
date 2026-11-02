import sys
import os
import subprocess
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from database import Database

# Исправление кодировки для Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Авторизация - ООО "Обувь"')
        self.setFixedSize(500, 600)
        
        # Основной макет БЕЗ отступов
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)  # Убираем все отступы
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(20)
        
        # Логотип компании - проверяем несколько возможных путей
        print("=== Поиск логотипа ===")  # Отладочная информация
        
        # Создаем список возможных путей
        possible_paths = [
            "image/Icon.png",  # В папке image
            "Icon.png",        # В корневой папке
            "logo.png",        # Старый логотип
            "images/Icon.png", # В папке images (если есть)
            "images/logo.png", # В папке images
            "icon/Icon.png",   # В папке icon
        ]
        
        logo_path = None
        for path in possible_paths:
            if os.path.exists(path):
                logo_path = path
                print(f"Найден логотип: {os.path.abspath(path)}")
                break
            else:
                print(f"Не найден: {path}")
        
        if logo_path:
            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            
            if pixmap.isNull():
                print(f"Ошибка: не удалось загрузить изображение из {logo_path}")
                # Создаем заглушку текста
                fallback_label = QLabel('ООО "Обувь"')
                fallback_label.setFont(QFont("Times New Roman", 24, QFont.Bold))
                fallback_label.setAlignment(Qt.AlignCenter)
                fallback_label.setStyleSheet("color: #000000;")
                main_layout.addWidget(fallback_label)
            else:
                print(f"Размер изображения: {pixmap.width()}x{pixmap.height()}")
                # Масштабируем логотип
                scaled_pixmap = pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
                logo_label.setAlignment(Qt.AlignCenter)
                main_layout.addWidget(logo_label)
        else:
            print("Логотип не найден ни по одному из путей")
            # Если логотип не найден, показываем текстовый заголовок
            logo_text_label = QLabel('ООО "Обувь"')
            logo_text_label.setFont(QFont("Times New Roman", 24, QFont.Bold))
            logo_text_label.setAlignment(Qt.AlignCenter)
            logo_text_label.setStyleSheet("color: #000000; padding: 20px;")
            main_layout.addWidget(logo_text_label)
        
        # Заголовок
        title_label = QLabel('ООО "Обувь"')
        title_font = QFont("Times New Roman", 20, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("title")
        main_layout.addWidget(title_label)
        
        subtitle_label = QLabel('Авторизация в системе')
        subtitle_font = QFont("Times New Roman", 14)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle_label)
        
        # Контейнер для формы - ЦЕНТРИРУЕМ ВСЁ
        form_container = QWidget()
        form_container.setFixedWidth(400)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(15)
        form_layout.setAlignment(Qt.AlignCenter)  # Центрируем содержимое
        
        # Email поле
        email_container = QWidget()
        email_layout = QVBoxLayout(email_container)
        email_layout.setSpacing(5)
        email_layout.setAlignment(Qt.AlignCenter)
        
        email_label = QLabel('Логин:')
        email_label.setFont(QFont("Times New Roman", 12, QFont.Bold))
        email_label.setAlignment(Qt.AlignCenter)  # Центрируем текст
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('Введите Логин')
        self.email_input.setFixedHeight(40)
        self.email_input.setAlignment(Qt.AlignCenter)  # Центрируем текст в поле
        
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)
        
        # Пароль поле
        password_container = QWidget()
        password_layout = QVBoxLayout(password_container)
        password_layout.setSpacing(5)
        password_layout.setAlignment(Qt.AlignCenter)
        
        password_label = QLabel('Пароль:')
        password_label.setFont(QFont("Times New Roman", 12, QFont.Bold))
        password_label.setAlignment(Qt.AlignCenter)  # Центрируем текст
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Введите пароль')
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(40)
        self.password_input.setAlignment(Qt.AlignCenter)  # Центрируем текст в поле
        
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        
        # Добавляем поля в форму
        form_layout.addWidget(email_container)
        form_layout.addWidget(password_container)
        
        main_layout.addWidget(form_container, 0, Qt.AlignCenter)
        
        # Кнопки - вертикальное расположение
        button_container = QWidget()
        button_container.setFixedWidth(400)
        button_layout = QVBoxLayout(button_container)
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignCenter)
        
        # Кнопка Войти
        self.login_button = QPushButton('Войти')
        self.login_button.setFixedHeight(50)
        self.login_button.setFixedWidth(200)  # Фиксированная ширина
        self.login_button.clicked.connect(self.login)
        
        # Кнопка Войти как гость (шире)
        self.guest_button = QPushButton('Войти как гость')
        self.guest_button.setFixedHeight(50)
        self.guest_button.setFixedWidth(250)  # Шире для текста
        self.guest_button.clicked.connect(self.login_as_guest)
        
        # Добавляем кнопки в вертикальный layout
        button_layout.addWidget(self.login_button, 0, Qt.AlignCenter)
        button_layout.addWidget(self.guest_button, 0, Qt.AlignCenter)
        
        main_layout.addWidget(button_container, 0, Qt.AlignCenter)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        
        # Кнопка тестирования UI - создаем ПОСЛЕ установки основного layout (правая верхняя)
        self.test_ui_button = QPushButton('🔍 Тестирование', self)
        self.test_ui_button.setFixedSize(120, 30)
        self.test_ui_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border-radius: 3px;
                font-size: 10px;
                border: 1px solid #388E3C;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
        self.test_ui_button.clicked.connect(self.run_ui_tests)
        # Позиционируем в правом верхнем углу ПОВЕРХ всего
        self.test_ui_button.raise_()  # Поднимаем на передний план
        self.test_ui_button.move(365, 5)  # 500-120-15=365, отступ 5px сверху
        
       
    
    def login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        
        if not email or not password:
            QMessageBox.warning(self, 'Ошибка', 'Заполните все поля')
            return
        
        # Проверка пользователя в базе данных
        query = """
            SELECT user_id, full_name, role 
            FROM users 
            WHERE email = %s AND password_hash = %s AND is_active = true
        """
        result = self.db.execute_query(query, (email, password))
        
        if result:
            user_id, full_name, role = result[0]
            QMessageBox.information(self, 'Успешно', f'Добро пожаловать, {full_name}!')
            self.open_main_window(user_id, full_name, role)
        else:
            QMessageBox.critical(self, 'Ошибка', 'Неверный email или пароль')
    
    def login_as_guest(self):
        guest_name = 'Гость'
        guest_role = 'Гость'
        self.open_main_window(None, guest_name, guest_role)
    
    def open_main_window(self, user_id, full_name, role):
        from main_window import MainWindow
        self.main_window = MainWindow(user_id, full_name, role)
        self.main_window.show()
        self.close()
    
    def run_ui_tests(self):
        """Запуск автоматических тестов интерфейса в терминале"""
        try:
            # Меняем текст кнопки на время выполнения
            original_text = self.test_ui_button.text()
            self.test_ui_button.setText("🔄 Тесты...")
            self.test_ui_button.setEnabled(False)
            
            # Показываем сообщение о запуске
            QMessageBox.information(
                self, 
                'Запуск тестирования UI', 
                'Тестирование пользовательского интерфейса запущено!\n\n'
                'Откроется новое окно терминала с результатами.\n'
                'После завершения тестов закройте окно терминала.'
            )
            
            # Проверяем существование файла тестов
            test_file = "test_ui.py"
            if not os.path.exists(test_file):
                # Пробуем найти файл с другим именем
                alternative_files = ["test_auth.py", "test.py", "tests.py"]
                for alt_file in alternative_files:
                    if os.path.exists(alt_file):
                        test_file = alt_file
                        break
                else:
                    # Файл не найден
                    QMessageBox.critical(
                        self, 
                        'Файл не найден', 
                        f'Файл тестов не найден. Искали:\n'
                        f'- test_ui.py\n'
                        f'- test_auth.py\n'
                        f'- test.py\n'
                        f'- tests.py'
                    )
                    self.test_ui_button.setText(original_text)
                    self.test_ui_button.setEnabled(True)
                    return
            
            # Запускаем тесты в новом окне терминала
            if sys.platform == "win32":
                # Для Windows
                subprocess.Popen(
                    ['cmd', '/k', sys.executable, test_file],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                # Для Linux/Mac
                subprocess.Popen(['x-terminal-emulator', '-e', sys.executable, test_file])
            
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось запустить тесты: {str(e)}')
        finally:
            # Восстанавливаем кнопку
            self.test_ui_button.setText(original_text)
            self.test_ui_button.setEnabled(True)
    
    def run_alinko_tests(self):
        """Запуск тестов из файла test_Alinko.py"""
        try:
            # Меняем текст кнопки на время выполнения
            original_text = self.test_alinko_button.text()
            self.test_alinko_button.setText("🔄 Запуск...")
            self.test_alinko_button.setEnabled(False)
            
            # Проверяем существование файла test_Alinko.py
            test_file = "test_Alinko.py"
            
            if not os.path.exists(test_file):
                # Ищем файл в других местах
                possible_paths = [
                    "test_Alinko.py",
                    "test_Alinko.txt",
                    os.path.join(os.path.dirname(__file__), "test_Alinko.py"),
                    "test.py",
                    "test_script.py"
                ]
                
                test_file = None
                for path in possible_paths:
                    if os.path.exists(path):
                        test_file = path
                        break
                
                if not test_file:
                    # Файл не найден нигде
                    QMessageBox.critical(
                        self, 
                        'Файл не найден', 
                        'Файл test_Alinko.py не найден.\n\n'
                        'Проверьте, что файл находится в той же папке, что и приложение.'
                    )
                    self.test_alinko_button.setText(original_text)
                    self.test_alinko_button.setEnabled(True)
                    return
            
            # Показываем информацию о запуске
            QMessageBox.information(
                self, 
                'Запуск тестов Alinko', 
                f'Запускаются тесты из файла:\n{test_file}\n\n'
                'Откроется новое окно терминала.\n'
                'После завершения тестов закройте окно терминала.'
            )
            
            # Запускаем тесты в новом окне терминала
            if sys.platform == "win32":
                # Для Windows - открываем в новом окне командной строки
                subprocess.Popen(
                    ['cmd', '/k', sys.executable, test_file],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            elif sys.platform == "darwin":  # macOS
                # Для Mac
                subprocess.Popen(['open', '-a', 'Terminal', test_file])
            else:  # Linux
                # Для Linux
                subprocess.Popen(['x-terminal-emulator', '-e', sys.executable, test_file])
            
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось запустить тесты Alinko: {str(e)}')
        finally:
            # Восстанавливаем кнопку
            self.test_alinko_button.setText(original_text)
            self.test_alinko_button.setEnabled(True)

# Для тестирования
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AuthWindow()
    window.show()
    sys.exit(app.exec_())