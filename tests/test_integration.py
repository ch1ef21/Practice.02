import pytest
import requests

BASE_URL = "http://127.0.0.1:5015"

NO_PROXY = {"http": None, "https": None}

def test_integration_catalog_lifecycle():
    
    response = requests.get(f"{BASE_URL}/products", proxies=NO_PROXY)
    assert response.status_code == 200, f"Ожидался 200, но получен {response.status_code}"
    
    products = response.json()
    assert len(products) > 0, "Ошибка: Каталог товаров пуст в БД!"
    
    target_product = products[0]
    product_id = target_product["id"]
    initial_stock = target_product["stock"]
    
    print(f"\n[Интеграционный Тест] Проверяем товар: '{target_product['name']}' (ID: {product_id})")
    print(f"[Интеграционный Тест] Текущий остаток на складе: {initial_stock} шт.")

    check_payload = {"quantity": 1}
    check_res = requests.post(
        f"{BASE_URL}/products/{product_id}/check-stock", 
        json=check_payload, 
        proxies=NO_PROXY
    )
    assert check_res.status_code == 200
    assert check_res.json()["status"] == "Доступно"
    
    invalid_payload = {"quantity": initial_stock + 5}
    error_res = requests.post(
        f"{BASE_URL}/products/{product_id}/check-stock", 
        json=invalid_payload, 
        proxies=NO_PROXY
    )
    
    assert error_res.status_code == 400
    assert "error" in error_res.json()
    print(f"[Интеграционный Тест] Запрос на {initial_stock + 5} шт. успешно отклонен системой (Код 400).")