import mysql.connector
import json
import os


class Database:
    """
    Třída zajišťující připojení k databázi MySQL.
    Načítá konfigurační údaje ze souboru config.json.
    """

    def __init__(self):
        """
        Inicializuje instanci databáze a načte konfiguraci.
        """
        self.connection = None
        self.config = self._load_config()

    def _load_config(self):
        """
        Načte nastavení databáze ze souboru config/config.json.

        Returns:
            dict: Slovník s konfiguračními daty.

        Raises:
            FileNotFoundError: Pokud soubor config.json neexistuje.
        """
        current_dir = os.path.dirname(__file__)
        config_path = os.path.join(current_dir, '..', 'config', 'config.json')

        if not os.path.exists(config_path):
            raise FileNotFoundError("Chyba: Konfigurační soubor config.json nebyl nalezen.")

        with open(config_path, 'r') as f:
            data = json.load(f)
            return data

    def connect(self):
        """
        Vytvoří nové připojení k databázi pomocí údajů z konfigurace.

        Raises:
            ConnectionError: Pokud se připojení nezdaří.
        """
        try:
            db_settings = self.config['db']
            self.connection = mysql.connector.connect(
                host=db_settings['host'],
                user=db_settings['user'],
                password=db_settings['password'],
                database=db_settings['database']
            )
        except mysql.connector.Error as err:
            raise ConnectionError(f"Chyba připojení k databázi: {err}")

    def get_conn(self):
        """
        Vrátí aktivní připojení k databázi. Pokud neexistuje, vytvoří nové.

        Returns:
            mysql.connector.connection.MySQLConnection: Objekt připojení.
        """
        if self.connection is None:
            self.connect()
        elif not self.connection.is_connected():
            self.connect()

        return self.connection