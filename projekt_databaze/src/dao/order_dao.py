import mysql.connector


class OrderDAO:
    """
    Data Access Object (DAO) pro správu objednávek.
    Implementuje transakční zpracování pro vytvoření objednávky.
    """

    def __init__(self, db_instance):
        self.db = db_instance

    def create_order(self, user_id, items):
        """
        Vytvoří kompletní objednávku v rámci jedné databázové transakce.
        Zapisuje do tabulek 'orders' a 'order_items'.

        Args:
            user_id (int): ID uživatele, který objednává.
            items (list): Seznam položek košíku (slovníky s klíči id, qty, price).

        Returns:
            int: ID nově vytvořené objednávky.

        Raises:
            Exception: Pokud transakce selže, provede se rollback.
        """
        conn = self.db.get_conn()
        cursor = conn.cursor()

        try:
            try:
                conn.rollback()
            except:
                pass

            conn.start_transaction()

            sql_order = "INSERT INTO orders (user_id, status, created_at) VALUES (%s, 'new', NOW())"
            cursor.execute(sql_order, (user_id,))

            new_order_id = cursor.lastrowid

            sql_item = "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s)"

            for item in items:
                p_id = item['id']
                qty = item['qty']
                price = item['price']

                values = (new_order_id, p_id, qty, price)
                cursor.execute(sql_item, values)

            conn.commit()
            return new_order_id

        except Exception as e:
            conn.rollback()
            raise e

        finally:
            cursor.close()