class OrderDAO:
    """
    Data Access Object pro Objednávky.
    Řeší složité operace a transakce nad tabulkami 'orders' a 'order_items'.
    """

    def __init__(self, db):
        self.db = db

    def create_order(self, user_id, items):
        """
        Vytvoří objednávku v jedné atomické transakci.
        Vloží hlavičku objednávky a následně všechny položky.
        """
        conn = self.db.get_conn()
        cursor = conn.cursor()

        try:
            conn.autocommit = False

            cursor.execute("INSERT INTO orders (user_id, status, created_at) VALUES (%s, 'new', NOW())", (user_id,))
            order_id = cursor.lastrowid

            sql_item = "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s)"
            for item in items:
                cursor.execute(sql_item, (order_id, item['id'], item['qty'], item['price']))

            conn.commit()
            conn.autocommit = True
            return order_id

        except Exception as e:
            conn.rollback()
            try:
                conn.autocommit = True
            except:
                pass
            raise e
        finally:
            cursor.close()

    def get_all(self):
        """
        Vrátí seznam všech objednávek seřazený od nejnovějších.
        """
        conn = self.db.get_conn()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT o.id, u.username, o.created_at, o.status 
            FROM orders o JOIN users u ON o.user_id = u.id 
            ORDER BY o.created_at DESC
        """
        cursor.execute(sql)
        res = cursor.fetchall()
        cursor.close()
        return res

    def update_status(self, order_id, status):
        """
        Aktualizuje stav objednávky (např. 'paid', 'shipped').
        """
        conn = self.db.get_conn()
        cursor = conn.cursor()
        cursor.execute("UPDATE orders SET status=%s WHERE id=%s", (status, order_id))
        conn.commit()
        cursor.close()

    def delete(self, order_id):
        """
        Smaže objednávku. Položky se smažou automaticky díky kaskádě v DB.
        """
        conn = self.db.get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders WHERE id=%s", (order_id,))
        conn.commit()
        cursor.close()