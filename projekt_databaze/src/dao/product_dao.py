class ProductDAO:
    """
    Data Access Object (DAO) pro práci s produkty.
    Zajišťuje čtení aktivních produktů a import nových dat.
    """

    def __init__(self, db_instance):
        self.db = db_instance

    def get_all_active(self):
        """
        Získá seznam všech aktivních produktů z databáze.
        Využívá databázový pohled (VIEW) v_active_catalog.

        Returns:
            list: Seznam slovníků, kde každý slovník reprezentuje produkt.
        """
        conn = self.db.get_conn()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM v_active_catalog"
        cursor.execute(query)

        result = cursor.fetchall()
        cursor.close()
        return result

    def import_product(self, name, price, category_id):
        """
        Vloží nový produkt do databáze.

        Args:
            name (str): Název produktu.
            price (float): Cena produktu.
            category_id (int): ID kategorie.

        Raises:
            Exception: Pokud selže vložení do DB.
        """
        conn = self.db.get_conn()
        cursor = conn.cursor()

        try:
            sql = "INSERT INTO products (name, price, is_active, category_id) VALUES (%s, %s, 1, %s)"
            values = (name, price, category_id)

            cursor.execute(sql, values)
            conn.commit()

        except Exception as e:
            conn.rollback()
            raise e

        finally:
            cursor.close()