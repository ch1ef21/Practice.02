import sys
from flask import Flask, jsonify
from models import ProductRepository

app = Flask(__name__)
db_set_products = ProductRepository()

def init_defaults():
    try:
        with db_set_products._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM products;")
                count = cur.fetchone()['count']
                
                if count == 0:
                    cur.execute("""
                        INSERT INTO products (name, price) VALUES 
                        ('Smartphone', 499.99),
                        ('Laptop', 1199.50),
                        ('Graphics Card GTX 1070', 250.00);
                    """)
                    conn.commit()
                    print("БАЗА БЫЛА ПУСТА: Успешно созданы 3 базовых товара!", flush=True)
                else:
                    print(f"В базе уже есть товары (количество: {count}), пропускаем инициализацию.", flush=True)
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

if __name__ == '__main__':
    init_defaults()
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5001)