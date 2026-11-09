import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "store.db")

def init_db(db_path=DB_PATH):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        stock INTEGER NOT NULL,
        rating REAL NOT NULL,
        warranty_months INTEGER NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE orders (
        order_id TEXT PRIMARY KEY,
        customer_name TEXT NOT NULL,
        customer_email TEXT NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        total_price REAL NOT NULL,
        status TEXT NOT NULL,
        order_date TEXT NOT NULL,
        tracking_number TEXT,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    """)

    cur.execute("""
    CREATE TABLE returns (
        return_id TEXT PRIMARY KEY,
        order_id TEXT NOT NULL,
        reason TEXT NOT NULL,
        status TEXT NOT NULL,
        refund_amount REAL NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id)
    )
    """)

    # Populate Products (Thai Sea Fish & Local Seafood from CAT EAT FISH - cateatfish.co/sea/thai-fish)
    # Note: warranty_months represents Cold-Chain Freezer Shelf Life (-20°C) in months
    products = [
        ("PRD-101", "ปลากะมงพร้าว แล่เนื้อ (Giant Trevally Fillet)", "ปลากลุ่มกะมง", 320.0, 42, 4.9, 6),
        ("PRD-102", "ปลากะรังจุดฟ้า ทั้งตัว (Leopard Coral Grouper)", "กลุ่มปลาเก๋า", 590.0, 18, 4.9, 6),
        ("PRD-103", "ปลาอังเกย แล่เนื้อไร้ก้าง (Golden Snapper Fillet)", "กลุ่มปลากะพง", 350.0, 35, 4.8, 6),
        ("PRD-104", "ปลาเหลืองญี่ปุ่น แล่เนื้อก้างน้อย (สำหรับเด็ก/ผู้สูงอายุ)", "ปลาชื่อไม่คุ้นน่าลอง", 280.0, 50, 4.9, 6),
        ("PRD-105", "ปลาแชกำ แล่เนื้อเกรดซาชิมิ (Yellowspotted Trevally)", "ปลากลุ่มกะมง", 420.0, 12, 4.8, 6),
        ("PRD-106", "ปลาเก๋าดอกดำ แล่เนื้อหั่นชิ้น (Black-tipped Grouper)", "กลุ่มปลาเก๋า", 390.0, 24, 4.7, 6),
        ("PRD-107", "ปลาจ้าวสมุทร แล่เนื้อติดมันท้องสีส้ม", "ปลาชื่อไม่คุ้นน่าลอง", 360.0, 15, 4.7, 6),
        ("PRD-108", "ปลากุเลาอันดามัน ทั้งตัว (Threadfin)", "ปลาตัวเล็กและปลาผิวน้ำ", 480.0, 8, 4.9, 12),
        ("PRD-109", "ปลาอินทรีย์ หั่นแว่นสเต็ก (King Mackerel Steak)", "ปลาตัวเล็กและปลาผิวน้ำ", 340.0, 45, 4.8, 6),
        ("PRD-110", "ปลาทูอันดามัน ทั้งตัว แพคคู่ (Andaman Short Mackerel)", "ปลาตัวเล็กและปลาผิวน้ำ", 150.0, 80, 4.6, 6),
        ("PRD-111", "ปลาสากหางเหลือง/ปลาน้ำดอกไม้ แล่เนื้อ (Barracuda)", "ปลาตัวเล็กและปลาผิวน้ำ", 260.0, 30, 4.5, 6),
        ("PRD-112", "ปลาวัวกระดาษ แล่เนื้อไร้เกล็ด (Unicorn Leatherjacket)", "ปลาชื่อไม่คุ้นน่าลอง", 290.0, 22, 4.7, 6),
        ("PRD-113", "หมึกหอมอันดามัน ทั้งตัว (Soft Cuttlefish)", "หมึก-กุ้ง-ปู-หอย", 450.0, 19, 4.8, 6),
        ("PRD-114", "หอยติบพังงา แกะเนื้อสด (Rock Oyster)", "หมึก-กุ้ง-ปู-หอย", 220.0, 28, 4.7, 6),
        ("PRD-115", "เนื้อปูก้อนแกะสด บ้านน้ำเค็ม (Lump Crab Meat)", "หมึก-กุ้ง-ปู-หอย", 550.0, 14, 4.9, 6)
    ]

    cur.executemany("""
    INSERT INTO products (sku, name, category, price, stock, rating, warranty_months)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, products)

    # Populate Cold-Chain Seafood Orders
    orders = [
        ("ORD-1001", "Somchai Prasert", "somchai@email.com", 1, 2, 640.0, "delivered", "2026-10-01", "COOL-KRY-882910"),
        ("ORD-1002", "Anongporn Wongsuwan", "anongporn@email.com", 2, 1, 590.0, "delivered", "2026-10-05", "COOL-EXP-772190"),
        ("ORD-1003", "Kittipong Chaiyaphum", "kittipong@email.com", 3, 2, 700.0, "shipped", "2026-10-21", "COOL-KRY-991201"),
        ("ORD-1004", "Natdanai Siriporn", "natdanai@email.com", 4, 2, 560.0, "delivered", "2026-09-15", "COOL-EXP-551234"),
        ("ORD-1005", "Pornthip Suksan", "pornthip@email.com", 5, 1, 420.0, "delivered", "2026-10-10", "COOL-KRY-441098"),
        ("ORD-1006", "Wichai Rattanakorn", "wichai@email.com", 6, 2, 780.0, "delivered", "2026-10-12", "COOL-KRY-331872"),
        ("ORD-1007", "Sasithorn Maneewan", "sasithorn@email.com", 8, 1, 480.0, "processing", "2026-10-23", None),
        ("ORD-1008", "Chaiwat Boonsri", "chaiwat@email.com", 9, 3, 1020.0, "shipped", "2026-10-22", "COOL-EXP-662911"),
        ("ORD-1009", "Benjamaporn Thani", "benjamaporn@email.com", 15, 1, 550.0, "cancelled", "2026-10-18", None),
        ("ORD-1010", "Teerapat Kaewmanee", "teerapat@email.com", 2, 1, 590.0, "delivered", "2026-09-28", "COOL-EXP-119283"),
        ("ORD-1011", "Jirawat Narkvilai", "jirawat@email.com", 7, 1, 360.0, "returned", "2026-10-02", "COOL-KRY-661002"),
        ("ORD-1012", "Malee Sangkhum", "malee@email.com", 13, 1, 450.0, "processing", "2026-10-24", None),
        ("ORD-1013", "Siriwan Chokdee", "siriwan@email.com", 10, 4, 600.0, "delivered", "2026-10-14", "COOL-EXP-889123"),
        ("ORD-1014", "Arthit Prasertsuk", "arthit@email.com", 1, 1, 320.0, "processing", "2026-10-24", None),
        ("ORD-1015", "Kanchana Sriwichai", "kanchana@email.com", 15, 2, 1100.0, "delivered", "2026-09-10", "COOL-KRY-551982"),
        ("ORD-1016", "Thanaporn Somboon", "thanaporn@email.com", 11, 2, 520.0, "delivered", "2026-10-15", "COOL-EXP-771992"),
        ("ORD-1017", "Rungroj Jaidee", "rungroj@email.com", 14, 3, 660.0, "delivered", "2026-10-17", "COOL-KRY-112877"),
        ("ORD-1018", "Supaporn Dee", "supaporn@email.com", 12, 2, 580.0, "shipped", "2026-10-22", "COOL-EXP-992812"),
        ("ORD-1019", "Narongchai Wattana", "narongchai@email.com", 3, 2, 700.0, "delivered", "2026-10-08", "COOL-KRY-334991"),
        ("ORD-1020", "Varanya Srisuk", "varanya@email.com", 4, 1, 280.0, "delivered", "2026-10-19", "COOL-EXP-441882")
    ]

    cur.executemany("""
    INSERT INTO orders (order_id, customer_name, customer_email, product_id, quantity, total_price, status, order_date, tracking_number)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, orders)

    # Populate Returns / Cold-Chain Freshness Claims
    returns = [
        ("RET-501", "ORD-1011", "กล่องโฟมชำรุดระหว่างขนส่งทำให้ถุงสุญญากาศคลายความเย็น", "approved", 360.0, "2026-10-03"),
        ("RET-502", "ORD-1004", "จัดส่งรูปแบบเนื้อปลาสลับแพค (สั่งแล่เนื้อ ได้แบบหั่นแว่น)", "refunded", 560.0, "2026-09-16"),
        ("RET-503", "ORD-1002", "แจ้งเคลมเกินกำหนด 24 ชั่วโมงหลังรับสินค้าและนำปลาออกจากช่องแช่แข็งแล้ว", "rejected", 0.0, "2026-10-09"),
        ("RET-504", "ORD-1010", "ถุงซีลสุญญากาศมีรอยรั่วซึมจากการกระแทก", "approved", 590.0, "2026-09-29"),
        ("RET-505", "ORD-1015", "รถขนส่งควบคุมอุณหภูมิส่งล่าช้ากว่ากำหนด 1 วัน", "approved", 1100.0, "2026-09-11")
    ]

    cur.executemany("""
    INSERT INTO returns (return_id, order_id, reason, status, refund_amount, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, returns)

    conn.commit()
    conn.close()
    print(f"Database successfully seeded at {db_path} with {len(products)} products, {len(orders)} orders, and {len(returns)} returns.")

if __name__ == "__main__":
    init_db()
