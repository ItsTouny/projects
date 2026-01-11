import mysql.connector
import json
import os


class Database:
    """
    Třída zajišťující správu připojení k databázi MySQL.
    Načítá konfiguraci a poskytuje metody pro získání spojení.
    """

    def __init__(self):
        """
        Inicializuje instanci a načte konfiguraci.
        """
        self.connection = None
        self.config = self._load_config()

    def _load_config(self):
        """
        Načte přihlašovací údaje ze souboru config.json.
        """
        current_dir = os.path.dirname(__file__)
        config_path = os.path.join(current_dir, '..', 'config', 'config.json')
        if not os.path.exists(config_path):
            raise FileNotFoundError("Chyba: Konfigurační soubor config.json nebyl nalezen.")
        with open(config_path, 'r') as f:
            return json.load(f)

    def connect(self):
        """
        Vytvoří nové připojení k databázi s nastavením autocommit.
        """
        if self.connection:
            try:
                self.connection.close()
            except:
                pass

        cfg = self.config['db']
        self.connection = mysql.connector.connect(
            host=cfg['host'],
            user=cfg['user'],
            password=cfg['password'],
            database=cfg['database'],
            autocommit=True
        )

    def get_conn(self):
        """
        Vrátí aktivní připojení. Pokud spadlo, pokusí se ho obnovit.
        """
        if self.connection is None:
            self.connect()
        elif not self.connection.is_connected():
            try:
                self.connection.reconnect(attempts=3, delay=0)
            except:
                self.connect()
        return self.connection