import psycopg2
from psycopg2.extras import RealDictCursor
import os

class ProductRepository:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/microservices_db")

    def _get_connection(self):
        return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)

    def get_all(self):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, price, stock FROM products;")
                return cur.fetchall()

    def get_by_id(self, product_id):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, price, stock FROM products WHERE id = %s;", (product_id,))
                return cur.fetchone()

    def reduce_stock(self, product_id, quantity):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE products 
                    SET stock = stock - %s 
                    WHERE id = %s AND stock >= %s;
                """, (quantity, product_id, quantity))
                conn.commit()