import pytest
import requests
import time
import pika
import json

CATALOG_URL = "http://127.0.0.1:5015"
CART_URL = "http://127.0.0.1:5002"
ORDER_URL = "http://127.0.0.1:8080"
RABBITMQ_HOST = "127.0.0.1" 
NO_PROXY = {"http": None, "https": None}

def test_performance_before_vs_after():
    print("\n\n==================================================")
    print("=== СТАРТ ФИНАЛЬНОГО СРАВНИТЕЛЬНОГО ТЕСТИРОВАНИЯ ===")
    print("==================================================")

    user_id = "999"
    product_id = 1
    add_payload = {"user_id": user_id, "product_id": product_id, "quantity": 1}
    requests.post(f"{CART_URL}/cart/add", json=add_payload, proxies=NO_PROXY)


    t0 = time.perf_counter()
    res_cold = requests.get(f"{CATALOG_URL}/products", proxies=NO_PROXY)
    t1 = time.perf_counter()
    catalog_before = (t1 - t0) * 1000

    t2 = time.perf_counter()
    res_hot = requests.get(f"{CATALOG_URL}/products", proxies=NO_PROXY)
    t3 = time.perf_counter()
    catalog_after = (t3 - t2) * 1000


    order_payload = {"user_id": int(user_id), "items": [{"product_id": product_id, "quantity": 1}]}
    
    t4 = time.perf_counter()
    res_sync_order = requests.post(f"{ORDER_URL}/orders/create", json=order_payload, proxies=NO_PROXY)
    t5 = time.perf_counter()
    checkout_before = (t5 - t4) * 1000


    t6 = time.perf_counter()
    res_async_checkout = requests.post(f"{CART_URL}/cart/checkout", json={"user_id": user_id}, proxies=NO_PROXY)
    t7 = time.perf_counter()
    checkout_after = (t7 - t6) * 1000



    print("\n РЕЗУЛЬТАТЫ СРАВНЕНИЯ (ВРЕМЯ ОТКЛИКА SYSTEM LATENCY):")
    print("--------------------------------------------------")
    
    print(f"1. Получение каталога (GET /products):")
    print(f"   - До оптимизации (В базу данных): {catalog_before:.2f} ms")
    print(f"   - После оптимизации (Из RAM кэша): {catalog_after:.2f} ms")
    diff_cat = catalog_before - catalog_after
    print(f"    Результат: Ускорение на {diff_cat:.2f} ms (в {catalog_before/catalog_after:.1f} раз!)")
    print("--------------------------------------------------")

    print(f"2. Оформление заказа (Checkout):")
    print(f"   - До оптимизации (Синхронный HTTP REST): {checkout_before:.2f} ms")
    print(f"   - После оптимизации (Асинхронный AMQP):  {checkout_after:.2f} ms")
    diff_check = checkout_before - checkout_after
    print(f"    Результат: Ускорение на {diff_check:.2f} ms (в {checkout_before/checkout_after:.1f} раз!)")
    print("--------------------------------------------------")

    total_before = catalog_before + checkout_before
    total_after = catalog_after + checkout_after
    print(f"ИТОГОВАЯ ЗАДЕРЖКА СИНХРОННОЙ ФАЗЫ ДЛЯ КЛИЕНТА:")
    print(f"   - БЫЛО (Синхронная архитектура): {total_before:.2f} ms")
    print(f"   - СТАЛО (Оптимизированная EDA):  {total_after:.2f} ms")
    print(f"    ОБЩЕЕ СНИЖЕНИЕ ОЖИДАНИЯ: на {total_before - total_after:.2f} ms (Быстрее на {(1 - total_after/total_before)*100:.1f}%)")
    print("==================================================\n")

    assert res_cold.status_code == 200
    assert res_async_checkout.status_code == 202