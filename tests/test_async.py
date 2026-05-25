import pytest
import requests
import time

CART_URL = "http://127.0.0.1:5002"
ORDER_URL = "http://127.0.0.1:8080" 
NO_PROXY = {"http": None, "https": None}

def test_async_checkout_integration():
    print("\n\n=== СТАРТ ТЕСТИРОВАНИЯ АСИНХРОННОЙ ИНТЕГРАЦИИ ===")
    
    user_id = "777"
    product_id = 1
    
    add_payload = {"user_id": user_id, "product_id": product_id, "quantity": 1}
    add_res = requests.post(f"{CART_URL}/cart/add", json=add_payload, proxies=NO_PROXY)
    assert add_res.status_code == 200
    print(" [Тест] Товар успешно добавлен в корзину.")

    checkout_payload = {"user_id": user_id}
    t_start = time.perf_counter()
    
    checkout_res = requests.post(f"{CART_URL}/cart/checkout", json=checkout_payload, proxies=NO_PROXY)
    
    t_end = time.perf_counter()
    latency = (t_end - t_start) * 1000

    assert checkout_res.status_code == 202
    assert checkout_res.json()["status"] == "accepted"
    print(f" [Тест] Корзина успешно приняла заказ за {latency:.2f} ms и бросила в RabbitMQ.")

    print(" [Тест] Ожидаем асинхронную обработку заказа воркером...")
    
    order_created = False
    for attempt in range(5): 
        time.sleep(1)
        
        try:
            order_check_res = requests.get(f"{ORDER_URL}/orders/user/{user_id}", proxies=NO_PROXY)
            if order_check_res.status_code == 200 and len(order_check_res.json()) > 0:
                print(f" [Тест] Успех! Заказ обнаружен в БД на попытке {attempt + 1}.")
                order_created = True
                break
        except Exception:
            pass
            
   
    print("=== ТЕСТ АСИНХРОННОЙ ИНТЕГРАЦИИ ЗАВЕРШЕН ===\n")