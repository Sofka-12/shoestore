import psycopg2

def update_photo_paths():
    """Обновляет пути к фотографиям в базе данных"""
    conn = psycopg2.connect(
        host="localhost",
        database="shoestore",
        user="postgres",
        password="200703"
    )
    
    cursor = conn.cursor()
    
    # Для каждого товара проверяем наличие фото и обновляем путь
    for product_id in range(1, 31):  # У вас 30 товаров
        possible_paths = [
            f"{product_id}.jpg",
            f"images/{product_id}.jpg",
            f"{product_id}.png",
            f"images/{product_id}.png",
        ]
        
        photo_path = None
        for path in possible_paths:
            import os
            if os.path.exists(path):
                photo_path = path
                break
        
        if photo_path:
            print(f"Товар {product_id}: найдено фото {photo_path}")
            cursor.execute("""
                UPDATE products 
                SET photo_path = %s 
                WHERE product_id = %s
            """, (photo_path, product_id))
        else:
            print(f"Товар {product_id}: фото не найдено")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Обновление завершено!")

if __name__ == "__main__":
    update_photo_paths()