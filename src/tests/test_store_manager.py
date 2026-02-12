"""
Tests for orders manager
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

import json
import pytest
from store_manager import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    result = client.get('/health-check')
    assert result.status_code == 200
    assert result.get_json() == {'status':'ok'}

def test_stock_flow(client):
    # 1. Créez un article (Product)
    product_data = {'name': 'Test Stock Flow', 'sku': 'SKU_TEST_FLOW', 'price': 15.50}
    response_create_product = client.post('/products', json=product_data)
    assert response_create_product.status_code == 201
    
    response_json = response_create_product.get_json()
    product_id = response_json['product_id']

    stock_data = {'product_id': product_id, 'quantity': 5}
    response_add_stock = client.post('/stocks', json=stock_data)
    assert response_add_stock.status_code == 201

    response_stock_initial = client.get(f'/stocks/{product_id}')
    assert response_stock_initial.status_code in [200, 201]
    assert response_stock_initial.get_json()['quantity'] == 5

    order_data = {
        'user_id': 1,
        'items': [{'product_id': product_id, 'quantity': 2}]
    }
    response_create_order = client.post('/orders', json=order_data)
    assert response_create_order.status_code == 201
    
    order_json = response_create_order.get_json()
    order_id = order_json.get('order_id', order_json.get('id'))

    response_stock_after_order = client.get(f'/stocks/{product_id}')
    assert response_stock_after_order.get_json()['quantity'] == 3

    response_delete_order = client.delete(f'/orders/{order_id}')
    assert response_delete_order.status_code in [200, 204]

    response_stock_restored = client.get(f'/stocks/{product_id}')
    assert response_stock_restored.get_json()['quantity'] == 5