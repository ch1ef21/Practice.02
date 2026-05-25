import pytest
import requests
import time

CATALOG_URL = "http://127.0.0.1:5015"
CART_URL = "http://127.0.0.1:5002"
ORDER_URL = "http://127.0.0.1:8080"
NO_PROXY = {"http": None, "https": None}

def test_integration_performance_benchmark():
    print("\n\n=== СТАРТ ЗАМЕРА ПРОИЗВОДИТЕЛЬНОСТИ ИНТЕГРАЦИИ ===")

    t0 = time.perf_counter()
    cat_res1 = requests.get(f"{CATALOG_URL}/products", proxies=NO_PROXY)
    t1 = time.perf_counter()
    catalog_latency_cold = (t1 - t0) * 1000
    assert cat_res1.status_code == 200
    
    product_id = cat_res1.json()[0]["id"]
    

    t_start = time.perf_counter()
    cat_res2 = requests.get(f"{CATALOG_URL}/products", proxies=NO_PROXY)
    t_end = time.perf_counter()
    catalog_latency_hot = (t_end - t_start) * 1000
    assert cat_res2.status_code == 200
    
    cart_payload = {"user_id": 100, "product_id": product_id, "quantity": 1}
    t2 = time.perf_counter()
    cart_res = requests.post(f"{CART_URL}/cart/add", json=cart_payload, proxies=NO_PROXY)
    t3 = time.perf_counter()
    cart_latency = (t3 - t2) * 1000
    assert cart_res.status_code in [200, 201]

    order_payload = {"user_id": 100, "items": [{"product_id": product_id, "quantity": 1}]}
    t4 = time.perf_counter()
    order_res = requests.post(f"{ORDER_URL}/orders/create", json=order_payload, proxies=NO_PROXY)
    t5 = time.perf_counter()
    order_latency = (t5 - t4) * 1000
    assert order_res.status_code == 201

    print(f"\n[BENCHMARK] Результаты замера времени отклика (Latency):")
    print(f"  - Catalog (1-й запрос, Холодный):  {catalog_latency_cold:.2f} ms (Идёт в БД)")
    print(f"  - Catalog (2-й запрос, Горячий):   {catalog_latency_hot:.2f} ms (Идёт в КЭШ 🚀)")
    print(f"  - Cart Service    (POST /cart/add): {cart_latency:.2f} ms")
    print(f"  - Order Service   (POST /orders):   {order_latency:.2f} ms")
    print(f"  - Суммарное время синхронной фазы:  {catalog_latency_hot + cart_latency + order_latency:.2f} ms")
    print("==================================================\n")