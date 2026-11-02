import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from products_window import ProductsWindow
    print("✅ Успешно импортирован ProductsWindow")
    
    # Проверяем, что это класс
    print(f"✅ Тип: {type(ProductsWindow)}")
    
    # Пробуем создать экземпляр
    test_instance = ProductsWindow(None, 'Гость')
    print("✅ Успешно создан экземпляр ProductsWindow")
    
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    
    # Покажем, что есть в модуле
    try:
        import products_window
        print(f"✅ Модуль products_window загружен")
        print(f"✅ Содержимое модуля: {dir(products_window)}")
    except Exception as e2:
        print(f"❌ Не могу загрузить модуль: {e2}")
        
except Exception as e:
    print(f"❌ Другая ошибка: {e}")