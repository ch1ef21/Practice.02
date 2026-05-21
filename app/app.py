import sys
from flask import Flask, jsonify, request
from models import ProductRepository
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
db_set_products = ProductRepository()

def init_defaults():
    try:
        with db_set_products._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM products;")
                count = cur.fetchone()['count']
                
                if count == 0:
                    cur.execute("""
                        INSERT INTO products (name, price, stock) VALUES 
                        ('Smartphone', 499.99, 10),
                        ('Laptop', 1199.50, 5),
                        ('Graphics Card GTX 1070', 250.00, 2);
                    """)
                    conn.commit()
                    print("БАЗА БЫЛА ПУСТА: Созданы 3 базовых товара со складом!", flush=True)
                else:
                    cur.execute("""
                        SELECT COLUMN_NAME 
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME = 'products' AND COLUMN_NAME = 'stock';
                    """)
                    column_exists = cur.fetchone()
                    
                    if not column_exists:
                        print("Авто-миграция: Колонка 'stock' не найдена. Добавляю...", flush=True)
                        cur.execute("ALTER TABLE products ADD COLUMN stock INTEGER NOT NULL DEFAULT 10;")
                        cur.execute("UPDATE products SET stock = 5 WHERE name = 'Laptop';")
                        cur.execute("UPDATE products SET stock = 2 WHERE name = 'Graphics Card GTX 1070';")
                        conn.commit()
                        print("База успешно обновлена!", flush=True)
                    else:
                        print(f"В базе уже есть товары ({count}) и колонка stock на месте.", flush=True)
    except Exception as e:
        print(f"Ошибка инициализации базы данных: {e}", file=sys.stderr, flush=True)

@app.route('/products', methods=['GET'])
def get_products():
    products = db_set_products.get_all()
    return jsonify(products), 200

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = db_set_products.get_by_id(product_id)
    if product is None:
        return jsonify({'error': 'Товар не найден'}), 404
    return jsonify(product), 200

@app.route('/products/<int:product_id>/check-stock', methods=['POST'])
def check_stock(product_id):
    product = db_set_products.get_by_id(product_id)
    if product is None:
        return jsonify({'error': 'Товар не найден в каталоге'}), 404
        
    data = request.get_json() or {}
    requested_quantity = data.get('quantity', 1)
    
    if product['stock'] < requested_quantity:
        return jsonify({
            'error': 'Недостаточно товара на складе',
            'available': product['stock'],
            'requested': requested_quantity
        }), 400
        
    return jsonify({
        'status': 'Доступно',
        'product_id': product_id,
        'current_stock': product['stock']
    }), 200

if __name__ == '__main__':
    init_defaults()
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5001)