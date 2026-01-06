class ReportDAO:
    """
    Data Access Object (DAO) pro generování reportů a statistik.
    """

    def __init__(self, db_instance):
        self.db = db_instance

    def get_stats(self):
        """
        Získá agregovaná data o prodejích podle kategorií.
        Čte data z databázového pohledu v_sales_report.

        Returns:
            list: Seznam slovníků obsahující statistiky prodejů.
        """
        conn = self.db.get_conn()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM v_sales_report")

        data = cursor.fetchall()
        cursor.close()

        return data