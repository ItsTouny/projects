from projekt_databaze.src.models import Product

class ProductDAO:
    """
    Data Access Object pro entitu Produkt.
    Zajišťuje komunikaci s tabulkou 'products' a pohledem 'v_active_catalog'.
    """

    def __init__(self, db):
        self.db = db

    def get_all_active(self):
        """
        Vrátí seznam všech aktivních produktů převedený na objekty Product.
        """
        conn = self.db.get_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM v_active_catalog")
        rows = cursor.fetchall()
        cursor.close()

        products = []
        for row in rows:
            p = Product(row['product_id'], row['product_name'], row['price'])
            products.append(p)
        return products

    def create_product(self, name, price, category_id=1):
        """
        Vloží nový produkt do databáze (využito při importu).
        """
        conn = self.db.get_conn()
        cursor = conn.cursor()
        try:
            sql = "INSERT INTO products (name, price, is_active, category_id) VALUES (%s, %s, 1, %s)"
            cursor.execute(sql, (name, price, category_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()