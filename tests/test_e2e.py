import pytest
import requests
import time

CATALOG_URL = "http://127.0.0.1:5015"
CART_URL = "http://127.0.0.1:5002"
ORDER_URL = "http://127.0.0.1:8080" 
NO_PROXY = {"http": None, "https": None}

def test_e2e_order_placement_saga_lifecycle():
    print("\n--- СТАРТ E2E СЦЕНАРИЯ ---")
    
    cat_res = requests.get(f"{CATALOG_URL}/products", proxies=NO_PROXY)
    assert cat_res.status_code == 200
    products = cat_res.json()
    
    test_product = products[0]
    product_id = test_product["id"]
    initial_stock = test_product["stock"]
    print(f"[E2E] Шаг 1: Выбран товар '{test_product['name']}' (ID: {product_id}). Остаток на складе: {initial_stock}")
    
    user_id = 100
    cart_payload = {
        "user_id": user_id,
        "product_id": product_id,
        "quantity": 1
    }
    cart_res = requests.post(f"{CART_URL}/cart/add", json=cart_payload, proxies=NO_PROXY)
    assert cart_res.status_code in [200, 201], f"Корзина вернула код {cart_res.status_code}"
    print(f"[E2E] Шаг 2: Товар успешно добавлен в корзину через /cart/add для пользователя {user_id}")

    order_payload = {
        "user_id": user_id,
        "items": [{"product_id": product_id, "quantity": 1}]
    }
    order_res = requests.post(f"{ORDER_URL}/orders/create", json=order_payload, proxies=NO_PROXY)
    assert order_res.status_code == 201
    
    order_data = order_res.json()
    order_id = order_data["order_id"]
    print(f"[E2E] Шаг 3: Заказ создан через /orders/create! ID: {order_id}. Статус: {order_data['status']}")

    print("[E2E] Ожидание асинхронной обработки транзакции оркестратором Саги через RabbitMQ...")
    time.sleep(3)

    final_cat_res = requests.get(f"{CATALOG_URL}/products", proxies=NO_PROXY)
    final_products = final_cat_res.json()
    updated_product = next(p for p in final_products if p["id"] == product_id)
    
    print(f"[E2E] Шаг 4: Проверка склада. Было: {initial_stock}, стало: {updated_product['stock']}")
    
    assert updated_product["stock"] == initial_stock - 1
    print("--- E2E ТЕСТ УСПЕШНО ЗАВЕРШЕН (ВСЯ СИСТЕМА СИНХРОНИЗИРОВАНА) ---")