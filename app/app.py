import sys
import structlog
from flask import Flask, jsonify, request
from flask_cors import CORS
from models import ProductRepository
from cachetools import TTLCache

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"), 
        structlog.processors.add_log_level,          
        structlog.processors.JSONRenderer()           
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

app = Flask(__name__)
CORS(app)
db_set_products = ProductRepository()

products_cache = TTLCache(maxsize=10, ttl=60)

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
                    logger.info("Database initialized with default products", action="db_init", count=3)
                else:
                    cur.execute("""
                        SELECT COLUMN_NAME 
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME = 'products' AND COLUMN_NAME = 'stock';
                    """)
                    if not cur.fetchone():
                        logger.warn("Column 'stock' not found. Running auto-migration...", action="db_migration")
                        cur.execute("ALTER TABLE products ADD COLUMN stock INTEGER NOT NULL DEFAULT 10;")
                        cur.execute("UPDATE products SET stock = 5 WHERE name = 'Laptop';")
                        cur.execute("UPDATE products SET stock = 2 WHERE name = 'Graphics Card GTX 1070';")
                        conn.commit()
                        logger.info("Database schema updated successfully", action="db_migration_success")
                    else:
                        logger.info("Database integrity check passed", action="db_check", current_count=count)
    except Exception as e:
        logger.error("Database initialization failed", error=str(e), action="db_init_error")

@app.route('/products', methods=['GET'])
def get_products():
    if "all_products" in products_cache:
        cached_data = products_cache["all_products"]
        logger.info("Fetched all products from cache (Cache Hit)", count=len(cached_data), source="memory_cache")
        return jsonify(cached_data), 200

    products = db_set_products.get_all()
    logger.info("Fetched all products from catalog database (Cache Miss)", count=len(products), source="postgresql")
    
    products_cache["all_products"] = products
    return jsonify(products), 200

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = db_set_products.get_by_id(product_id)
    if product is None:
        logger.warn("Product not found", product_id=product_id, status_code=404)
        return jsonify({'error': 'Товар не найден'}), 404
    logger.info("Fetched single product details", product_id=product_id, name=product['name'])
    return jsonify(product), 200

@app.route('/products/<int:product_id>/check-stock', methods=['POST'])
def check_stock(product_id):
    product = db_set_products.get_by_id(product_id)
    if product is None:
        logger.warn("Stock check failed: Product not found", product_id=product_id)
        return jsonify({'error': 'Товар не найден в каталоге'}), 404
        
    data = request.get_json() or {}
    requested_quantity = data.get('quantity', 1)
    
    if product['stock'] < requested_quantity:
        logger.error(
            "Insufficient stock for order", 
            product_id=product_id, 
            product_name=product['name'],
            available=product['stock'], 
            requested=requested_quantity,
            status="REJECTED"
        )
        return jsonify({
            'error': 'Недостаточно товара на складе',
            'available': product['stock'],
            'requested': requested_quantity
        }), 400
        
    logger.info(
        "Stock check approved", 
        product_id=product_id, 
        product_name=product['name'],
        current_stock=product['stock'],
        requested=requested_quantity,
        status="APPROVED"
    )
    return jsonify({
        'status': 'Доступно',
        'product_id': product_id,
        'current_stock': product['stock']
    }), 200

if __name__ == '__main__':
    init_defaults()
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5001)