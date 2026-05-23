import pytest
from unittest.mock import MagicMock, patch
from app.models import ProductRepository

@pytest.fixture
def mock_repo():
    repo = ProductRepository()
    repo._get_connection = MagicMock()
    return repo

def test_get_by_id_success(mock_repo):
    mock_cursor = mock_repo._get_connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
    mock_cursor.fetchone.return_value = {
        'id': 1, 
        'name': 'Test Product', 
        'price': 100.0, 
        'stock': 5
    }

    product = mock_repo.get_by_id(1)

    assert product is not None
    assert product['id'] == 1
    assert product['name'] == 'Test Product'
    assert product['stock'] == 5
    
    assert mock_cursor.execute.called

def test_get_by_id_not_found(mock_repo):
    mock_cursor = mock_repo._get_connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
    mock_cursor.fetchone.return_value = None

    product = mock_repo.get_by_id(999)

    assert product is None

def test_reduce_stock_success(mock_repo):
    mock_cursor = mock_repo._get_connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
    
    mock_repo.reduce_stock(product_id=1, quantity=2)

    expected_sql = '\n                    UPDATE products \n                    SET stock = stock - %s \n                    WHERE id = %s AND stock >= %s;\n                '
    
    mock_cursor.execute.assert_called_with(
        expected_sql,
        (2, 1, 2) 
    )
    assert mock_repo._get_connection.return_value.__enter__.return_value.commit.called