import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import sys
import os

# Přidání cesty k aktuální složce, aby Python našel naše moduly
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
        self.root.geometry("1000x700")  # Zvětšeno okno, aby se tam vše vešlo

        # 1. Připojení k databázi
        try:
            self.db = Database()
            self.db.connect()

            # Inicializace DAO tříd
            self.product_dao = ProductDAO(self.db)
            self.order_dao = OrderDAO(self.db)
            self.report_dao = ReportDAO(self.db)

        except Exception as e:
            messagebox.showerror("Kritická chyba", f"Chyba při startu aplikace:\n{e}")
            self.root.destroy()
            return

        # 2. Vytvoření záložek (Tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')

        # Vytvoření rámců pro jednotlivé záložky
        self.tab_order = ttk.Frame(self.notebook)
        self.tab_manage = ttk.Frame(self.notebook)  # <--- NOVÁ ZÁLOŽKA (CRUD)
        self.tab_report = ttk.Frame(self.notebook)
        self.tab_import = ttk.Frame(self.notebook)

        # Přidání záložek do notebooku
        self.notebook.add(self.tab_order, text='Nová Objednávka')
        self.notebook.add(self.tab_manage, text='Správa Objednávek')
        self.notebook.add(self.tab_report, text='Statistiky')
        self.notebook.add(self.tab_import, text='Import')

        # 3. Spuštění nastavení pro jednotlivé záložky
        self.setup_order_ui()
        self.setup_manage_ui()  # <--- Spuštění nové sekce
        self.setup_report_ui()
        self.setup_import_ui()

    # =================================================================
    # ZÁLOŽKA 1: NOVÁ OBJEDNÁVKA (Transakce)
    # =================================================================
    def setup_order_ui(self):
        """
        Vytvoří UI pro vytváření nových objednávek.
        """
        frame = tk.Frame(self.tab_order, padx=10, pady=10)
        frame.pack(fill='both', expand=True)

        # Výběr produktu
        lbl_prod = tk.Label(frame, text="Výběr produktu:")
        lbl_prod.pack(anchor="w")

        self.cb_products = ttk.Combobox(frame, state="readonly", width=50)
        self.cb_products.pack(anchor="w", pady=5)

        # Načtení dat
        self.reload_products()

        # Množství
        lbl_qty = tk.Label(frame, text="Množství:")
        lbl_qty.pack(anchor="w")

        self.spin_qty = tk.Spinbox(frame, from_=1, to=100, width=5)
        self.spin_qty.pack(anchor="w", pady=5)

        # Tlačítko přidat
        btn_add = tk.Button(frame, text="Přidat do košíku", command=self.add_to_cart)
        btn_add.pack(anchor="w", pady=10)

        # Košík (Listbox)
        lbl_cart = tk.Label(frame, text="Obsah košíku:")
        lbl_cart.pack(anchor="w")

        self.list_cart = tk.Listbox(frame, height=10)
        self.list_cart.pack(fill='x', pady=5)

        self.cart = []  # Seznam položek v paměti

        # Tlačítko Odeslat
        btn_send = tk.Button(frame, text="DOKONČIT OBJEDNÁVKU (Transakce)",
                             bg="green", fg="white", command=self.submit_order)
        btn_send.pack(fill='x', pady=20)

    def reload_products(self):
        """
        Načte produkty z DB do rozbalovacího seznamu.
        """
        try:
            products = self.product_dao.get_all_active()
            self.products_map = {}
            values = []

            for p in products:
                # Pozor: Ve VIEW se sloupec jmenuje product_name
                label = f"{p['product_name']} ({p['price']} Kč)"
                self.products_map[label] = p
                values.append(label)

            self.cb_products['values'] = values
        except Exception as e:
            messagebox.showerror("Chyba DB", str(e))

    def add_to_cart(self):
        """
        Přidá vybranou položku do dočasného seznamu (košíku).
        """
        text = self.cb_products.get()
        if text == "":
            return

        product_data = self.products_map[text]
        qty = int(self.spin_qty.get())

        item = {}
        item['id'] = product_data['product_id']
        item['name'] = product_data['product_name']
        item['price'] = product_data['price']
        item['qty'] = qty

        self.cart.append(item)

        total = item['price'] * qty
        display = f"{item['name']} - {qty} ks (Celkem: {total} Kč)"
        self.list_cart.insert(tk.END, display)

    def submit_order(self):
        """
        Odešle košík do DAO pro vytvoření transakce.
        """
        if not self.cart:
            messagebox.showwarning("Pozor", "Košík je prázdný!")
            return

        try:
            # Pevně dané ID uživatele (simulace přihlášení)
            user_id = 2
            order_id = self.order_dao.create_order(user_id, self.cart)

            messagebox.showinfo("Hotovo", f"Objednávka č. {order_id} byla uložena.")

            # Reset formuláře
            self.cart = []
            self.list_cart.delete(0, tk.END)

            # Aktualizace ostatních záložek
            self.show_report()
            self.load_orders()

        except Exception as e:
            messagebox.showerror("Chyba", f"Objednávka selhala:\n{e}")

    # =================================================================
    # ZÁLOŽKA 2: SPRÁVA OBJEDNÁVEK (CRUD Operace)
    # =================================================================
    def setup_manage_ui(self):
        """
        Vytvoří UI pro správu: Seznam objednávek, Detail, Mazání, Úprava stavu.
        """
        # A) Horní část - Seznam objednávek
        frame_top = tk.LabelFrame(self.tab_manage, text="Seznam Objednávek")
        frame_top.pack(fill='both', expand=True, padx=5, pady=5)

        cols = ("ID", "Zákazník", "Datum", "Stav")
        self.tree_orders = ttk.Treeview(frame_top, columns=cols, show='headings', height=8)

        for col in cols:
            self.tree_orders.heading(col, text=col)
            self.tree_orders.column(col, width=100)

        self.tree_orders.pack(side=tk.LEFT, fill='both', expand=True)

        # Scrollbar pro seznam
        sb = tk.Scrollbar(frame_top, orient=tk.VERTICAL, command=self.tree_orders.yview)
        sb.pack(side=tk.RIGHT, fill='y')
        self.tree_orders.configure(yscrollcommand=sb.set)

        # Událost: Po kliknutí na řádek načti detail
        self.tree_orders.bind("<<TreeviewSelect>>", self.on_order_select)

        # Ovládací tlačítka
        frame_actions = tk.Frame(self.tab_manage)
        frame_actions.pack(fill='x', padx=5, pady=5)

        btn_refresh = tk.Button(frame_actions, text="Obnovit seznam", command=self.load_orders)
        btn_refresh.pack(side=tk.LEFT, padx=5)

        btn_ship = tk.Button(frame_actions, text="Nastavit 'Odesláno' (Update)", command=self.mark_as_shipped)
        btn_ship.pack(side=tk.LEFT, padx=5)

        btn_del = tk.Button(frame_actions, text="Smazat objednávku (Delete)", bg="#ffcccc", command=self.delete_order)
        btn_del.pack(side=tk.RIGHT, padx=5)

        # B) Dolní část - Detail položek
        frame_bottom = tk.LabelFrame(self.tab_manage, text="Položky vybrané objednávky (Detail)")
        frame_bottom.pack(fill='both', expand=True, padx=5, pady=5)

        cols_items = ("Produkt", "Množství", "Cena/ks")
        self.tree_items = ttk.Treeview(frame_bottom, columns=cols_items, show='headings', height=5)

        for col in cols_items:
            self.tree_items.heading(col, text=col)

        self.tree_items.pack(fill='both', expand=True)

        # Načíst data při startu
        self.load_orders()

    def load_orders(self):
        """Načte seznam všech objednávek do horní tabulky."""
        for row in self.tree_orders.get_children():
            self.tree_orders.delete(row)

        try:
            orders = self.order_dao.get_all_orders()
            for o in orders:
                vals = (o['id'], o['username'], o['created_at'], o['status'])
                self.tree_orders.insert("", tk.END, values=vals)
        except Exception as e:
            print(f"Chyba načítání objednávek: {e}")

    def on_order_select(self, event):
        """Po kliknutí na objednávku načte její položky do dolní tabulky."""
        selected_item = self.tree_orders.selection()
        if not selected_item:
            return

        # Získáme ID z vybraného řádku
        item_data = self.tree_orders.item(selected_item)
        order_id = item_data['values'][0]

        # Vyčistit dolní tabulku
        for row in self.tree_items.get_children():
            self.tree_items.delete(row)

        try:
            items = self.order_dao.get_order_items(order_id)
            for i in items:
                self.tree_items.insert("", tk.END, values=(i['name'], i['quantity'], i['unit_price']))
        except Exception as e:
            print(f"Chyba detailu: {e}")

    def mark_as_shipped(self):
        """Změní stav vybrané objednávky (Update)."""
        selected = self.tree_orders.selection()
        if not selected:
            messagebox.showwarning("Pozor", "Vyberte objednávku.")
            return

        order_id = self.tree_orders.item(selected)['values'][0]

        try:
            self.order_dao.update_status(order_id, 'shipped')
            messagebox.showinfo("Hotovo", "Stav objednávky byl změněn.")
            self.load_orders()
        except Exception as e:
            messagebox.showerror("Chyba", str(e))

    def delete_order(self):
        """Smaže vybranou objednávku a její položky (Delete)."""
        selected = self.tree_orders.selection()
        if not selected:
            messagebox.showwarning("Pozor", "Vyberte objednávku.")
            return

        if not messagebox.askyesno("Smazat", "Opravdu smazat tuto objednávku?"):
            return

        order_id = self.tree_orders.item(selected)['values'][0]

        try:
            self.order_dao.delete_order(order_id)
            messagebox.showinfo("Hotovo", "Objednávka smazána.")
            self.load_orders()
            # Vymazat i detail, protože objednávka už neexistuje
            for row in self.tree_items.get_children():
                self.tree_items.delete(row)
        except Exception as e:
            messagebox.showerror("Chyba", str(e))

    # =================================================================
    # ZÁLOŽKA 3: STATISTIKY (Reporty)
    # =================================================================
    def setup_report_ui(self):
        """
        Vytvoří UI pro zobrazení agregovaných statistik.
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
        Načte data z VIEW v databázi a zobrazí je.
        """
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            data = self.report_dao.get_stats()
            for row in data:
                vals = (row['category_name'], row['items_sold'], row['total_revenue'])
                self.tree.insert("", tk.END, values=vals)
        except Exception as e:
            print(f"Chyba reportu: {e}")

    # =================================================================
    # ZÁLOŽKA 4: IMPORT DAT
    # =================================================================
    def setup_import_ui(self):
        """
        Vytvoří UI pro nahrávání JSON souborů.
        """
        frame = tk.Frame(self.tab_import, padx=20, pady=20)
        frame.pack(fill='both', expand=True)

        lbl = tk.Label(frame, text="Import produktů z JSON", font="Arial 14")
        lbl.pack(pady=10)

        btn = tk.Button(frame, text="Vybrat soubor...", command=self.run_import, width=20, height=2)
        btn.pack()

    def run_import(self):
        """
        Spustí import produktů ze souboru.
        """
        file_path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data_list = json.load(f)

            count = 0

            for item in data_list:
                if 'name' not in item or 'price' not in item:
                    continue

                name = item['name']
                price = item['price']
                cat_id = item.get('category_id', 1)

                self.product_dao.import_product(name, price, cat_id)
                count += 1

            messagebox.showinfo("Info", f"Importováno {count} produktů.")
            self.reload_products()

        except ValueError:
            messagebox.showerror("Chyba", "Soubor není platný JSON.")
        except Exception as e:
            messagebox.showerror("Chyba importu", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = EshopApp(root)
    root.mainloop()