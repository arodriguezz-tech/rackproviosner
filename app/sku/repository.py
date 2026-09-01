from app.core.database import app_connection
class SkuRepository:
    def list(self):
        with app_connection() as c: return [r["sku"] for r in c.execute("SELECT sku FROM sku ORDER BY sku")]
    def load(self,sku):
        with app_connection() as c: return c.execute("SELECT * FROM sku WHERE sku=?",(sku,)).fetchone(),c.execute("SELECT * FROM sku_content WHERE sku=?",(sku,)).fetchone()
    def history(self):
        with app_connection() as c: return c.execute("SELECT * FROM sku_revision ORDER BY id DESC").fetchall()
