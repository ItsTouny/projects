import unittest
from unittest.mock import MagicMock
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '..', 'src')
sys.path.append(src_path)

from D1_dao.user_dao import UserDAO
from D1_dao.product_dao import ProductDAO
from D1_dao.order_dao import OrderDAO
from models import User, Product


class TestDAO(unittest.TestCase):
    """
    Sada unit testů pro ověření logiky DAO tříd.
    Testy využívají Mock objekty pro simulaci databáze.
    """

    def setUp(self):
        """
        Příprava falešné databáze před každým testem.
        """
        self.mock_db = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_cur = MagicMock()
        self.mock_db.get_conn.return_value = self.mock_conn
        self.mock_conn.cursor.return_value = self.mock_cur

    def test_user_dao_get_by_id(self):
        """
        Ověří, že UserDAO správně vrátí objekt, který vypadá jako User.
        """
        self.mock_cur.fetchone.return_value = {'id': 1, 'username': 'admin', 'is_admin': 1}
        dao = UserDAO(self.mock_db)
        u = dao.get_by_id(1)
        self.assertIsNotNone(u)
        self.assertEqual(type(u).__name__, 'User')
        self.assertEqual(u.username, 'admin')

    def test_product_dao_get_all(self):
        """
        Ověří, že ProductDAO správně převede data na objekty Product.
        """
        self.mock_cur.fetchall.return_value = [
            {'product_id': 1, 'product_name': 'X', 'price': 100}
        ]
        dao = ProductDAO(self.mock_db)
        lst = dao.get_all_active()

        self.assertEqual(len(lst), 1)
        self.assertEqual(type(lst[0]).__name__, 'Product')
        self.assertEqual(lst[0].name, 'X')
        self.assertEqual(lst[0].price, 100)

    def test_order_dao_transaction(self):
        """
        Ověří, že OrderDAO při vytváření objednávky správně potvrdí transakci (commit).
        """
        dao = OrderDAO(self.mock_db)
        self.mock_cur.lastrowid = 55
        oid = dao.create_order(1, [{'id': 1, 'qty': 1, 'price': 10}])

        self.assertEqual(oid, 55)
        self.mock_conn.commit.assert_called()


if __name__ == '__main__':
    unittest.main()