import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QFile, QTextStream

# Исправление кодировки для Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def load_styles(app):
    """Загружает CSS стили из файла"""
    style_file = QFile("style.css")
    
    if style_file.exists():
        style_file.open(QFile.ReadOnly | QFile.Text)
        style_stream = QTextStream(style_file)
        style_stream.setCodec("UTF-8")
        app.setStyleSheet(style_stream.readAll())
        style_file.close()
        print("Стили успешно загружены из style.css")
    else:
        # Стандартные стили по руководству
        app.setStyleSheet("""
            QWidget {
                font-family: "Times New Roman";
                font-size: 12pt;
                background-color: #FFFFFF;
            }
            QPushButton {
                background-color: #00FA9A;
                color: #000000;
                border: 1px solid #000000;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7FFF00;
            }
            QPushButton:pressed {
                background-color: #2E8B57;
                color: #FFFFFF;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #000000;
                border-radius: 4px;
                padding: 6px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 2px solid #00FA9A;
            }
        """)
        print("Используются стандартные стили")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Устанавливаем шрифт Times New Roman
    font = QFont("Times New Roman", 10)
    app.setFont(font)
    
    # Устанавливаем иконку приложения из Icon.ico
    if os.path.exists("Icon.ico"):
        app.setWindowIcon(QIcon("Icon.ico"))
        print("Иконка приложения загружена из Icon.ico")
    elif os.path.exists("logo.png"):
        app.setWindowIcon(QIcon("logo.png"))
        print("Иконка приложения загружена из logo.png")
    
    # Загружаем стили
    load_styles(app)
    
    from auth_window import AuthWindow
    window = AuthWindow()
    window.show()
    sys.exit(app.exec_())