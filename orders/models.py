import psycopg2
from psycopg2.extras import RealDictCursor
import os

class OrderRepository:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/microservices_db")

    def _get_connection(self):
        return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)

    def add(self, order_id, user_id, status='Created'):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO orders (id, user_id, status) VALUES (%s, %s, %s);",
                    (order_id, user_id, status)
                )
            conn.commit()

    def get_by_id(self, order_id):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, user_id, status, created_at FROM orders WHERE id = %s;", (order_id,))
                return cur.fetchone()