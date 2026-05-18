def map_cart_to_order(user_id, cart_items):
    transformed_items = []
    for item in cart_items:
        transformed_items.append({
            "product_id": item.get('product_id'),
            "quantity": item.get('quantity'),
            "price_at_purchase": item.get('price') 
        })

    return {
        "user_id": user_id,
        "items": transformed_items,
        "metadata": {
            "source": "web_cart",
            "version": "1.0"
        }
    }