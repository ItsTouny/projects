import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from models import User, Product
from D1_dao.user_dao import UserDAO
from D1_dao.product_dao import ProductDAO
from D1_dao.order_dao import OrderDAO
from D1_dao.report_dao import ReportDAO


class EshopApp:
    """
    Hlavní grafická aplikace (GUI) postavená na Tkinter.
    Spojuje uživatelské rozhraní s datovou vrstvou (DAO).
    """

    def __init__(self, root):
        """
        Inicializuje aplikaci, připojuje DB a spouští automatické přihlášení.
        """
        self.root = root
        self.root.title("Skladový systém (Pure DAO Architecture)")
        self.root.geometry("1000x700")

        try:
            self.db = Database()
            self.db.connect()

            self.user_dao = UserDAO(self.db)
            self.product_dao = ProductDAO(self.db)
            self.order_dao = OrderDAO(self.db)
            self.report_dao = ReportDAO(self.db)

            self.current_user = self.user_dao.get_by_id(1)
            if not self.current_user:
                self.current_user = User(1, "Admin (Fallback)", True)

            self.init_gui()

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.root.destroy()

    def init_gui(self):
        """
        Vytvoří hlavní záložky aplikace.
        """
        self.root.title(f"Sklad - Přihlášen: {self.current_user.username}")
        nb = ttk.Notebook(self.root)
        nb.pack(expand=True, fill='both')

        self.tab1 = ttk.Frame(nb)
        nb.add(self.tab1, text='Nová Objednávka')
        self.tab2 = ttk.Frame(nb)
        nb.add(self.tab2, text='Správa')
        self.tab3 = ttk.Frame(nb)
        nb.add(self.tab3, text='Statistiky')
        self.tab4 = ttk.Frame(nb)
        nb.add(self.tab4, text='Import')

        self.ui_order()
        self.ui_manage()
        self.ui_report()
        self.ui_import()

    def ui_order(self):
        """
        Vytvoří UI pro zadávání nových objednávek.
        """
        f = tk.Frame(self.tab1, padx=10, pady=10)
        f.pack(fill='both', expand=True)

        tk.Label(f, text="Produkt:").pack(anchor="w")
        self.cb_prod = ttk.Combobox(f, state="readonly", width=50)
        self.cb_prod.pack(anchor="w")
        self.reload_products()

        tk.Label(f, text="Množství:").pack(anchor="w")
        self.spin_qty = tk.Spinbox(f, from_=1, to=100)
        self.spin_qty.pack(anchor="w")

        tk.Button(f, text="Přidat", command=self.add_cart).pack(anchor="w", pady=5)
        self.lst_cart = tk.Listbox(f, height=10)
        self.lst_cart.pack(fill='x')
        self.cart = []
        tk.Button(f, text="DOKONČIT", bg="green", fg="white", command=self.submit).pack(fill='x', pady=10)

    def reload_products(self):
        """
        Načte produkty z DAO a naplní Combobox.
        """
        prods = self.product_dao.get_all_active()
        self.map_prod = {str(p): p for p in prods}
        self.cb_prod['values'] = list(self.map_prod.keys())

    def add_cart(self):
        """
        Přidá položku do dočasného košíku v paměti.
        """
        txt = self.cb_prod.get()
        if not txt: return
        p = self.map_prod[txt]
        q = int(self.spin_qty.get())
        self.cart.append({'id': p.id, 'name': p.name, 'price': p.price, 'qty': q})
        self.lst_cart.insert(tk.END, f"{p.name} x{q}")

    def submit(self):
        """
        Odešle košík do OrderDAO k vytvoření transakce.
        """
        if not self.cart: return
        try:
            self.order_dao.create_order(self.current_user.id, self.cart)
            messagebox.showinfo("OK", "Uloženo")
            self.cart = []
            self.lst_cart.delete(0, tk.END)
            self.load_orders()
            self.show_stats()
        except Exception as e:
            messagebox.showerror("Err", str(e))

    def ui_manage(self):
        """
        Vytvoří UI pro správu existujících objednávek.
        """
        f = tk.Frame(self.tab2, padx=10)
        f.pack(fill='both', expand=True)
        cols = ("ID", "User", "Date", "Status")
        self.tree = ttk.Treeview(f, columns=cols, show='headings')
        for c in cols: self.tree.heading(c, text=c)
        self.tree.pack(fill='both', expand=True)

        pnl = tk.Frame(f)
        pnl.pack(fill='x', pady=5)
        tk.Button(pnl, text="Refresh", command=self.load_orders).pack(side=tk.LEFT)
        self.cb_st = ttk.Combobox(pnl, values=["paid", "shipped", "cancelled"], width=10)
        self.cb_st.pack(side=tk.LEFT, padx=5)
        self.cb_st.current(0)
        tk.Button(pnl, text="Update Status", command=self.upd_status).pack(side=tk.LEFT)
        tk.Button(pnl, text="Smazat", bg="#fcc", command=self.del_order).pack(side=tk.RIGHT)
        self.load_orders()

    def load_orders(self):
        """
        Načte seznam objednávek z DB do tabulky.
        """
        for i in self.tree.get_children(): self.tree.delete(i)
        for o in self.order_dao.get_all():
            self.tree.insert("", tk.END, values=(o['id'], o['username'], o['created_at'], o['status']))

    def upd_status(self):
        """
        Změní stav vybrané objednávky.
        """
        sel = self.tree.selection()
        if sel:
            oid = self.tree.item(sel)['values'][0]
            self.order_dao.update_status(oid, self.cb_st.get())
            self.load_orders()

    def del_order(self):
        """
        Smaže vybranou objednávku.
        """
        sel = self.tree.selection()
        if sel:
            oid = self.tree.item(sel)['values'][0]
            self.order_dao.delete(oid)
            self.load_orders()
            self.show_stats()

    def ui_report(self):
        """
        Vytvoří UI pro zobrazení statistik.
        """
        f = tk.Frame(self.tab3)
        f.pack(fill='both')
        tk.Button(f, text="Refresh", command=self.show_stats).pack()
        self.tree_rep = ttk.Treeview(f, columns=("Kat", "Ks", "Trzba"), show='headings')
        for c in ("Kat", "Ks", "Trzba"): self.tree_rep.heading(c, text=c)
        self.tree_rep.pack(fill='both')

    def show_stats(self):
        """
        Zobrazí statistiky prodejů načtené z ReportDAO.
        """
        for i in self.tree_rep.get_children(): self.tree_rep.delete(i)
        for r in self.report_dao.get_sales_stats():
            self.tree_rep.insert("", tk.END, values=(r['category_name'], r['items_sold'], r['total_revenue']))

    def ui_import(self):
        """
        Vytvoří UI pro import JSON souborů.
        """
        f = tk.Frame(self.tab4)
        f.pack(fill='both')
        tk.Button(f, text="Import JSON", command=self.do_import).pack(pady=20)

    def do_import(self):
        """
        Provede import produktů z vybraného souboru.
        """
        fn = filedialog.askopenfilename()
        if fn:
            try:
                with open(fn) as f:
                    data = json.load(f)
                c = 0
                for i in data:
                    if 'name' in i and 'price' in i:
                        self.product_dao.create_product(i['name'], i['price'])
                        c += 1
                messagebox.showinfo("OK", f"Importováno {c}")
                self.reload_products()
            except Exception as e:
                messagebox.showerror("Err", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = EshopApp(root)
    root.mainloop()