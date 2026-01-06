import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from dao.product_dao import ProductDAO
from dao.order_dao import OrderDAO
from dao.report_dao import ReportDAO


class EshopApp:
    """
    Hlavní třída grafického rozhraní (GUI) aplikace.
    Využívá knihovnu Tkinter a propojuje uživatele s vrstvou DAO.
    """

    def __init__(self, root):
        """
        Inicializuje aplikaci, připojení k DB a grafické komponenty.
        """
        self.root = root
        self.root.title("Skladový systém (D1 - DAO Pattern)")
        self.root.geometry("900x600")

        try:
            self.db = Database()
            self.db.connect()

            self.product_dao = ProductDAO(self.db)
            self.order_dao = OrderDAO(self.db)
            self.report_dao = ReportDAO(self.db)

        except Exception as e:
            messagebox.showerror("Chyba", f"Chyba při startu aplikace:\n{e}")
            self.root.destroy()
            return

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')

        self.tab_order = ttk.Frame(self.notebook)
        self.tab_report = ttk.Frame(self.notebook)
        self.tab_import = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_order, text='Nová Objednávka')
        self.notebook.add(self.tab_report, text='Statistiky')
        self.notebook.add(self.tab_import, text='Import')

        self.setup_order_ui()
        self.setup_report_ui()
        self.setup_import_ui()

    def setup_order_ui(self):
        """
        Vytvoří uživatelské rozhraní pro záložku Objednávky.
        """
        frame = tk.Frame(self.tab_order, padx=10, pady=10)
        frame.pack(fill='both', expand=True)

        lbl_prod = tk.Label(frame, text="Výběr produktu:")
        lbl_prod.pack(anchor="w")

        self.cb_products = ttk.Combobox(frame, state="readonly", width=50)
        self.cb_products.pack(anchor="w", pady=5)

        self.reload_products()

        lbl_qty = tk.Label(frame, text="Množství:")
        lbl_qty.pack(anchor="w")

        self.spin_qty = tk.Spinbox(frame, from_=1, to=100, width=5)
        self.spin_qty.pack(anchor="w", pady=5)

        btn_add = tk.Button(frame, text="Přidat do košíku", command=self.add_to_cart)
        btn_add.pack(anchor="w", pady=10)

        lbl_cart = tk.Label(frame, text="Obsah košíku:")
        lbl_cart.pack(anchor="w")

        self.list_cart = tk.Listbox(frame, height=10)
        self.list_cart.pack(fill='x', pady=5)

        self.cart = []

        btn_send = tk.Button(frame, text="DOKONČIT OBJEDNÁVKU", bg="green", fg="white", command=self.submit_order)
        btn_send.pack(fill='x', pady=20)

    def reload_products(self):
        """
        Načte aktuální seznam produktů z databáze do výběrového pole (Combobox).
        """
        try:
            products = self.product_dao.get_all_active()
            self.products_map = {}
            values = []

            for p in products:
                label = f"{p['product_name']} ({p['price']} Kč)"
                self.products_map[label] = p
                values.append(label)

            self.cb_products['values'] = values
        except Exception as e:
            messagebox.showerror("Chyba", str(e))

    def add_to_cart(self):
        """
        Přidá vybraný produkt a množství do nákupního košíku (paměti).
        """
        text = self.cb_products.get()
        if text == "":
            return

        product_data = self.products_map[text]
        qty_str = self.spin_qty.get()
        qty = int(qty_str)

        item = {}
        item['id'] = product_data['product_id']
        item['name'] = product_data['product_name']
        item['price'] = product_data['price']
        item['qty'] = qty

        self.cart.append(item)

        total_price = item['price'] * qty
        display_text = f"{item['name']} - {qty} ks (Celkem: {total_price} Kč)"
        self.list_cart.insert(tk.END, display_text)

    def submit_order(self):
        """
        Odešle obsah košíku k uložení do databáze.
        Volá transakční metodu v OrderDAO.
        """
        if len(self.cart) == 0:
            messagebox.showwarning("Pozor", "Košík je prázdný!")
            return

        try:
            order_id = self.order_dao.create_order(2, self.cart)

            messagebox.showinfo("Hotovo", f"Objednávka č. {order_id} byla uložena.")

            self.cart = []
            self.list_cart.delete(0, tk.END)
            self.show_report()

        except Exception as e:
            messagebox.showerror("Chyba", f"Objednávka selhala:\n{e}")

    def setup_report_ui(self):
        """
        Vytvoří uživatelské rozhraní pro záložku Statistiky.
        """
        frame = tk.Frame(self.tab_report, padx=10, pady=10)
        frame.pack(fill='both', expand=True)

        btn = tk.Button(frame, text="Aktualizovat data", command=self.show_report)
        btn.pack(anchor="w", pady=5)

        cols = ("Kategorie", "Prodané kusy", "Tržba")
        self.tree = ttk.Treeview(frame, columns=cols, show='headings')

        self.tree.heading("Kategorie", text="Kategorie")
        self.tree.heading("Prodané kusy", text="Prodané kusy")
        self.tree.heading("Tržba", text="Tržba (Kč)")

        self.tree.pack(fill='both', expand=True)

    def show_report(self):
        """
        Načte agregovaná data (report) z databáze a zobrazí je v tabulce.
        """
        items = self.tree.get_children()
        for item in items:
            self.tree.delete(item)

        try:
            data = self.report_dao.get_stats()
            for row in data:
                vals = (row['category_name'], row['items_sold'], row['total_revenue'])
                self.tree.insert("", tk.END, values=vals)
        except Exception as e:
            print(f"Chyba reportu: {e}")

    def setup_import_ui(self):
        """
        Vytvoří uživatelské rozhraní pro záložku Import.
        """
        frame = tk.Frame(self.tab_import, padx=20, pady=20)
        frame.pack(fill='both', expand=True)

        lbl = tk.Label(frame, text="Import produktů z JSON", font="Arial 14")
        lbl.pack(pady=10)

        btn = tk.Button(frame, text="Vybrat soubor...", command=self.run_import, width=20, height=2)
        btn.pack()

    def run_import(self):
        """
        Spustí proces importu produktů z vybraného JSON souboru.
        """
        file_path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data_list = json.load(f)

            count = 0

            for item in data_list:
                if 'name' not in item:
                    continue
                if 'price' not in item:
                    continue

                name = item['name']
                price = item['price']

                if 'category_id' in item:
                    cat_id = item['category_id']
                else:
                    cat_id = 1

                self.product_dao.import_product(name, price, cat_id)
                count = count + 1

            messagebox.showinfo("Info", f"Importováno {count} produktů.")
            self.reload_products()

        except ValueError:
            messagebox.showerror("Chyba", "Soubor není platný JSON.")
        except Exception as e:
            messagebox.showerror("Chyba", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = EshopApp(root)
    root.mainloop()