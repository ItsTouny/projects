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

    def get_all_orders(self):
        """
        Načte seznam všech objednávek včetně jména uživatele.
        Spojuje tabulky 'orders' a 'users'.
        """
        conn = self.db.get_conn()
        cursor = conn.cursor(dictionary=True)
        # Jednoduchý JOIN, abychom viděli, čí ta objednávka je
        sql = """
        SELECT o.id, u.username, o.created_at, o.status 
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.created_at DESC
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_order_items(self, order_id):
        """
        Načte detail položek pro konkrétní objednávku.
        Spojuje 'order_items' a 'products'.
        """
        conn = self.db.get_conn()
        cursor = conn.cursor(dictionary=True)
        sql = """
        SELECT p.name, oi.quantity, oi.unit_price
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = %s
        """
        cursor.execute(sql, (order_id,))
        result = cursor.fetchall()
        cursor.close()
        return result

    def update_status(self, order_id, new_status):
        """
        SPLNĚNÍ ZADÁNÍ: Úprava (Update)
        Změní stav objednávky (např. na 'paid').
        """
        conn = self.db.get_conn()
        cursor = conn.cursor()
        try:
            sql = "UPDATE orders SET status = %s WHERE id = %s"
            cursor.execute(sql, (new_status, order_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

    def delete_order(self, order_id):
        """
        SPLNĚNÍ ZADÁNÍ: Smazání (Delete) více tabulek najednou.
        Díky nastavení ON DELETE CASCADE v SQL databázi,
        smazáním řádku v 'orders' se automaticky smažou i řádky v 'order_items'.
        """
        conn = self.db.get_conn()
        cursor = conn.cursor()
        try:
            sql = "DELETE FROM orders WHERE id = %s"
            cursor.execute(sql, (order_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()