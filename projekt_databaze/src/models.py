class User:
    """
    Datová přepravka (Data Transfer Object) reprezentující uživatele.
    Slouží pouze k uchování dat načtených z databáze.
    """
    def __init__(self, id, username, is_admin):
        """
        Inicializuje objekt uživatele.
        """
        self.id = id
        self.username = username
        self.is_admin = is_admin

class Product:
    """
    Datová přepravka (Data Transfer Object) reprezentující produkt.
    """
    def __init__(self, id, name, price):
        """
        Inicializuje objekt produktu.
        """
        self.id = id
        self.name = name
        self.price = price

    def __str__(self):
        """
        Vrací textovou reprezentaci produktu (např. pro Combobox).
        """
        return f"{self.name} ({self.price} Kč)"