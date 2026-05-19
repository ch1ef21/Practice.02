import psycopg2
from psycopg2.extras import ReadlDictCursor
import os

class ProductRepository:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/microservices_db')
    
    def _get_connection(self):
        return psycopg2.connect(self.db_url, cursor_factory=ReadlDictCursor)
    
    def get_all(self):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, price, stock FROM products")
                return cur.fetchall()
            
    def get_by_id(self, product_id):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, price FROM products WHERE id = %s", (product_id,))
                return cur.fetchone()