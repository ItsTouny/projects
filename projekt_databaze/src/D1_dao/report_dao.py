class ReportDAO:
    """
    Data Access Object pro čtení reportů a statistik.
    """

    def __init__(self, db):
        self.db = db

    def get_sales_stats(self):
        """
        Získá agregovaná data o prodejích z databázového pohledu (VIEW).
        """
        conn = self.db.get_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM v_sales_report")
        data = cursor.fetchall()
        cursor.close()
        return data