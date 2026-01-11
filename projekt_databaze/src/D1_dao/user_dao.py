from projekt_databaze.src.models import User


class UserDAO:
    """
    Data Access Object pro entitu Uživatel.
    Zajišťuje komunikaci s tabulkou 'users'.
    """

    def __init__(self, db):
        self.db = db

    def get_by_id(self, user_id):
        """
        Vyhledá uživatele podle ID a vrátí objekt User.
        """
        conn = self.db.get_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        row = cursor.fetchone()
        cursor.close()

        if row:
            return User(row['id'], row['username'], bool(row['is_admin']))
        return None

    def authenticate(self, username, password):
        """
        Ověří přihlašovací údaje a vrátí objekt User v případě úspěchu.
        """
        conn = self.db.get_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        row = cursor.fetchone()
        cursor.close()

        if row:
            return User(row['id'], row['username'], bool(row['is_admin']))
        return None